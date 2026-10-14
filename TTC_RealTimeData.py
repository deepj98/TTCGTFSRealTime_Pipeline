import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import re
import google.protobuf.message
from google.transit import gtfs_realtime_pb2
import os
from pathlib import Path
from dotenv import load_dotenv

# Database Configuration
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "dbvalue.env"
load_dotenv(dotenv_path=ENV_PATH)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TABLE_NAME = "TTC_GTFSRealTime"

#fetching real time raw data 

def fetch_ttc_realtime_data():
    gtfs_url = "https://bustime.ttc.ca/gtfsrt/vehicles"

    try:
        response = requests.get(gtfs_url, timeout=30)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        records = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                v = entity.vehicle
                records.append({
                    'vehicle_id': v.vehicle.id,
                    'route_id': v.trip.route_id,
                    'trip_id': v.trip.trip_id,
                    'latitude': v.position.latitude,
                    'longitude': v.position.longitude,
                    'bearing': v.position.bearing,
                    'speed': v.position.speed,
                    'timestamp': v.timestamp,
                })
        df = pd.DataFrame(records)
        print(f"fetched {len(df)} vehicle records from GTFS-RT")
        return df
    except Exception as e:
        print(f"GTFS-RT fetch failed: {e}")
        return None

#Transforming the raw data - Filters for now 
def transform_data(df):
    if df is None or len(df) == 0:
        return None
    df = df.copy()
    
    df.columns=(df.columns.str.strip().str.replace(' ', '_').str.replace(r'[^a-zA-Z0-9_]','',regex=True)
            .str.lower()
            )
    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].dtype in ['int64','float64']:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna('Unknown')

    print(f"transformatoin complete")
    return df

#Load data final stage after cleaning 
def load_data(df, table_name):
    if df is None or len(df) == 0:
        print("No data found")
        return False

    engine = create_engine(DATABASE_URL)

    df.to_sql(
        table_name,
        engine,
        if_exists = 'replace',
        index = False,
        chunksize = 1000
    )
    print("Data added")
    return True

# Main class
if __name__=="__main__":
    print("=" * 60)
    print("TTC GTFS-RT ETL PIPELINE")
    print("=" * 60)

    extract_data = fetch_ttc_realtime_data()
    clean_data = transform_data(extract_data)
    load_data(clean_data, TABLE_NAME)
    

    







