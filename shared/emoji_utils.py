import emoji
from starlette.responses import HTMLResponse

TWEMOJI_BASE = 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/'


def emojify(response) -> HTMLResponse:
    content = getattr(response, 'body', '')
    response.render(content)
    
    rendered_text = response.body.decode('utf8')
    
    def repl(e, _):
        hex_codes = '-'.join(f'{ord(c):x}' for c in e)
        url = f'{TWEMOJI_BASE}{hex_codes}.png'
        return f'<img src="{url}" alt="{e}" style="height:1em; vertical-align:-0.1lem;">'
    
    new_text = emoji.replace_emoji(rendered_text, repl)
    encoded_content = new_text.encode('utf-8')
    
    response.headers['Content-Length'] = str(len(encoded_content))
    
    return HTMLResponse(content=encoded_content, status_code=response.status_code, headers=response.headers)
