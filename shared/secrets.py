import os

def get_secret(env_var_name: str, default: str | None = None) -> str:
    value = os.getenv(env_var_name)
    if value and os.path.exists(value):
        try:
            with open(value, 'r') as f:
                return f.read().strip()
            
        except Exception as e:
            return default
    
    return value if value is not None else default
