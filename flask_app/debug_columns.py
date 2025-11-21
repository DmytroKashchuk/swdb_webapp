
import psycopg2
import psycopg2.extras

def get_db_connection():
    return psycopg2.connect(
        host="10.20.5.20",
        port=5432,
        dbname="swdb",
        user="postgres_dima",
        password="Dadomagico96!",
    )

def test_query():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Example for 2015
    query = """
        SELECT *
        FROM usa_2015_hist2015_model pi
        JOIN usa_2015_hist2015_modeldesc ps
          ON pi.tabkey = ps.tabkey
        LIMIT 1;
    """
    
    try:
        cur.execute(query)
        row = cur.fetchone()
        if row:
            print("Keys in row dict:", list(row.keys()))
        
        if cur.description:
            col_names = [desc.name for desc in cur.description]
            print("Columns in description:", col_names)
            
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    test_query()
