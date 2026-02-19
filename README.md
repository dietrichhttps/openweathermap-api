# OpenWeatherMap API Integration Service

Сервис для автоматического получения данных о погоде с OpenWeatherMap API и сохранения их в PostgreSQL.

## Структура проекта

```
├── weather_service.py      # Основной скрипт сервиса получения данных о погоде
├── database.py             # Модуль работы с PostgreSQL БД
├── config.py               # Конфигурация приложения
├── requirements.txt        # Зависимости Python
├── docker-compose.yml      # Docker Compose конфигурация с сервисами
├── Dockerfile              # Docker образ для контейнеризации приложения
├── entrypoint.sh           # Скрипт входной точки для контейнера
├── .env.example            # Пример файла переменных окружения
├── .gitignore              # Файл игнорирования Git
├── errors.log              # Логи ошибок (создается при запуске)
└── README.md               # Документация проекта
```

## Структура базы данных

### Таблица `requests`
Хранит историю запросов к API:
- `id` - уникальный идентификатор запроса
- `city` - город, для которого запрашивается погода
- `request_time` - время запроса
- `status` - статус запроса (success/error)
- `error_message` - сообщение об ошибке (если есть)

### Таблица `responses`
Хранит полученные данные о погоде:
- `id` - уникальный идентификатор ответа
- `request_id` - внешний ключ на таблицу requests
- `temperature` - температура (°C)
- `feels_like` - ощущаемая температура (°C)
- `humidity` - влажность (%)
- `pressure` - давление (гПа)
- `wind_speed` - скорость ветра (м/с)
- `description` - описание погоды
- `response_time` - время получения ответа

## Развертывание

### Предварительные требования
- Docker и Docker Compose
- API ключ OpenWeatherMap (получить бесплатно: https://openweathermap.org/api)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/dietrichhttps/openweathermap-api.git
cd openweathermap-api
```

2. Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` и укажите ваш API ключ:
```
OPENWEATHERMAP_API_KEY=your_actual_api_key_here
```

4. Запустите сервис:
```bash
docker-compose up -d
```

### Локальный запуск (без Docker)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте базу данных PostgreSQL и настройте `.env`

3. Запустите сервис:
```bash
python weather_service.py
```

## SQL-запрос с JOIN

Запрос для получения истории запросов и полученных данных о погоде:

```sql
SELECT 
    r.id AS request_id,
    r.city,
    r.request_time,
    r.status,
    r.error_message,
    resp.temperature,
    resp.feels_like,
    resp.humidity,
    resp.pressure,
    resp.wind_speed,
    resp.description,
    resp.response_time
FROM requests r
LEFT JOIN responses resp ON r.id = resp.request_id
ORDER BY r.request_time DESC
LIMIT 100;
```

## Логирование ошибок

Ошибки подключения и таймауты записываются в файл `errors.log`:
- Ошибки таймаута
- Ошибки соединения
- HTTP ошибки
- Общие ошибки запросов

## Конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OPENWEATHERMAP_API_KEY` | API ключ OpenWeatherMap | - |
| `CITY` | Город для запроса погоды | Moscow |
| `REQUEST_INTERVAL_MINUTES` | Интервал запросов (минуты) | 5 |
| `DB_HOST` | Хост базы данных | localhost |
| `DB_PORT` | Порт базы данных | 5432 |
| `DB_NAME` | Имя базы данных | weather_db |
| `DB_USER` | Пользователь БД | postgres |
| `DB_PASSWORD` | Пароль БД | postgres |
