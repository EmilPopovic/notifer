import smtplib
import logging
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shared.email_templates import EmailContent

logger = logging.getLogger(__name__)

class EmailSender(ABC):
    @abstractmethod
    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        return False

class SMPTEmailSender(EmailSender):
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        
        self._verify_credentials()

    def _verify_credentials(self) -> None:
        logger.info(f'Verifying SMTP credentials for {self.smtp_server}:{self.smtp_port}')
        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                server.starttls()
            
            server.login(self.username, self.password)
            server.quit()
            logger.info('SMTP credentials verified successfully')
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f'SMTP authentication failed: {e}')
            raise ValueError(f'Invalid SMTP credentials for {self.username}') from e
        except smtplib.SMTPException as e:
            logger.error(f'SMTP error during credential verification: {e}')
            raise ConnectionError(f'SMTP connection failed: {e}') from e
        except Exception as e:
            logger.error(f'Unexpected error during SMTP credential verification: {e}')
            raise ConnectionError(f'Failed to verify SMTP credentials: {e}') from e

    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        logger.info(f'Sending email via SMTP to {recipient_email}')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = content.subject
        msg['From'] = self.from_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(content.html, 'html'))

        try:
            logger.debug(f'Connecting to SMTP server {self.smtp_server}:{self.smtp_port}')
            # Port 465 uses SSL, port 587 uses STARTTLS
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.username, self.password)
            server.sendmail(self.from_email, recipient_email, msg.as_string())
            server.quit()
            logger.info(f'Email sent successfully via SMTP to {recipient_email}')
            return True
        except Exception as e:
            logger.exception(f'Failed to send email via SMTP to {recipient_email}: {e}')
            return False
