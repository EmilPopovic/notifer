import os
import configparser
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

from shared.email_client_factory import EmailStrategy

class Settings(BaseSettings):
    def __init__(self):
        super().__init__()
        self._config_parser = self._load_config_file()

    def _load_config_file(self) -> configparser.ConfigParser | None:
        '''Load configuration from app.conf file.'''
        config_path = Path(__file__).parent.parent.parent / 'config' / 'app.conf'
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            return config
        return None

    def _get_config_value(self, section: str, key: str, default: str = '') -> str:
        if self._config_parser and self._config_parser.has_option(section, key):
            return self._config_parser.get(section, key)
        return default

    # Worker configuration
    @property
    def worker_enabled(self) -> bool:
        return self._get_config_value('components', 'worker', 'true').lower() == 'true'

    @property
    def worker_interval(self) -> int:
        return int(self._get_config_value('worker', 'worker_interval') or os.getenv('WORKER_INTERVAL', '3600'))
    
    @property
    def max_workers(self) -> int:
        return int(self._get_config_value('worker', 'max_workers') or os.getenv('MAX_WORKERS', '10'))

    # Calendar configuration
    @property
    def base_calendar_url(self) -> str:
        return self._get_config_value('api', 'base_calendar_url') or os.getenv('BASE_CALENDAR_URL', 'https://www.fer.unizg.hr/_download/calevent/mycal.ics')

    # Database configuration
    @property
    def postgres_host(self) -> str:
        return self._get_config_value('database', 'host') or os.getenv('POSTGRES_HOST', 'postgres')
    
    @property
    def postgres_port(self) -> int:
        config_port = self._get_config_value('database', 'port')
        return int(config_port or os.getenv('POSTGRES_PORT', '5432'))
    
    @property
    def postgres_user(self) -> str:
        return self._get_config_value('database', 'user') or os.getenv('POSTGRES_USER', 'postgres')
    
    @property
    def postgres_password(self) -> str:
        return os.getenv('POSTGRES_PASSWORD', '')
    
    @property
    def postgres_db(self) -> str:
        return self._get_config_value('database', 'database') or os.getenv('POSTGRES_DB', 'postgres')
    
    @property
    def postgres_sslmode(self) -> str:
        return self._get_config_value('database', 'sslmode') or os.getenv('POSTGRES_SSLMODE', 'disable')

    # Redis configuration
    redis_url: str = os.getenv('REDIS_URL', 'redis://redis:6379/0')

    # S3 configuration
    @property
    def s3_bucket(self) -> str:
        return self._get_config_value('s3', 'bucket') or os.getenv('S3_BUCKET', 'calendar')
    
    @property
    def s3_endpoint(self) -> str:
        return self._get_config_value('s3', 'endpoint_internal') or os.getenv('S3_ENDPOINT', 'http://minio:9002')
    
    @property
    def s3_user(self) -> str:
        return self._get_config_value('s3', 'user') or os.getenv('S3_USER', 'admin')
    
    @property
    def s3_password(self) -> str:
        return os.getenv('S3_PASSWORD', '')

    # Email configuration
    @property
    def email_strategy(self) -> EmailStrategy:
        '''Get email strategy from environment variable with fallback.'''
        strategy_str = self._get_config_value('email', 'strategy') or os.getenv('EMAIL_STRATEGY', 'resend_with_fallback').lower()
        try:
            return EmailStrategy(strategy_str)
        except ValueError:
            return EmailStrategy.RESEND_WITH_FALLBACK

    resend_api_key: str = os.getenv('RESEND_API_KEY', '')
    resend_username: str = os.getenv('RESEND_UPDATE_USERNAME', '')
    
    @property
    def resend_daily_limit(self) -> int:
        return int(self._get_config_value('email', 'resend_daily_limit') or os.getenv('RESEND_DAILY_LIMIT', '95'))
    
    @property
    def resend_monthly_limit(self) -> int:
        return int(self._get_config_value('email', 'resend_monthly_limit') or os.getenv('RESEND_MONTHLY_LIMIT', '2950'))
    
    @property
    def resend_rate_limit_per_second(self) -> int:
        return int(self._get_config_value('email', 'resend_rate_limit_per_second') or os.getenv('RESEND_RATE_LIMIT_PER_SECOND', '2'))

    smtp_server: str = os.getenv('SMTP_SERVER', '')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    smtp_username: str = os.getenv('SMTP_UPDATE_USERNAME', '')
    smtp_password: str = os.getenv('SMTP_UPDATE_PASSWORD', '')

    # API configuration
    api_url: str = os.getenv('API_URL', '').replace('${API_PORT}', str(os.getenv('API_PORT', '8026')))

    class Config:
        env_file = '.env'
        extra = 'ignore'

@lru_cache
def get_settings() -> Settings:
    return Settings()
