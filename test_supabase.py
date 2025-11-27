import psycopg2

# Параметры из Supabase
HOST = "aws-1-eu-west-1.pooler.supabase.com"
PORT = 5432
DBNAME = "postgres"
USER = "postgres.nkkyxflxcrqueydzoqvs"
PASSWORD = "9C086908r.,"  # <— сюда

def main():
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            sslmode="require",  # Supabase без SSL не пустит
        )
        print("✅ Подключение к Supabase успешно!")

        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        print("Время на сервере:", cur.fetchone())

        cur.close()
        conn.close()
        print("✅ Соединение закрыто")

    except Exception as e:
        print("❌ Ошибка подключения:")
        print(e)

if __name__ == "__main__":
    main()
