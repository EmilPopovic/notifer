'''Factory for creating email clients with different sending strategies.'''

from enum import Enum
from shared.email_client import EmailClient
from shared.email_senders import (
    ResendEmailSender,
    SMPTEmailSender,
    ResendWithSMTPFallbackSender,
    ResendWithUsageLimits
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
            rate_limit_per_second: int = 2
    ) -> EmailClient:
        '''Create an email client that only uses Resend.'''
        sender = ResendEmailSender(api_key, from_email, rate_limit_per_second)
        sender_config = {
            'type': 'resend_only',
            'params': {
                'api_key': api_key,
                'from_email': from_email,
                'api_base_url': api_base_url,
                'rate_limit_per_second': rate_limit_per_second
            }
        }
        return EmailClient(sender, api_base_url, sender_config=sender_config)
    
    @staticmethod
    def create_smtp_only_client(
            smtp_server: str,
            smtp_port: int,
            username: str,
            password: str,
            from_email: str,
            api_base_url: str
    ) -> EmailClient:
        '''Create an email client that only uses SMTP.'''
        sender = SMPTEmailSender(smtp_server, smtp_port, username, password, from_email)
        sender_config = {
            'type': 'smtp_only',
            'params': {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'username': username,
                'password': password,
                'from_email': from_email,
                'api_base_url': api_base_url
            }
        }
        return EmailClient(sender, api_base_url, sender_config=sender_config)
    
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
            rate_limit_per_second: int = 2
    ) -> EmailClient:
        '''Create an email client that uses Resend with SMTP fallback.'''
        resend_sender = ResendEmailSender(resend_api_key, resend_from_email, rate_limit_per_second)
        smtp_sender = SMPTEmailSender(smtp_server, smtp_port, smtp_username, smtp_password, smtp_from_email)
        usage_limits = ResendWithUsageLimits(daily_limit, monthly_limit)

        sender = ResendWithSMTPFallbackSender(resend_sender, smtp_sender, usage_limits)
        sender_config = {
            'type': 'resend_with_fallback',
            'params': {
                'resend_api_key': resend_api_key,
                'resend_from_email': resend_from_email,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'smtp_username': smtp_username,
                'smtp_password': smtp_password,
                'smtp_from_email': smtp_from_email,
                'api_base_url': api_base_url,
                'daily_limit': daily_limit,
                'monthly_limit': monthly_limit,
                'rate_limit_per_second': rate_limit_per_second
            }
        }
        return EmailClient(sender, api_base_url, sender_config=sender_config)
