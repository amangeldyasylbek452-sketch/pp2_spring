import psycopg2
from config import DB

def get_conn():
    return psycopg2.connect(**DB)