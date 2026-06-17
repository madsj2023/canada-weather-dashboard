import pandas as pd
import datetime

# 1. Configuration
# We define the stations and years we want
stations = [51442, 51157, 51459, 50430]
years = range(2021, 2026) # 2021 to 2025 inclusive

# List to hold the downloaded dataframes before merging
all_data = []

print("--- Starting Download ---")

# 2. Downloading and Merging
for station_id in stations:
    for year in years:
        # Construct the URL
        # Month=1 is required by the URL structure, but timeframe=2 (Daily) 
        # usually returns the full year regardless of the month provided.
        url = f"http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={year}&Month=1&timeframe=2"
        
        try:
            print(f"Downloading Station: {station_id} for Year: {year}...")
            # Read CSV directly from URL
            df = pd.read_csv(url)
            
            # Add to our list
            all_data.append(df)
            
        except Exception as e:
            print(f"Error downloading {station_id} - {year}: {e}")

# Merge all downloaded chunks into one large DataFrame
big_df = pd.concat(all_data, ignore_index=True)

# Save the raw daily data to a file
big_df.to_csv("weather_data_daily_2021_2025.csv", index=False)
print("Success: 'weather_data_daily_2021_2025.csv' created.")


# 3. Creating the Monthly Report
print("--- Creating Monthly Report ---")

# First, ensure the Date/Time is actual date format so we can extract Month/Year
big_df['Date/Time'] = pd.to_datetime(big_df['Date/Time'])

# We define specific math logic for each column
# We do not aggregate "Flags" or "Day" columns, only the value columns.
aggregation_rules = {
    'Max Temp (°C)': 'max',        # We want the HIGHEST temp reached in that month
    'Min Temp (°C)': 'min',        # We want the LOWEST temp reached in that month
    'Mean Temp (°C)': 'mean',      # We want the AVERAGE temperature of the month
    'Total Rain (mm)': 'sum',      # We want the TOTAL amount of rain
    'Total Snow (cm)': 'sum',      # We want the TOTAL amount of snow
    'Total Precip (mm)': 'sum',    # We want the TOTAL precipitation
    'Spd of Max Gust (km/h)': 'max'# We want the STRONGEST wind gust of the month
}

# We handle "Missing" columns gracefully. 
# Only attempt to aggregate columns that actually exist in the downloaded data.
existing_cols = [col for col in aggregation_rules.keys() if col in big_df.columns]
final_rules = {k: v for k, v in aggregation_rules.items() if k in existing_cols}

# Group by Station, Year, and Month, then apply the rules
monthly_report = big_df.groupby(['Station Name', 'Year', 'Month'])[existing_cols].agg(final_rules)

# Round the averages to 2 decimal places for cleaner reading
monthly_report = monthly_report.round(2)

# Save the monthly report
monthly_report.to_csv("weather_data_monthly_summary.csv")
print("Success: 'weather_data_monthly_summary.csv' created.")