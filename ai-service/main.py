"""
Kafka-сервис для работы с тасками с использованием локальной Ollama LLM.
Для масштабирования возможно добавление новых инстансов либо использование API.

Читает сообщения из input topic,
обрабатывает через Ollama с JSON-выводом,
отправляет результат в output topic.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional

import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from ollama import AsyncClient
from pydantic import BaseModel, Field

# Конфигурация env задается композом
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "texts_to_summarize")
OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "summaries")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "summarizer-group")
MODEL = os.getenv("SUMMARIZER_MODEL", "gemma3:4b")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("taskai")


class Task(BaseModel):
    name: str
    description: str
    tags: list[str]
    # Опционально указывается дата до которой задачу нужно сделать
    # перед отправлением в кафку пропарсить в datetime
    expiration_date: Optional[str] = None
    # Возможная зона к которой эта таска относится?
    zone: str


async def generate_task_metadata(text: str) -> Optional[Task]:
    try:
        client = AsyncClient()
        response = await client.chat(
            messages=[
                {
                    'role': 'system',
                    'content': 'Ты — эксперт по созданию и компоновке задач из текстов пользователя. На вход подается текст и нужно выдать json с данными по данной задаче и её выжимке.'
                },
                {
                    'role': 'user',
                    'content': f'Создай задачу из следующего текста:\n\n{text}'
                }
            ],
            model=MODEL,
            format=Task.model_json_schema(),
        )

        task_obj = Task.model_validate_json(response['message']['content'])
        return task_obj

    except Exception as e:
        logger.exception(f"Error calling Ollama for summarization: {e}")
        return None


class OutputMessage(BaseModel):
    input_text: str
    task: Task
    model: str
    timestamp: str


async def process_message(text: str) -> OutputMessage:
    task = await generate_task_metadata(text)

    if task is None:
        logger.warning("Failed to generate task meta, using empty string")
        task = ""

    return OutputMessage(
        input_text=text,
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
                text = msg.value
                if not text or not text.strip():
                    logger.warning(f"Empty message at offset {msg.offset}, skipping")
                    continue

                logger.info(
                    f"Processing message | partition={msg.partition} offset={msg.offset} "
                    f"size={len(text)} chars"
                )
                # NOTE: Нужно ли ограничить длину сообщения или оставить это беку/боту?
                result = await process_message(text)

                await producer.send(OUTPUT_TOPIC, value=result.model_dump())

                logger.info(
                    f"taskai sent | offset={msg.offset} task_len={len(result.summary)} chars"
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