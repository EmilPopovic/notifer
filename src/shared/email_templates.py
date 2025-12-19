import os
import datetime
from jinja2 import Environment, FileSystemLoader
from shared.calendar_utils import EventChange

TRANSLATIONS = {
    'hr': {
        'weekdays': {
            'Monday': 'ponedjeljak',
            'Tuesday': 'utorak', 
            'Wednesday': 'srijeda',
            'Thursday': 'četvrtak',
            'Friday': 'petak',
            'Saturday': 'subota',
            'Sunday': 'nedjelja'
        },
        'subjects': {
            'activate': 'Potvrdi svoju pretplatu',
            'delete': 'Potvrdi brisanje računa', 
            'pause': 'Potvrdi pauziranje obavijesti',
            'resume': 'Potvrdi uključivanje obavijesti',
            'notification': 'Promjena u rasporedu'
        },
        'activate': {
            'title': 'Potvrdi akciju',
            'text': 'Klikni gumb za aktivaciju svojih obavijesti.',
            'button': 'Aktiviraj',
            'fallback': 'Ako gumb ne radi, klikni ovaj link:'
        },
        'pause': {
            'title': 'Potvrdi akciju', 
            'text': 'Zatraženo je pauziranje obavijesti. Možeš ih opet uključiti bilo kad.',
            'button': 'Pauziraj obavijesti',
            'fallback': 'Ako gumb ne radi, klikni ovaj link:'
        },
        'resume': {
            'title': 'Potvrdi akciju',
            'text': 'Zatraženo je ponovno uključivanje obavijesti. Možeš ih pauzirati bilo kad.',
            'button': 'Uključi obavijesti', 
            'fallback': 'Ako gumb ne radi, klikni ovaj link:'
        },
        'delete': {
            'title': 'Potvrdi akciju',
            'text': 'Zatraženo je brisanje računa. Ova akcija se ne može poništiti.',
            'button': 'Obriši račun',
            'fallback': 'Ako gumb ne radi, klikni ovaj link:'
        },
        'notification': {
            'title': 'Promjene u rasporedu',
            'text': 'Imaš promjene u rasporedu ({{ count }}):',
            'new_event': 'Novi događaj',
            'removed_event': 'Uklonjeni događaj', 
            'updated_event': 'Ažurirani događaj',
            'old': 'Staro:',
            'new': 'Novo:',
            'title_label': 'Naslov:',
            'start_label': 'Početak:',
            'end_label': 'Završetak:',
            'location_label': 'Lokacija:',
            'more_events': '... i još {{ count }} događaja.',
            'details_text': 'Za više detalja, posjeti svoj službeni',
            'fer_calendar': 'FER kalendar',
            'unsubscribe_text': 'Ne želiš više primati obavijesti?',
            'unsubscribe_link': 'Pauziraj ih!',
            'time_changed': 'Vrijeme promijenjeno',
            'location_changed': 'Lokacija promijenjena',
            'no_location': 'Bez lokacije',
            'minor_changes_detected': 'Ažurirani manji detalji',
            'new_time': 'Novo vrijeme',
            'new_location': 'Nova lokacija',
            'details_updated': 'Detalji događaja su ažurirani',
            'when_label': 'Vrijeme:',
        }
    },
    'en': {
        'weekdays': {
            'Monday': 'Monday',
            'Tuesday': 'Tuesday',
            'Wednesday': 'Wednesday', 
            'Thursday': 'Thursday',
            'Friday': 'Friday',
            'Saturday': 'Saturday',
            'Sunday': 'Sunday'
        },
        'subjects': {
            'activate': 'Confirm your subscription',
            'delete': 'Confirm account deletion',
            'pause': 'Confirm notifications pause',
            'resume': 'Confirm notifications resume', 
            'notification': 'Schedule change'
        },
        'activate': {
            'title': 'Confirm action',
            'text': 'Click the button to activate your notifications.',
            'button': 'Activate',
            'fallback': 'If the button doesn\'t work, click this link:'
        },
        'pause': {
            'title': 'Confirm action',
            'text': 'You\'ve requested to pause notifications. You can resume them at any time.',
            'button': 'Pause notifications',
            'fallback': 'If the button doesn\'t work, click this link:'
        },
        'resume': {
            'title': 'Confirm action',
            'text': 'You\'ve requested to resume notifications. You can pause them at any time.',
            'button': 'Resume notifications',
            'fallback': 'If the button doesn\'t work, click this link:'
        },
        'delete': {
            'title': 'Confirm action',
            'text': 'You\'ve requested to delete your account. This action cannot be undone.',
            'button': 'Delete account',
            'fallback': 'If the button doesn\'t work, click this link:'
        },
        'notification': {
            'title': 'Schedule changes',
            'text': 'You have schedule changes ({{ count }}):',
            'new_event': 'New event',
            'removed_event': 'Removed event',
            'updated_event': 'Updated event',
            'old': 'Old:',
            'new': 'New:', 
            'title_label': 'Title:',
            'start_label': 'Start:',
            'end_label': 'End:',
            'location_label': 'Location:',
            'more_events': '... and {{ count }} more events.',
            'details_text': 'For more details, visit your official',
            'fer_calendar': 'FER calendar',
            'unsubscribe_text': 'Don\'t want to receive notifications anymore?',
            'unsubscribe_link': 'Pause them!',
            'time_changed': 'Time changed',
            'location_changed': 'Location changed',
            'no_location': 'No location',
            'minor_changes_detected': 'Minor details updated',
            'new_time': 'New time',
            'new_location': 'New location',
            'details_updated': 'Event details updated',
            'when_label': 'When:',
        }
    }
}

