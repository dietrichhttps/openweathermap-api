import requests
import time
import logging
import sys
from datetime import datetime
import config
from database import create_tables, get_db_cursor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler('errors.log', encoding='utf-8')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def fetch_weather(city: str) -> dict:
    params = {
        'q': city,
        'appid': config.OPENWEATHERMAP_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    try:
        response = requests.get(
            config.API_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        error_logger.error(f"Timeout while fetching weather for {city}")
        raise
    except requests.exceptions.ConnectionError as e:
        error_logger.error(f"Connection error while fetching weather for {city}: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        error_logger.error(f"HTTP error while fetching weather for {city}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Request error while fetching weather for {city}: {e}")
        raise


def save_request(city: str, status: str, error_message: str = None) -> int:
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO requests (city, request_time, status, error_message)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (city, datetime.now(), status, error_message))
        return cursor.fetchone()['id']


def save_response(request_id: int, weather_data: dict):
    with get_db_cursor() as cursor:
        main_data = weather_data.get('main', {})
        wind_data = weather_data.get('wind', {})
        weather_desc = weather_data.get('weather', [{}])[0]
        
        cursor.execute("""
            INSERT INTO responses 
            (request_id, temperature, feels_like, humidity, pressure, wind_speed, description, response_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request_id,
            main_data.get('temp'),
            main_data.get('feels_like'),
            main_data.get('humidity'),
            main_data.get('pressure'),
            wind_data.get('speed'),
            weather_desc.get('description'),
            datetime.now()
        ))


def process_weather_request():
    city = config.CITY
    logger.info(f"Fetching weather for {city}...")
    
    try:
        weather_data = fetch_weather(city)
        request_id = save_request(city, 'success')
        save_response(request_id, weather_data)
        
        temp = weather_data.get('main', {}).get('temp')
        logger.info(f"Successfully saved weather data for {city}: {temp}°C")
        
    except Exception as e:
        error_msg = str(e)
        save_request(city, 'error', error_msg)
        error_logger.error(f"Failed to process weather request for {city}: {error_msg}")


def main():
    logger.info("Starting weather service...")
    logger.info(f"Request interval: {config.REQUEST_INTERVAL_MINUTES} minutes")
    logger.info(f"City: {config.CITY}")
    
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        error_logger.error(f"Failed to create tables: {e}")
        sys.exit(1)
    
    while True:
        process_weather_request()
        
        interval_seconds = config.REQUEST_INTERVAL_MINUTES * 60
        logger.info(f"Waiting {config.REQUEST_INTERVAL_MINUTES} minutes until next request...")
        time.sleep(interval_seconds)


if __name__ == '__main__':
    main()
