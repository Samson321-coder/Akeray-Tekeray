import os
import sqlite3
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Load environment
DB_NAME = "rental_bot.db"
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL:
        if not POSTGRES_AVAILABLE:
            raise ImportError("DATABASE_URL is set but 'psycopg2' is not installed. Please run 'pip install psycopg2-binary'")
        # Use PostgreSQL
        # Koyeb/Render sometimes use postgres://, but psycopg2 prefers postgresql://
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url)
        return conn
    else:
        # Fallback to SQLite
        conn = sqlite3.connect(DB_NAME)
        return conn

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    conn = get_db_connection()
    
    # Handle placeholder difference: Postgres uses %s, SQLite uses ?
    if not is_postgres:
        query = query.replace("%s", "?")
    
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
            
        if commit:
            conn.commit()
            
        return result
    finally:
        cur.close()
        conn.close()

def init_db():
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    # PostgreSQL uses SERIAL for auto-increment, SQLite uses AUTOINCREMENT
    id_type = "SERIAL" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    # Create Users table
    execute_query(f'''
    CREATE TABLE IF NOT EXISTS users (
        id {id_type},
        telegram_id BIGINT UNIQUE,
        username TEXT,
        role TEXT DEFAULT 'user'
    )
    ''', commit=True)
    
    # Create Listings table
    execute_query(f'''
    CREATE TABLE IF NOT EXISTS listings (
        id {id_type},
        owner_id BIGINT,
        title TEXT,
        city TEXT DEFAULT 'Dilla',
        location TEXT,
        price TEXT,
        photo_file_id TEXT,
        contact_phone TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'pending',
        fee_amount REAL DEFAULT 0,
        transaction_id TEXT,
        last_checked_at TEXT
    )
    ''', commit=True)
    
    # Migration handling
    if is_postgres:
        # Postgres migration: ADD COLUMN IF NOT EXISTS
        execute_query("ALTER TABLE listings ADD COLUMN IF NOT EXISTS city TEXT DEFAULT 'Dilla'", commit=True)
        execute_query("ALTER TABLE listings ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending'", commit=True)
        execute_query("ALTER TABLE listings ADD COLUMN IF NOT EXISTS fee_amount REAL DEFAULT 0", commit=True)
        execute_query("ALTER TABLE listings ADD COLUMN IF NOT EXISTS transaction_id TEXT", commit=True)
        execute_query("ALTER TABLE listings ADD COLUMN IF NOT EXISTS last_checked_at TEXT", commit=True)
    else:
        # SQLite migration
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(listings)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'city' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN city TEXT DEFAULT 'Dilla'")
        if 'status' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN status TEXT DEFAULT 'pending'")
        if 'fee_amount' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN fee_amount REAL DEFAULT 0")
        if 'transaction_id' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN transaction_id TEXT")
        if 'last_checked_at' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN last_checked_at TEXT")
        conn.commit()
        conn.close()
    
    # Create Ratings table
    execute_query(f'''
    CREATE TABLE IF NOT EXISTS ratings (
        id {id_type},
        listing_id INTEGER,
        reviewer_id BIGINT,
        rating INTEGER,
        created_at TEXT
    )
    ''', commit=True)

def add_user(telegram_id, username, role='user'):
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    if is_postgres:
        query = 'INSERT INTO users (telegram_id, username, role) VALUES (%s, %s, %s) ON CONFLICT (telegram_id) DO NOTHING'
    else:
        query = 'INSERT OR IGNORE INTO users (telegram_id, username, role) VALUES (%s, %s, %s)'
    
    execute_query(query, (telegram_id, username, role), commit=True)

def get_user_role(telegram_id):
    result = execute_query('SELECT role FROM users WHERE telegram_id = %s', (telegram_id,), fetchone=True)
    return result[0] if result else 'user'

