import os


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


PROJECT_CONFIG = {
    "zhipuai_api_key": os.getenv("ZHIPUAI_API_KEY", ""),
    "email": {
        "host": os.getenv("EMAIL_HOST", "smtp.163.com"),
        "port": int(os.getenv("EMAIL_PORT", "465")),
        "use_ssl": env_bool("EMAIL_USE_SSL", True),
        "user": os.getenv("EMAIL_HOST_USER", ""),
        "password": os.getenv("EMAIL_HOST_PASSWORD", ""),
    },
}
