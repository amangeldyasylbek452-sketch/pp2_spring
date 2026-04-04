import psycopg2
from config import load_config


def connect():
    config = load_config()
    return psycopg2.connect(**config)