def add_listing(owner_id, title, city, location, price, photo_file_id, contact_phone, fee_amount=0):
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_postgres:
        query = '''
        INSERT INTO listings (owner_id, title, city, location, price, photo_file_id, contact_phone, created_at, status, fee_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        '''
    else:
        query = '''
        INSERT INTO listings (owner_id, title, city, location, price, photo_file_id, contact_phone, created_at, status, fee_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
    
    params = (owner_id, title, city, location, price, photo_file_id, contact_phone, created_at, 'pending', fee_amount)
    conn = get_db_connection()
        
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        if is_postgres:
            listing_id = cur.fetchone()[0]
        else:
            listing_id = cur.lastrowid
        conn.commit()
        return listing_id
    finally:
        cur.close()
        conn.close()

def update_listing_txid(listing_id, transaction_id):
    execute_query('UPDATE listings SET transaction_id = %s WHERE id = %s', (transaction_id, listing_id), commit=True)

def approve_listing(listing_id):
    execute_query('UPDATE listings SET status = %s WHERE id = %s', ('paid', listing_id), commit=True)

def get_listing_by_id(listing_id):
    return execute_query('SELECT * FROM listings WHERE id = %s', (listing_id,), fetchone=True)

def get_pending_listings_with_txid():
    """Returns all listings that have a transaction ID but are still pending."""
    return execute_query("SELECT * FROM listings WHERE status = 'pending' AND transaction_id IS NOT NULL ORDER BY id DESC", fetchall=True)

def get_listing_by_txid(txid):
    """Returns a listing by its transaction ID."""
    return execute_query("SELECT * FROM listings WHERE transaction_id = %s", (txid,), fetchone=True)

def get_all_listings():
    return execute_query("SELECT * FROM listings WHERE status = 'paid' ORDER BY id DESC", fetchall=True)

def search_listings(query, city=None):
    pattern = f'%{query}%'
    if city:
        return execute_query("SELECT * FROM listings WHERE status = 'paid' AND city = %s AND (location LIKE %s OR title LIKE %s) ORDER BY id DESC", (city, pattern, pattern), fetchall=True)
    return execute_query("SELECT * FROM listings WHERE status = 'paid' AND (city LIKE %s OR location LIKE %s OR title LIKE %s) ORDER BY id DESC", (pattern, pattern, pattern), fetchall=True)

def expire_old_listings():
    """Mark listings older than 60 days as expired."""
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    if is_postgres:
        query = "UPDATE listings SET status = 'expired' WHERE status = 'paid' AND created_at::timestamp <= NOW() - INTERVAL '60 days'"
    else:
        query = "UPDATE listings SET status = 'expired' WHERE status = 'paid' AND created_at <= date('now', '-60 days')"
    execute_query(query, commit=True)

def get_active_listing_count():
    result = execute_query("SELECT COUNT(*) FROM listings WHERE status = 'paid'", fetchone=True)
    return result[0] if result else 0

def get_pending_listing_count():
    result = execute_query("SELECT COUNT(*) FROM listings WHERE status = 'pending'", fetchone=True)
    return result[0] if result else 0

def get_total_user_count():
    result = execute_query("SELECT COUNT(*) FROM users", fetchone=True)
    return result[0] if result else 0

def add_rating(listing_id, reviewer_id, rating):
    from datetime import datetime
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Prevent duplicate ratings from the same reviewer on the same listing
    existing = execute_query(
        "SELECT id FROM ratings WHERE listing_id = %s AND reviewer_id = %s",
        (listing_id, reviewer_id), fetchone=True
    )
    if existing:
        execute_query(
            "UPDATE ratings SET rating = %s, created_at = %s WHERE listing_id = %s AND reviewer_id = %s",
            (rating, created_at, listing_id, reviewer_id), commit=True
        )
    else:
        execute_query(
            "INSERT INTO ratings (listing_id, reviewer_id, rating, created_at) VALUES (%s, %s, %s, %s)",
            (listing_id, reviewer_id, rating, created_at), commit=True
        )

def get_avg_rating(listing_id):
    result = execute_query(
        "SELECT AVG(rating), COUNT(*) FROM ratings WHERE listing_id = %s",
        (listing_id,), fetchone=True
    )
    if result and result[0]:
        return round(result[0], 1), result[1]
    return None, 0

def get_listings_by_owner(owner_id):
    return execute_query("SELECT * FROM listings WHERE owner_id = %s ORDER BY id DESC", (owner_id,), fetchall=True)

def delete_listing(listing_id):
    execute_query('DELETE FROM listings WHERE id = %s', (listing_id,), commit=True)

def unlist_listing(listing_id):
    execute_query("UPDATE listings SET status = 'rented' WHERE id = %s", (listing_id,), commit=True)

def get_all_users():
    return execute_query('SELECT telegram_id, username, role FROM users', fetchall=True)

def get_listings_needing_check(days=14):
    """Find active listings that haven't been checked in more than 'days'."""
    is_postgres = DATABASE_URL and POSTGRES_AVAILABLE
    if is_postgres:
        # Postgres uses INTERVAL
        query = """
        SELECT * FROM listings 
        WHERE status = 'paid' 
        AND (last_checked_at IS NULL OR last_checked_at::timestamp <= NOW() - INTERVAL %s)
        """
        interval = f'{days} days'
        return execute_query(query, (interval,), fetchall=True)
    else:
        # SQLite uses date()
        query = f"SELECT * FROM listings WHERE status = 'paid' AND (last_checked_at IS NULL OR last_checked_at <= date('now', '-{days} days'))"
        return execute_query(query, fetchall=True)

def update_last_checked(listing_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query("UPDATE listings SET last_checked_at = %s WHERE id = %s", (now, listing_id), commit=True)

def refresh_listing_date(listing_id):
    """Updates the created_at date to now, resetting the 60-day expiry clock."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query("UPDATE listings SET created_at = %s WHERE id = %s", (now, listing_id), commit=True)
