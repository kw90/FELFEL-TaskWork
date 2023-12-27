from quality_metric_calculator.utils import read_env_bool, read_env_int, read_env_str

POSTGRES_USER = read_env_str("POSTGRES_USER")
POSTGRES_PASSWORD = read_env_str("POSTGRES_PASSWORD")
POSTGRES_DB = read_env_str("POSTGRES_DB")
POSTGRES_HOST = read_env_str("POSTGRES_HOST")
POSTGRES_PORT = read_env_int("POSTGRES_PORT")

UVICORN_WORKERS = read_env_int("UVICORN_WORKERS")
UVICORN_RELOAD = read_env_bool("UVICORN_RELOAD")
UVICORN_PORT = read_env_int("UVICORN_PORT")
UVICORN_HOST = read_env_str("UVICORN_HOST")
