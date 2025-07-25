import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# === 1. Load and prepare data ===

file_path = 'data/234_01.csv'  # Update if your file is elsewhere

# Load with header row 0, skip code/unit rows (rows 1 and 2)
df = pd.read_csv(file_path, header=0, skiprows=[1,2])
df.rename(columns={df.columns[0]: "Time"}, inplace=True)

# Parse custom time 'Day:Hour:Minute:Second.Millisecond' to elapsed seconds
def parse_custom_time(t):
    try:
        days, hours, mins, sec_ms = t.split(':')
        sec, ms = sec_ms.split('.')
        total_seconds = (
            int(days) * 24 * 3600 +
            int(hours) * 3600 +
            int(mins) * 60 +
            int(sec) +
            int(ms)/1000.0
        )
        return total_seconds
    except Exception:
        return None

df['Elapsed_Seconds'] = df['Time'].apply(parse_custom_time)

# Define sensor columns
sensor_cols = [col for col in df.columns if col not in ['Time', 'Elapsed_Seconds']]

# === Save processed data for future use ===
# Create a timestamp for this analysis session
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save processed dataframe with timestamp
processed_filename = f"processed_data/flight_data_processed_{timestamp}.csv"
df.to_csv(processed_filename, index=False)
print(f"Processed data saved: {processed_filename}")

# Save a summary file
summary_data = {
    'Total_Records': len(df),
    'Time_Range_Start': df['Elapsed_Seconds'].min(),
    'Time_Range_End': df['Elapsed_Seconds'].max(),
    'Duration_Seconds': df['Elapsed_Seconds'].max() - df['Elapsed_Seconds'].min(),
    'Sensors': list(sensor_cols),
    'Analysis_Timestamp': datetime.now().isoformat()
}

# Create sensor statistics
sensor_stats = df[sensor_cols].describe()
sensor_stats.to_csv(f"processed_data/sensor_statistics_{timestamp}.csv")
print(f"Sensor statistics saved: processed_data/sensor_statistics_{timestamp}.csv")

# === 2. Plot each sensor, save as HTML ===

for sensor in sensor_cols:
    fig = px.line(
        df, x='Elapsed_Seconds', y=sensor,
        title=f'{sensor} vs Time',
        labels={'Elapsed_Seconds': 'Time (s)', sensor: 'Current (A)'}
    )
    # Show in notebook/script (optional)
    # fig.show()
    
    # Save to HTML in plots folder with timestamp
    html_filename = f"plots/{sensor}_{timestamp}.html"
    fig.write_html(html_filename)
    print(f"Saved: {html_filename}")

print(f"\nAll plots saved as HTML files in 'plots/' folder!")
print(f"Processed data saved in 'processed_data/' folder!")
print(f"Analysis session: {timestamp}")
print("\nOpen the HTML files in your browser to view interactively.")