def format_datetime(value: datetime.datetime, language: str = 'hr') -> str:
    weekday_en = value.strftime("%A")
    weekday_localized = TRANSLATIONS[language]['weekdays'].get(weekday_en, weekday_en)
    day = value.day
    month = value.month
    year = value.year
    time_str = value.strftime("%H:%M")
    return f"{weekday_localized}, {day}.{month}.{year} {time_str}"

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'email'))
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_confirmation_email(email_type: str, base_url: str, token: str, language: str = 'hr') -> str:
    template = env.get_template('confirmation.html')
    t = TRANSLATIONS[language][email_type]

    body = template.render(
        base_url=base_url,
        token=token,
        title=t['title'],
        text=t['text'],
        button_text=t['button'],
        fallback_text=t['fallback'],
        lang=language,
        endpoint=email_type
    )
    return body

def render_notification_email(template_name: str, base_url: str, event_changes: list[EventChange], token: str, language: str = 'hr'):
    template = env.get_template(f'{template_name}.html')
    t = TRANSLATIONS[language][template_name]
    
    env.filters['format_datetime'] = lambda value: format_datetime(value, language)

    body = template.render(
        event_changes=event_changes,
        count=len(event_changes),
        base_url=base_url,
        token=token,
        title=t['title'],
        text=t['text'],
        t=t,
        lang=language
    )
    return body

class EmailContent:
    def __init__(self, subject: str, plain_text: str | None = None, html: str | None = None):
        self.subject: str = subject
        self.plain_text: str = plain_text if plain_text is not None else ''
        self.html: str = html if html is not None else ''

def activation_email_content(base_url: str, token: str, language: str = 'hr') -> EmailContent:
    subject = TRANSLATIONS[language]['subjects']['activate']
    html = render_confirmation_email('activate', base_url, token, language)
    return EmailContent(subject, html=html)

def deletion_email_content(base_url: str, token: str, language: str = 'hr') -> EmailContent:
    subject = TRANSLATIONS[language]['subjects']['delete']
    html = render_confirmation_email('delete', base_url, token, language)
    return EmailContent(subject, html=html)

def pause_email_content(base_url: str, token: str, language: str = 'hr') -> EmailContent:
    subject = TRANSLATIONS[language]['subjects']['pause']
    html = render_confirmation_email('pause', base_url, token, language)
    return EmailContent(subject, html=html)

def resume_email_content(base_url: str, token: str, language: str = 'hr') -> EmailContent:
    subject = TRANSLATIONS[language]['subjects']['resume']
    html = render_confirmation_email('resume', base_url, token, language)
    return EmailContent(subject, html=html)

def notification_email_content(base_url: str, event_changes: list[EventChange], token: str, language: str = 'hr') -> EmailContent:
    subject = TRANSLATIONS[language]['subjects']['notification']
    html = render_notification_email('notification', base_url, event_changes, token, language)
    return EmailContent(subject, html=html)
