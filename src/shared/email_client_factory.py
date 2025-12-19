from shared.email_client import EmailClient
from shared.email_sender import SMPTEmailSender

class EmailClientFactory:    
    @staticmethod
    def create_smtp_client(
            smtp_server: str,
            smtp_port: int,
            username: str,
            password: str,
            from_email: str,
            api_base_url: str,
            rate_limit_per_second: float = 2.0
    ) -> EmailClient:
        sender = SMPTEmailSender(smtp_server, smtp_port, username, password, from_email)
        return EmailClient(sender, api_base_url, rate_limit_per_second=rate_limit_per_second)
