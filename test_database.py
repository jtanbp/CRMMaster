import psycopg2

try:
    conn = psycopg2.connect(
        dbname="onexdb",
        user="jtan",
        password="parkgreen",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()

    # Force schema
    cur.execute("SET search_path TO public;")

    cur.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_name ILIKE 'supplier';
                """)
    print(cur.fetchall())

    cur.execute("SELECT * FROM public.supplier LIMIT 5;")
    print(cur.fetchall())

    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)