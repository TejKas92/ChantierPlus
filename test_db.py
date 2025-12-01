import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost/postgres')
        print("Connected to postgres database successfully!")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect to postgres: {e}")

    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost/chantierplus')
        print("Connected to chantierplus database successfully!")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect to chantierplus: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
