# Max Efficiency

Система управления задачами с AI-генерацией и MAX Mini App интерфейсом.

## Возможности

- **AI-генерация задач** - создавайте задачи естественным языком, AI структурирует их автоматически
- **Категории и теги** - организуйте задачи по категориям с автоматическими тегами
- **Совместная работа** - добавляйте пользователей в категории для совместного управления задачами
- **Умный поиск** - быстрый поиск задач по названию и описанию
- **MAX Mini App** - удобный интерфейс прямо в мессенджере MAX
- **Календарь задач** - визуализация задач с отслеживанием прогресса

## Архитектура

Проект состоит из нескольких микросервисов:

- **core-service** - основное API на FastAPI с PostgreSQL
- **ai-service** - сервис AI-генерации задач на базе Ollama
- **bot-service** - Бот для взаимодействия с системой
- **frontend** - React приложение
- **kafka** - брокер сообщений для связи между сервисами
- **redis** - кеширование данных
- **ollama** - локальная AI модель (qwen3:1.7b)

## Требования

- Docker & Docker Compose
- 4GB+ RAM (для AI модели может понадобиться несколько больше рекомендуется 8GB)
- MAX Bot Token
- (Опционально) NVIDIA GPU для ускорения AI

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Eiztrips/max-efficiency.git
cd max-efficiency
```

### 2. Создайте .env файл

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_bot_token_here
```

### 4. Запустите все сервисы

```bash
docker compose up -d
```

Это запустит все необходимые сервисы:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Kafka (порты 9092, 9094)
- Ollama (порт 11434)
- Core Service API (порт 8000)
- Frontend (порт 3000)
- AI Service
- Bot Service

### 5. Дождитесь загрузки AI модели

При первом запуске Ollama автоматически загрузит модель `qwen3:1.7b` (около 1GB). Это может занять несколько минут.

Проверить статус:
```bash
docker logs ollama-setup
```

## Деплой

### Запуск отдельных сервисов

```bash
# Только база данных и инфраструктура
docker compose up postgres redis kafka -d

# Core service
docker compose up core-service -d --build

# AI service
docker compose up ai-service -d --build

# Frontend
docker compose up frontend -d --build

# Bot service
docker compose up bot-service -d --build
```

### Логи

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f core-service
docker compose logs -f bot-service
docker compose logs -f ai-service
```

### API документация

После запуска core-service документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Остановка сервисов

```bash
# Остановить все
docker compose down

# Остановить и удалить volumes (БД, кеш)
docker compose down -v
```

## Структура проекта

```
max-efficiency/
├── bot-service/         # MAX бот
│   ├── src/
│   │   ├── main.py
│   │   ├── settings.py
│   │   └── services/
│   └── Dockerfile
├── core-service/        # FastAPI бэкенд
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   └── Dockerfile
├── ai-service/          # AI сервис генерации задач
│   ├── main.py
│   ├── config.yaml
│   └── Dockerfile
├── frontend/            # React Mini App
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   └── Dockerfile
└── docker-compose.yml
```

## Troubleshooting

### Бот не отвечает
1. Проверьте токен в `.env`
2. Убедитесь что bot-service запущен: `docker compose ps bot-service`
3. Проверьте логи: `docker compose logs bot-service`

### AI не генерирует задачи
1. Проверьте что модель была загружена: `docker logs ollama-setup`
2. Убедитесь что ai-service подключен к kafka: `docker compose logs ai-service`

