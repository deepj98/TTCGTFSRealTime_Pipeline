from TTC_RealTimeData import transform_data
from TTC_RealTimeData import fetch_ttc_realtime_data

df = transform_data(fetch_ttc_realtime_data())
if df is not None:
    print(f"shape: {df.shape}")
    print(df.head())

else:
    print("data transformation failed")