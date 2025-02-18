import os

def get_secret(env_var_name: str, default: str | None = None) -> str:
    value = os.getenv(env_var_name)
    if value and os.path.exists(value):
        with open(value, 'r') as f:
            return f.read().strip()
    return value if value is not None else default
