import asyncio
import json
import logging
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("test_ai_service")

KAFKA_BOOTSTRAP = "localhost:9094"
INPUT_TOPIC = "texts_to_summarize"
OUTPUT_TOPIC = "summaries"

# Тестовые данные
TEST_MESSAGES = [
    "Купить молоко, хлеб и яйца в магазине до вечера",
    "Позвонить врачу и записаться на прием в следующий вторник в 10:00",
    "Подготовить презентацию по проекту до пятницы, включить графики и статистику",
    "Отправить отчет начальнику о проделанной работе за неделю",
    "Забронировать билеты на самолет до 15 декабря для поездки в Санкт-Петербург",
]

def send_test_messages():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: v.encode('utf-8')
        )

        logger.info(f"Sending {len(TEST_MESSAGES)} test messages to {INPUT_TOPIC}...")

        for i, message in enumerate(TEST_MESSAGES):
            future = producer.send(INPUT_TOPIC, value=message)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message {i + 1} sent | partition={record_metadata.partition} "
                f"offset={record_metadata.offset}"
            )

        producer.flush()
        producer.close()
        logger.info("All test messages sent successfully")

    except Exception as e:
        logger.error(f"Error sending messages: {e}")
        raise


def consume_results(timeout_seconds=120):
    try:
        consumer = KafkaConsumer(
            OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test-consumer-group',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            consumer_timeout_ms=timeout_seconds * 1000
        )

        logger.info(f"Reading results from {OUTPUT_TOPIC}...")
        logger.info(f"Waiting up to {timeout_seconds} seconds for results...")

        message_count = 0

        for message in consumer:
            message_count += 1
            result = message.value

            logger.info(f"\n{'=' * 80}")
            logger.info(f"Result {message_count} | partition={message.partition} offset={message.offset}")
            logger.info(f"{'=' * 80}")
            logger.info(f"Input text: {result.get('input_text', 'N/A')[:100]}...")
            logger.info(f"Model: {result.get('model', 'N/A')}")
            logger.info(f"Timestamp: {result.get('timestamp', 'N/A')}")

            task = result.get('task', {})
            logger.info(f"\nTask metadata:")
            logger.info(f"  Name: {task.get('name', 'N/A')}")
            logger.info(f"  Description: {task.get('description', 'N/A')}")
            logger.info(f"  Tags: {task.get('tags', [])}")
            logger.info(f"  Zone: {task.get('zone', 'N/A')}")
            logger.info(f"  Expiration: {task.get('expiration_date', 'N/A')}")
            logger.info(f"{'=' * 80}\n")

        consumer.close()

        if message_count == 0:
            logger.warning(f"No messages received within {timeout_seconds} seconds")
        else:
            logger.info(f"Received {message_count} results")

    except Exception as e:
        logger.error(f"Error consuming results: {e}")
        raise


def main():
    logger.info("Starting test...")

    try:
        logger.info("\nSending test messages...")
        send_test_messages()
        consume_results(timeout_seconds=120)

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()

