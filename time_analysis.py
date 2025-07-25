import pandas as pd

# Load and parse data
df = pd.read_csv('234.csv', header=0, skiprows=[1,2])
df.rename(columns={df.columns[0]: 'Time'}, inplace=True)

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

print('=== TIME ANALYSIS ===')
print(f'Original time format: {df["Time"].iloc[0]}')
print(f'First data point: {df["Elapsed_Seconds"].iloc[0]:.1f} seconds')
print(f'Last data point: {df["Elapsed_Seconds"].iloc[-1]:.1f} seconds')
print(f'Total duration: {df["Elapsed_Seconds"].iloc[-1] - df["Elapsed_Seconds"].iloc[0]:.1f} seconds')
print(f'Time between samples: {df["Elapsed_Seconds"].iloc[1] - df["Elapsed_Seconds"].iloc[0]:.1f} seconds')
print(f'Sample rate: {1/(df["Elapsed_Seconds"].iloc[1] - df["Elapsed_Seconds"].iloc[0]):.0f} Hz')
print('\n=== ANALYSIS SUMMARY ===')
print('X-axis unit: SECONDS (with millisecond precision)')
print('Time resolution: 0.1 seconds (100 milliseconds)')
print('Data sampling: 10 Hz (10 samples per second)')
