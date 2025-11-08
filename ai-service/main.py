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
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
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
        client = AsyncClient(host=OLLAMA_HOST)
        response = await client.chat(
            messages=[
                {
                    'role': 'system',
                    'content': '''
Ты — эксперт по извлечению и структурированию задач из пользовательских текстов. Твоя задача: проанализировать входной текст, выявить суть задачи и сгенерировать точные метаданные в формате строгого JSON. Вывод должен быть ВАЛИДНЫМ JSON-объектом, соответствующим следующей схеме (не добавляй лишние поля, не меняй типы):

{
  "name": "строка (краткое название задачи, 1-5 слов)",
  "description": "строка (сжатая выжимка задачи, 1-3 предложения, фокус на ключевых действиях)",
  "tags": ["массив строк (3-5 релевантных тегов, короткие, без пробелов, например: 'todo', 'urgent', 'coding')"],
  "expiration_date": "строка в формате YYYY-MM-DD ИЛИ null (только если в тексте четко указана парсибельная дата; если даты нет или она неясная/белиберда — обязательно null)",
  "zone": "строка (категория зоны: 'work', 'personal', 'tech', 'health', 'education' или 'general', если неясно)"
}

ПРАВИЛА:
- Будь точен: извлекай только из текста, не галлюцинируй детали.
- expiration_date: 
  - Четкая дата (например, "до 31 декабря 2025" или "2025-12-31") → конвертируй в YYYY-MM-DD.
  - Нет даты → null.
  - Белиберда ("завтра", "скоро", "в ближайшее время", "летом") → null. Не угадывай!
- Если текст не содержит задачи (слишком короткий, оффтопик) — все равно генерируй JSON с пустыми/дефолтными значениями, но не null для обязательных строк (используй "" для name/description/zone).
- Вывод: ТОЛЬКО JSON-объект. Без ```json, без текста, без объяснений. Если JSON сломается — моделька сломается.

ПРИМЕРЫ:

Вход: "Напомни купить молоко завтра вечером. Важно не забыть!"
Вывод: {"name": "Купить молоко", "description": "Приобрести молоко в магазине вечером завтра.", "tags": ["shopping", "urgent", "personal"], "expiration_date": null, "zone": "personal"}

Вход: "Разработать API для аутентификации пользователей до 15 марта 2026 года. Использовать JWT."
Вывод: {"name": "Разработать API аутентификации", "description": "Создать эндпоинты для регистрации/логина с JWT-токенами.", "tags": ["coding", "api", "security", "dev"], "expiration_date": "2026-03-15", "zone": "work"}

Вход: "Просто привет, как дела?"
Вывод: {"name": "", "description": "", "tags": [], "expiration_date": null, "zone": "general"}

Вход: "Сделать отчет по продажам к пятнице, но пятница какая-то неопределенная."
Вывод: {"name": "Отчет по продажам", "description": "Подготовить summary продаж за период.", "tags": ["report", "sales", "work"], "expiration_date": null, "zone": "work"}
'''
                },
                {
                    'role': 'user',
                    'content': f'Создай задачу из следующего текста:\n\n{text}'
                }
            ],
            model=MODEL,
            format=Task.model_json_schema(),
        )

        # Robust extraction: support both dict response and object-like response
        content = None
        if isinstance(response, dict):
            content = response.get("message", {}).get("content")
        else:
            # try object-style .message.content
            try:
                msg = getattr(response, "message", None)
                if msg is not None:
                    content = getattr(msg, "content", None) or str(msg)
            except Exception:
                content = None

        if not content:
            logger.warning("Empty content from Ollama response")
            return None

        task_obj = Task.model_validate_json(content)
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
        logger.warning("Failed to generate task meta, using empty defaults")
        task = Task(name="", description="", tags=[], zone="")

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
                result = await process_message(text)

                await producer.send(OUTPUT_TOPIC, value=result.model_dump())

                # compute size of sent payload for logging
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