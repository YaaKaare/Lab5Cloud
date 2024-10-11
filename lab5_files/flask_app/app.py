from flask import Flask
import psycopg2
import redis

app = Flask(__name__)

# Configure Redis
r = redis.Redis(host="redis", port=6379)

# PostgreSQL connection parameters
db_params = {
    'dbname': 'mydatabase',
    'user': 'postgres',  
    'password': 'password',  
    'host': 'postgres',
    'port': '5432'
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

@app.route("/")
def home():
    # Increment count in Redis
    r.incr("hits")

    # Update count in PostgreSQL
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed."

    cur = conn.cursor()

    # Check if the visit count exists
    cur.execute("SELECT count FROM visit_count LIMIT 1;")
    visit = cur.fetchone()

    if visit is None:
        # Insert new visit count if it doesn't exist
        cur.execute("INSERT INTO visit_count (count) VALUES (1);")
    else:
        # Update the existing visit count
        new_count = visit[0] + 1
        cur.execute("UPDATE visit_count SET count = %s;", (new_count,))

    # Commit the transaction
    conn.commit()

    # Get the updated visit count for display
    cur.execute("SELECT count FROM visit_count LIMIT 1;")
    visit_count = cur.fetchone()[0]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return f"This page has been visited {visit_count} times."

if __name__ == "__main__":
    app.run(host="0.0.0.0")  





