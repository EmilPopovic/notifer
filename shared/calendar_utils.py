import logging
import requests
from icalendar import Calendar
from requests.exceptions import RequestException
from http.client import InvalidURL
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CALENDAR_PATH = '/_download/calevent/mycal.ics'


class ChangeType(Enum):
    ADDED = 1
    REMOVED = 2
    TIME = 3
    LOCATION = 4


@dataclass
class Event:
    uid: str
    summary: str
    start: datetime
    end: datetime
    location: str | None = None


@dataclass
class EventChange:
    old: Event | None
    new: Event | None
    change_type: list[ChangeType]


def parse_calendar_url(url: str) -> dict[str, str]:
    parsed_url = urlparse(url)
    
    if parsed_url.scheme not in ['http', 'https']:
        raise InvalidURL('❌ Nije URL.')
    if not (parsed_url.netloc.endswith('fer.hr') or parsed_url.netloc.endswith('fer.unizg.hr')):
        raise InvalidURL('❌ Nije valjana domena.')
    if parsed_url.path != CALENDAR_PATH:
        raise InvalidURL('❌ Nije valjan put.')
    
    parsed_query = parse_qs(parsed_url.query)
    user = parsed_query.get('user', [''])[0]
    auth = parsed_query.get('auth', [''])[0]
    
    if user == '':
        raise InvalidURL('❌ Nije valjan korisnik.')
    if auth == '':
        raise InvalidURL('❌ Nije valjan autentikacijski token.')
    
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
    

def parse_ical_event(ical_content: str) -> list[Event]:
    events = []
    try:
        cal = Calendar.from_ical(ical_content)
        for component in cal.walk():
            if component.name == 'VEVENT':
                summary = component.get('summary')
                if summary is None or not str(summary).strip():
                    continue
                uid = str(component.get('uid'))
                summary = str(summary)
                dtstart = component.get('dtstart').dt
                dtend = component.get('dtend').dt
                location = component.get('location')
                if location is not None:
                    location = str(location)
                events.append(Event(uid=uid, summary=summary, start=dtstart, end=dtend, location=location))
    except Exception as e:
        logger.exception('Failed to parse ical events: %s', e)
    return events


def extract_base_summary(summary: str) -> str:
    if not summary:
        return ''
    return summary.split('(')[0].strip()


def compute_event_changes(old_events: list[Event], new_events: list[Event]) -> list[EventChange]:
    changes = []
    
    def get_key(event: Event) -> str:
        return extract_base_summary(event.summary)
    
    old_dict = {get_key(e): e for e in old_events}
    new_dict = {get_key(e): e for e in new_events}
    
    for key, old_event in old_dict.items():
        if key not in new_dict:
            changes.append(EventChange(old=old_event, new=None, change_type=[ChangeType.REMOVED]))
            
    for key, new_events in new_dict.items():
        if key not in old_dict:
            changes.append(EventChange(old=None, new=new_events, change_type=[ChangeType.ADDED]))
    
    for key in set(old_dict.keys()).intersection(new_dict.keys()):
        old_event = old_dict[key]
        new_event = new_dict[key]
        change_types = []
        
        if old_event.start != new_event.start or old_event.end != new_event.end:
            change_types.append(ChangeType.TIME)
            
        if old_event.location != new_event.location:
            change_types.append(ChangeType.LOCATION)
        
        if len(change_types) > 0:
            changes.append(EventChange(old=old_event, new=new_event, change_type=change_types))
            
    return changes


def compute_ical_changes(old_ical: str, new_ical: str) -> list[EventChange]:
    old_events = parse_ical_event(old_ical)
    new_events = parse_ical_event(new_ical)
    return compute_event_changes(old_events, new_events)
