from TTC_RealTimeData import fetch_ttc_realtime_data

df = fetch_ttc_realtime_data()
if df is not None:
    print("shape: {df.shape}")
    print(df.head())

else:
    print("data extraction failed")