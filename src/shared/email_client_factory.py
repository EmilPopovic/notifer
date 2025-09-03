'''Factory for creating email clients with different sending strategies.'''

from enum import Enum
from .email_client import EmailClient
from .email_senders import (
    ResendEmailSender,
    SMPTEmailSender,
    ResendWithSMTPFallbackSender,
)

class EmailStrategy(str, Enum):
    RESEND_ONLY = 'resend'
    SMTP_ONLY = 'smtp'
    RESEND_WITH_FALLBACK = 'resend_with_fallback'

class EmailClientFactory:
    '''Factory for creating email clients with different configurations.'''

    @staticmethod
    def create_resend_only_client(
            api_key: str, 
            from_email: str, 
            api_base_url: str,
            rate_limit_per_second: float = 2.0
    ) -> EmailClient:
        '''Create an email client that only uses Resend.'''
        sender = ResendEmailSender(api_key, from_email)
        return EmailClient(sender, api_base_url, rate_limit_per_second=rate_limit_per_second)
    
    @staticmethod
    def create_smtp_only_client(
            smtp_server: str,
            smtp_port: int,
            username: str,
            password: str,
            from_email: str,
            api_base_url: str,
            rate_limit_per_second: float = 2.0
    ) -> EmailClient:
        '''Create an email client that only uses SMTP.'''
        sender = SMPTEmailSender(smtp_server, smtp_port, username, password, from_email)
        return EmailClient(sender, api_base_url, rate_limit_per_second=rate_limit_per_second)
    
    @staticmethod
    def create_resend_with_smtp_fallback(
            resend_api_key: str,
            resend_from_email: str,
            smtp_server: str,
            smtp_port: int,
            smtp_username: str,
            smtp_password: str,
            smtp_from_email: str,
            api_base_url: str,
            daily_limit: int = 95,
            monthly_limit: int = 2950,
            rate_limit_per_second: float = 2.0
    ) -> EmailClient:
        '''Create an email client that uses Resend with SMTP fallback.'''
        resend_sender = ResendEmailSender(resend_api_key, resend_from_email)
        smtp_sender = SMPTEmailSender(smtp_server, smtp_port, smtp_username, smtp_password, smtp_from_email)
        sender = ResendWithSMTPFallbackSender(resend_sender, smtp_sender, daily_limit, monthly_limit)
        return EmailClient(sender, api_base_url, rate_limit_per_second=rate_limit_per_second)
