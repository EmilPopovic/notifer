import os
from jinja2 import Environment, FileSystemLoader

from shared.calendar_utils import EventChange

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'email'))
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render_confirmation_email(template_name: str, base_url: str, token: str):
    template = env.get_template(f'{template_name}.html')
    return template.render(base_url=base_url, token=token)


def render_notification_email(template_name: str, base_url: str, event_changes: list[EventChange], token: str):
    template = env.get_template(f'{template_name}.html')
    
    # todo add event changes to the email
    
    return template.render(base_url=base_url, token=token)


def activation_email_content(base_url: str, token: str):
    subject = 'Potvrdi svoju pretplatu'
    body = render_confirmation_email('activation', base_url, token)
    return subject, body


def deletion_email_content(base_url: str, token: str):
    subject = 'Potvrdi brisanje računa'
    body = render_confirmation_email('deletion', base_url, token)
    return subject, body


def pause_email_content(base_url: str, token: str):
    subject = 'Potvrdi pauziranje obavijesti'
    body = render_confirmation_email('pause', base_url, token)
    return subject, body


def resume_email_content(base_url: str, token: str):
    subject = 'Potvrdi uključivanje obavijesti'
    body = render_confirmation_email('resume', base_url, token)
    return subject, body


def notification_email_content(base_url: str, event_changes: list[EventChange], token: str):
    subject = 'Promjena u rasporedu'
    body = render_notification_email('notification', base_url, event_changes, token)
    return subject, body
