"""
Kafka-сервис для работы с тасками с использованием локальной Ollama LLM.
Для масштабирования возможно добавление новых инстансов либо использование API.

Читает сообщения из input topic,
обрабатывает через Ollama с JSON-выводом,
отправляет результат в output topic.
"""
import os
import json
import yaml
import logging
from datetime import datetime
from typing import Optional

import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from ollama import AsyncClient
from pydantic import BaseModel, Field

# Конфигурация env задается композом
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "ai-service")
OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "main-service")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "max-efficiency")
MODEL = os.getenv("SUMMARIZER_MODEL", "qwen3:1.7b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("taskai")

# Load configuration
def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CONFIG = load_config()
SYSTEM_PROMPT = CONFIG.get("PREPROMT", "")


class Task(BaseModel):
    name: str
    description: str
    tags: list[str]
    # Опционально указывается дата до которой задачу нужно сделать
    # перед отправлением в кафку пропарсить в datetime
    expiration_date: Optional[str] = None
    # Возможная зона к которой эта таска относится?
    zone: str

class InputMessage(BaseModel):
    user_id: str  # Идентификатор пользователя или таскайди сделать?
    text: str     # Основной текст задачи
    recent_tags: Optional[list[str]] = None
    recent_zones: Optional[list[str]] = None

class OutputMessage(BaseModel):
    input_text: str
    task: Task
    model: str
    timestamp: str

async def generate_task_metadata(input_msg: InputMessage) -> Optional[Task]:
    text = input_msg.text

    context_str = ""
    if input_msg.recent_tags or input_msg.recent_zones:
        context_str = f"\n\nКонтекст пользователя:\n"
        if input_msg.recent_tags:
            context_str += f"- Недавние теги: {', '.join(input_msg.recent_tags[:5])}\n"  # Лимит 5 для краткости
        if input_msg.recent_zones:
            context_str += f"- Недавние зоны: {', '.join(input_msg.recent_zones)}\n"
        context_str += "Используй это для релевантных тегов и зоны (если текст не противоречит; стремись к последовательности)."

    full_prompt = f'Создай задачу из следующего текста:{context_str}\n\n{text}'

    try:
        client = AsyncClient(host=OLLAMA_HOST)
        response = await client.chat(
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT.replace("{{current_date}}", datetime.now().strftime("%Y-%m-%d"))
                },
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ],
            model=MODEL,
            format=Task.model_json_schema(),
        )

        if response is None or response.message.content is None:
            logger.error("No response from Ollama")
            return None

        task_obj = Task.model_validate_json(response.message.content)
        return task_obj

    except Exception as e:
        logger.exception(f"Error calling Ollama for summarization: {e}")
        return None



async def process_message(input_msg: InputMessage) -> OutputMessage:
    task = await generate_task_metadata(input_msg)

    if task is None:
        logger.warning("Failed to generate task meta, using empty defaults")
        task = Task(name="", description="", tags=[], zone="")

    return OutputMessage(
        input_text=input_msg.text,
        task=task,
        model=MODEL,
        timestamp=datetime.now().isoformat()
    )


async def create_consumer() -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else v,
    )
    await consumer.start()
    return consumer


async def create_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    )
    await producer.start()
    return producer


async def main():
    logger.info(
        f"Starting taskai service | Kafka: {KAFKA_BOOTSTRAP} | "
        f"Input: {INPUT_TOPIC} | Output: {OUTPUT_TOPIC} | Model: {MODEL}"
    )

    consumer = await create_consumer()
    producer = await create_producer()

    try:
        logger.info("Service started, waiting for messages...")

        async for msg in consumer:
            try:
                raw = msg.value
                if raw is None:
                    logger.warning(f"Empty message at offset {msg.offset}, skipping")
                    continue

                if isinstance(raw, str):
                    try:
                        payload = json.loads(raw)
                    except Exception:
                        logger.warning(f"Cannot parse message JSON at offset {msg.offset}, skipping")
                        continue
                else:
                    payload = raw

                try:
                    input_msg = InputMessage.model_validate(payload)
                except Exception as ve:
                    logger.warning(f"Invalid message schema at offset {msg.offset}: {ve}")
                    continue

                logger.info(
                    f"Processing message | partition={msg.partition} offset={msg.offset} "
                    f"size={len(json.dumps(payload, ensure_ascii=False))} chars"
                )

                result = await process_message(input_msg)

                await producer.send(OUTPUT_TOPIC, value=result.model_dump())

                sent_json = result.model_dump()
                size = len(json.dumps(sent_json, ensure_ascii=False))
                logger.info(
                    f"taskai sent | offset={msg.offset} task_size={size} chars"
                )

            except Exception as e:
                logger.exception(f"Error processing message at offset {msg.offset}: {e}")

    except Exception as e:
        logger.exception(f"Fatal error in main loop: {e}")

    finally:
        logger.info("Closing connections...")
        try:
            await consumer.stop()
            await producer.stop()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

        logger.info("Service stopped")


if __name__ == "__main__":
    asyncio.run(main())