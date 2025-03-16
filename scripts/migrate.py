import psycopg2
import os

supabase_conn = psycopg2.connect(
    dbname=os.getenv('SUPABASE_DB'),
    user=os.getenv('SUPABASE_USER'),
    password=os.getenv('SUPABASE_PASSWORD'),
    host=os.getenv('SUPABASE_HOST')
)
supabase_cursor = supabase_conn.cursor()

local_conn = psycopg2.connect(
    dbname=os.getenv('LOCAL_DB'),
    user=os.getenv('LOCAL_USER'),
    password=os.getenv('LOCAL_PASSWORD'),
    host=os.getenv('LOCAL_HOST'),
    port=os.getenv('LOCAL_PORT', 5432)
)
local_cursor = local_conn.cursor()

supabase_cursor.execute('SELECT email, calendar_auth, activated, paused, created FROM user_calendars;')

for email, calendar_auth, activated, paused, created in supabase_cursor.fetchall():
    local_cursor.execute(
        """
        INSERT INTO user_calendars (email, calendar_auth, activated, paused, created, previous_calendar_url, previous_calendar_hash, last_checked)
        VALUES (%s, %s, %s, %s, %s, NULL, NULL, NULL)
        ON CONFLICT (email) DO NOTHING;
        """,
        (email, calendar_auth, activated, paused, created)
    )

supabase_cursor.execute('SELECT date, count FROM resend_usage')

for date, count in supabase_cursor.fetchall():
    local_cursor.execute(
        """
        INSERT INTO resend_usage (date, count) VALUES (%s, %s)
        ON CONFLICT (date) DO NOTHING;
        """,
        (date, count)
    )

local_conn.commit()
supabase_conn.close()
local_conn.close()
