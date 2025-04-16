import sqlite3
import pandas as pd


def save_to_db(df):
    conn = sqlite3.connect("data/sites.db")
    df.to_sql("sites", conn, if_exists="replace", index=False)
    conn.close()


def parse_prices():
    try:
        conn = sqlite3.connect("data/sites.db")
        df = pd.read_sql_query("SELECT * FROM sites", conn)
        conn.close()
        return df

    except Exception as e:
        return None