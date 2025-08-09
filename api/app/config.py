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
        '''Get value from config file with fallback to environment.'''
        if self._config_parser and self._config_parser.has_option(section, key):
            return self._config_parser.get(section, key)
        return default
    
    # App components
    @property
    def student_signup_enabled(self) -> bool:
        return self._get_config_value('components', 'student_signup', 'true').lower() == 'true'
    
    @property
    def student_pause_enabled(self) -> bool:
        return self._get_config_value('components', 'student_pause', 'true').lower() == 'true'
    
    @property
    def student_resume_enabled(self) -> bool:
        return self._get_config_value('components', 'student_resume', 'true').lower() == 'true'
    
    @property
    def student_delete_enabled(self) -> bool:
        return self._get_config_value('components', 'student_delete', 'true').lower() == 'true'
    
    @property
    def admin_api_enabled(self) -> bool:
        return self._get_config_value('components', 'admin_api', 'true').lower() == 'true'
    
    @property
    def frontend_enabled(self) -> bool:
        return self._get_config_value('components', 'frontend', 'true').lower() == 'true'
    
    @property
    def allow_query_all_enabled(self) -> bool:
        return self._get_config_value('components', 'allow_query_all', 'true').lower() == 'true'
    
    @property
    def notifer_api_token_hash(self) -> str:
        return os.getenv('NOTIFER_API_TOKEN_HASH', '')

    @property
    def recipient_domain(self) -> str:
        return self._get_config_value('api', 'recipient_domain', 'fer.hr')

    # Rate Limiting
    @property
    def global_rate_limit(self) -> int:
        return int(self._get_config_value('api', 'rate_limit') or os.getenv('GLOBAL_RATE_LIMIT', '15'))
    
    @property
    def global_rate_limit_minutes(self) -> int:
        return int(self._get_config_value('api', 'rate_limit_minutes') or os.getenv('GLOBAL_RATE_LIMIT_MINUTES', '15'))
    
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
    resend_username: str = os.getenv('RESEND_CONFIRMATION_USERNAME', '')
    
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
    smtp_username: str = os.getenv('SMTP_CONFIRMATION_USERNAME', '')
    smtp_password: str = os.getenv('SMTP_CONFIRMATION_PASSWORD', '')

    # API configuration
    api_url: str = os.getenv('API_URL', '').replace('${API_PORT}', str(os.getenv('API_PORT', '8026')))
    api_port: int = int(os.getenv('API_PORT', '8026'))

    class Config:
        env_file = '.env'
        extra = 'ignore'

@lru_cache
def get_settings() -> Settings:
    return Settings()
