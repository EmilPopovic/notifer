import os
from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'email'))
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_email(template_name: str, base_url: str, token: str):
    """
    Renders an email template with the given parameters.
    """
    template = env.get_template(f'{template_name}.html')
    return template.render(base_url=base_url, token=token)

def activation_email_content(base_url: str, token: str):
    subject = 'Confirm Your Subscription'
    body = render_email('activation', base_url, token)
    return subject, body

def deletion_email_content(base_url: str, token: str):
    subject = 'Confirm Account Deletion'
    body = render_email('deletion', base_url, token)
    return subject, body

def pause_email_content(base_url: str, token: str):
    subject = 'Confirm Email Pause'
    body = render_email('pause', base_url, token)
    return subject, body

def resume_email_content(base_url: str, token: str):
    subject = 'Confirm Resume Notifications'
    body = render_email('resume', base_url, token)
    return subject, body
