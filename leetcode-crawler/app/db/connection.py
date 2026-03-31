import psycopg2
from app.config.settings import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)