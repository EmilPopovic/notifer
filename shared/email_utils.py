import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from shared.token_utils import create_token
from shared.email_templates import (
    activation_email_content, 
    deletion_email_content, 
    pause_email_content, 
    resume_email_content,
)

class EmailClient:
    def __init__(
            self,
            smtp_server: str,
            smtp_port: int,
            username: str,
            password: str,
            from_email: str,
            base_url: str,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.base_url = base_url
        
    def send_email(self, recipient_email: str, subject: str, body: str):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = recipient_email
        
        msg.attach(MIMEText(body, 'html'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, recipient_email, msg.as_string())
            server.quit()
            print(f'Successfully sent email to {recipient_email}')
        except Exception as e:
            print(f'Failed to send email to {recipient_email}: {e}')

    def send_activate_confirmation_email(self, recipient_email: str):
        """
        Sends a confirmation email containing a magic link.
        The magic link will point to your /activate endpoint with a token.
        """
        # Construct the magic link URL with the token as a query parameter
        token = create_token(recipient_email, 'activate')
        subject, body = activation_email_content(self.base_url, token)
        self.send_email(recipient_email, subject, body)


    def send_delete_confirmation_email(self, recipient_email: str):
        token = create_token(recipient_email, 'delete')
        subject, body = deletion_email_content(self.base_url, token)
        self.send_email(recipient_email, subject, body)


    def send_pause_confirmation_email(self, recipient_email: str):
        """
        Sends an email to confirm pausing notifications.
        """
        token = create_token(recipient_email, 'pause')
        subject, body = pause_email_content(self.base_url, token)
        self.send_email(recipient_email, subject, body)

    def send_resume_confirmation_email(self, recipient_email: str):
        """
        Sends an email to confirm resuming notifications.
        """
        token = create_token(recipient_email, 'resume')
        subject, body = resume_email_content(self.base_url, token)
        self.send_email(recipient_email, subject, body)