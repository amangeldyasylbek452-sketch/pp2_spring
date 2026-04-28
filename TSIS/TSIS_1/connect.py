import psycopg2
from convig import load_config


def connect():
    config = load_config()
    return psycopg2.connect(**config)