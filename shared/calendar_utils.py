import requests
from icalendar import Calendar
from requests.exceptions import RequestException
from http.client import InvalidURL
from urllib.parse import urlparse, parse_qs

CALENDAR_PATH = '/_download/calevent/mycal.ics'


def parse_calendar_url(url: str) -> dict[str, str]:
    parsed_url = urlparse(url)
    
    if parsed_url.scheme != 'https':
        raise InvalidURL('Not a URL')
    if not (parsed_url.netloc.endswith('fer.hr') or parsed_url.netloc.endswith('fer.unizg.hr')):
        raise InvalidURL('Invalid domain')
    if parsed_url.path != CALENDAR_PATH:
        raise InvalidURL('Invalid path')
    
    parsed_query = parse_qs(parsed_url.query)
    user = parsed_query.get('user', [''])[0]
    auth = parsed_query.get('auth', [''])[0]
    
    if user == '':
        raise InvalidURL('Invalid user')
    if auth == '':
        raise InvalidURL('Invalid auth')
    
    return {'user': user, 'auth': auth}


def is_valid_ical(ical_string: str) -> bool:
    try:
        Calendar.from_ical(ical_string)
        return True
    except Exception as _:
        return False
    
def is_valid_ical_url(url: str) -> bool:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        ical_content = response.text
        return is_valid_ical(ical_content)
    except RequestException as _:
        return False