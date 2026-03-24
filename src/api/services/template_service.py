from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from api.exceptions import ErrorCode

class TemplateService:
    def __init__(self, templates: Jinja2Templates, api_url: str):
        self.templates = templates
        self.api_url = api_url

        self.translations = {
            'hr': {
                'confirm': {
                    'activate': {
                        'title': 'Potvrdi aktivaciju',
                        'icon': '🔔',
                        'heading': 'Aktivirati obavijesti?',
                        'description': 'Klikom na gumb aktivirat ćeš obavijesti o promjenama rasporeda.',
                        'confirm_text': 'Aktiviraj',
                        'cancel_text': 'Odustani',
                        'button_class': '',
                    },
                    'delete': {
                        'title': 'Potvrdi brisanje',
                        'icon': '🗑️',
                        'heading': 'Obrisati račun?',
                        'description': 'Klikom na gumb trajno ćeš obrisati svoju pretplatu:',
                        'confirm_text': 'Obriši',
                        'cancel_text': 'Odustani',
                        'button_class': 'button-error',
                    },
                    'pause': {
                        'title': 'Potvrdi pauziranje',
                        'icon': '⏸️',
                        'heading': 'Pauzirati obavijesti?',
                        'description': 'Klikom na gumb pauzirati ćeš obavijesti za:',
                        'confirm_text': 'Pauziraj',
                        'cancel_text': 'Odustani',
                        'button_class': '',
                    },
                    'resume': {
                        'title': 'Potvrdi uključivanje',
                        'icon': '▶️',
                        'heading': 'Uključiti obavijesti?',
                        'description': 'Klikom na gumb ponovo ćeš uključiti obavijesti za:',
                        'confirm_text': 'Uključi',
                        'cancel_text': 'Odustani',
                        'button_class': '',
                    },
                },
                'activate': {
                    'title': 'Obavijesti aktivirane!',
                    'icon': '',
                    'heading': 'Obavijesti aktivirane!',
                    'description': 'Sada si pretplaćen na obavijesti o promjenama rasporeda.',
                    'additional_message': 'Pratit ćemo tvoj kalendar i obavijestiti te kad se dogodi promjena.',
                    'button_text': 'Vrati se na NotiFER'
                },
                'delete': {
                    'title': 'Račun obrisan',
                    'icon': '',
                    'heading': 'Račun obrisan',
                    'description': 'Obrisali smo tvoj račun:',
                    'button_text': 'Vrati se na NotiFER'
                },
                'pause': {
                    'title': 'Obavijesti pauzirane',
                    'icon': '',
                    'heading': 'Obavijesti pauzirane',
                    'description': 'Više nećemo slati obavijesti na tvoj mail:',
                    'button_text': 'Vrati se na NotiFER'
                },
                'resume': {
                    'title': 'Obavijesti uključene',
                    'icon': '',
                    'heading': 'Obavijesti uključene',
                    'description': 'Opet ćemo slati obavijesti na tvoj mail:',
                    'button_text': 'Vrati se na NotiFER'
                },
                'error': {
                    'title': 'Greška',
                    'icon': '',
                    'button_text': 'Vrati se na NotiFER',
                    'messages': {
                        'INVALID_TOKEN': 'Ovaj link je istekao ili nije valjan.'
                    }
                }
            },
            'en': {
                'confirm': {
                    'activate': {
                        'title': 'Confirm activation',
                        'icon': '🔔',
                        'heading': 'Activate notifications?',
                        'description': 'Click the button below to activate schedule change notifications.',
                        'confirm_text': 'Activate',
                        'cancel_text': 'Cancel',
                        'button_class': '',
                    },
                    'delete': {
                        'title': 'Confirm deletion',
                        'icon': '🗑️',
                        'heading': 'Delete account?',
                        'description': 'Click the button below to permanently delete your subscription:',
                        'confirm_text': 'Delete',
                        'cancel_text': 'Cancel',
                        'button_class': 'button-error',
                    },
                    'pause': {
                        'title': 'Confirm pause',
                        'icon': '⏸️',
                        'heading': 'Pause notifications?',
                        'description': 'Click the button below to pause notifications for:',
                        'confirm_text': 'Pause',
                        'cancel_text': 'Cancel',
                        'button_class': '',
                    },
                    'resume': {
                        'title': 'Confirm resume',
                        'icon': '▶️',
                        'heading': 'Resume notifications?',
                        'description': 'Click the button below to resume notifications for:',
                        'confirm_text': 'Resume',
                        'cancel_text': 'Cancel',
                        'button_class': '',
                    },
                },
                'activate': {
                    'title': 'Notifications activated!',
                    'icon': '',
                    'heading': 'Notifications activated!',
                    'description': 'You are now subscribed to schedule change notifications.',
                    'additional_message': 'We will monitor your calendar and notify you when changes occur.',
                    'button_text': 'Return to NotiFER'
                },
                'delete': {
                    'title': 'Account deleted',
                    'icon': '',
                    'heading': 'Account deleted',
                    'description': 'We have deleted your account:',
                    'button_text': 'Return to NotiFER'
                },
                'pause': {
                    'title': 'Notifications paused',
                    'icon': '',
                    'heading': 'Notifications paused',
                    'description': 'We will no longer send notifications to your email:',
                    'button_text': 'Return to NotiFER'
                },
                'resume': {
                    'title': 'Notifications resumed',
                    'icon': '',
                    'heading': 'Notifications resumed',
                    'description': 'We will resume sending notifications to your email:',
                    'button_text': 'Return to NotiFER'
                },
                'error': {
                    'title': 'Error',
                    'icon': '',
                    'button_text': 'Return to NotiFER',
                    'messages': {
                        'INVALID_TOKEN': 'This link has expired or is invalid.'
                    }
                }
            }
        }

    def _get_locale(self, request: Request) -> str:
        """Detect user's preferred language."""
        accept_language = request.headers.get('accept-language', '')
        if 'en' in accept_language.lower():
            return 'en'
        return 'hr'

    def render_response(
            self,
            request:
            Request,
            response_type: str,
            email: str | None = None,
            custom_title: str | None = None,
            custom_message: str | None = None,
            language: str | None = None
    ) -> HTMLResponse:
        """
        Render a response page using the consolidated template.
        
        Args:
            request: FastAPI request object
            response_type: One of 'activate', 'delete', 'pause', 'resume', 'error'
            email: User email to display (optional)
            custom_title: Custom title for error pages
            custom_message: Custom message for error pages
            language: Force specific language (optional)
        """
        if language is None:
            language = self._get_locale(request)

        translations = self.translations[language][response_type]

        context = {
            'request': request,
            'title': custom_title if custom_title is not None else translations['title'],
            'icon': translations['icon'],
            'heading': custom_title if custom_title is not None else translations['heading'],
            'base_url': self.api_url,
            'button_text': translations['button_text'],
            'lang': language
        }

        if response_type == 'error':
            context['description'] = custom_message
        else:
            context['description'] = translations.get('description')
            context['additional_message'] = translations.get('additional_message')
            if email:
                context['email'] = email

        return self.templates.TemplateResponse('response.html', context)
    
    def render_error(self, request: Request, title: str | None, message: str, language: str | None = None, error_type: ErrorCode | None = None) -> HTMLResponse:
        if language is None:
            language = self._get_locale(request)

        if title is None:
            title = self.translations[language]['error']['title']

        if error_type is not None and error_type == ErrorCode.INVALID_TOKEN:
            message = self.translations[language]['error']['messages']['INVALID_TOKEN']

        return self.render_response(request, 'error', custom_title=title, custom_message=message, language=language)
    
    def render_confirm(
            self,
            request: Request,
            action: str,
            token: str,
            action_url: str,
            email: str | None = None,
            language: str | None = None
    ) -> HTMLResponse:
        if language is None:
            language = self._get_locale(request)

        t = self.translations[language]['confirm'][action]

        context = {
            'request': request,
            'title': t['title'],
            'icon': t['icon'],
            'heading': t['heading'],
            'description': t.get('description'),
            'email': email,
            'action_url': action_url,
            'confirm_text': t['confirm_text'],
            'cancel_text': t['cancel_text'],
            'button_class': t['button_class'],
            'cancel_url': self.api_url,
            'lang': language,
        }

        return self.templates.TemplateResponse('confirm.html', context)

    def render_activate(self, request: Request, language: str | None = None) -> HTMLResponse:
        return self.render_response(request, 'activate', language=language)
    
    def render_delete(self, request: Request, email: str, language: str | None = None) -> HTMLResponse:
        return self.render_response(request, 'delete', email=email, language=language)
    
    def render_pause(self, request: Request, email: str, language: str | None = None) -> HTMLResponse:
        return self.render_response(request, 'pause', email=email, language=language)
    
    def render_resume(self, request: Request, email: str, language: str | None = None) -> HTMLResponse:
        return self.render_response(request, 'resume', email=email, language=language)
