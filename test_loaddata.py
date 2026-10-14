from sqlalchemy import create_engine, text
from TTC_RealTimeData import DATABASE_URL

engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        conn.execute(text("Select 1"))
        print("test connection successful")
except Exception as e:
    print(f"connection unsuccessfull:{e}")
    

