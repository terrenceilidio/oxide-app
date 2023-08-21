from flask import Flask, jsonify
import requests
import psycopg2

app = Flask(__name__)

# Define constants
ENDPOINT = "https://www.reddit.com/r/Wallstreetbets/top.json?limit=10&t=year"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'password',
    'database': 'mydatabase',
}

def create_reddit_table(conn):
    create_query = """
        CREATE TABLE IF NOT EXISTS Reddit (
            API VARCHAR,
            Description VARCHAR,
            Auth VARCHAR,
            HTTPS BOOLEAN,
            Cors VARCHAR,
            Link VARCHAR,
            Category VARCHAR,
            amount VARCHAR
        )
    """
    with conn.cursor() as cursor:
        cursor.execute(create_query)
        conn.commit()

def insert_reddit_data(conn, data_item):
    insert_query = """
        INSERT INTO Reddit (API, Description, Auth, HTTPS, Cors, Link, Category, amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cursor:
        cursor.execute(insert_query, (
            data_item['API'],
            data_item['Description'],
            data_item['Auth'],
            data_item['HTTPS'],
            data_item['Cors'],
            data_item['Link'],
            data_item['Category'],
            data_item['amount']
        ))
        conn.commit()

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/push/to/sql')
def push_to_sql():
    response = requests.get(ENDPOINT)

    if response.status_code == 200:
        json_response = response.json()

        conn = psycopg2.connect(**DB_CONFIG)
        create_reddit_table(conn)

        # Insert each item from the JSON response into the data table
        for item in json_response['data']['children']:
            data_item = item['data']
            insert_reddit_data(conn, data_item)

        conn.close()
        return "Done inserting data into table."
    else:
        return "Error: " + str(response.status_code)

@app.route('/get/all/rows')
def get_all_rows():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            select_query = "SELECT * FROM Reddit"
            cursor.execute(select_query)

            rows = cursor.fetchall()
            return jsonify(rows)
    finally:
        conn.close()

if __name__ == "__main__":
    app.run()
