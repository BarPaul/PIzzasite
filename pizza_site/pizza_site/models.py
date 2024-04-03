from django.db import connection

cur = connection.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    pizzas TEXT,
    is_completed BOOLEAN,
    created_at INTEGER,
    price INTEGER
)""")

def save_client(name, phone, price, *pizzas, is_completed=False):
    formatted = " ".join(pizzas)
    cur.execute(f"INSERT INTO clients VALUES (NULL, '{name}', '{phone}', '{formatted}', {int(is_completed)}, strftime('%s', 'now'), {price})")

def get_clients(column = "created_at") -> list[tuple]:
    cur.execute(f"SELECT * FROM clients ORDER BY {column}")
    return cur.fetchall()

def update_state(uid, state):
    cur.execute(f"UPDATE clients SET is_completed = {int(state)} WHERE id = {int(uid)}")
