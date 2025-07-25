import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

def load_and_analyze_data(csv_file):
    """
    Load flight test data and perform comprehensive analysis
    """
    # Load data
    df = pd.read_csv(csv_file, header=0, skiprows=[1,2])
    df.rename(columns={df.columns[0]: "Time"}, inplace=True)
    
    # Parse time
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
    
    return df


def create_statistical_plots(df, timestamp):
    """
    Create comprehensive statistical analysis plots
    """
    sensor_cols = [col for col in df.columns if col not in ['Time', 'Elapsed_Seconds']]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Flight Test Data Statistical Analysis', fontsize=16)
    
    # 1. Correlation heatmap
    correlation_matrix = df[sensor_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[0,0])
    axes[0,0].set_title('Sensor Correlation Matrix')
    
    # 2. Distribution plots
    for sensor in sensor_cols:
        df[sensor].hist(bins=30, ax=axes[0,1], alpha=0.7, label=sensor)
    axes[0,1].set_title('Current Distribution Histograms')
    axes[0,1].legend()
    
    # 3. Box plots for outlier detection
    df[sensor_cols].boxplot(ax=axes[1,0], rot=45)
    axes[1,0].set_title('Outlier Detection (Box Plots)')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # 4. Time series overview
    for sensor in sensor_cols[:4]:  # Show first 4 sensors
        axes[1,1].plot(df['Elapsed_Seconds'], df[sensor], label=sensor, alpha=0.7)
    axes[1,1].set_title('Time Series Overview (First 4 Sensors)')
    axes[1,1].set_xlabel('Time (seconds)')
    axes[1,1].set_ylabel('Current (A)')
    axes[1,1].legend()
    
    plt.tight_layout()
    
    # Save plot
    plot_filename = f"plots/statistical_analysis_{timestamp}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Statistical analysis plot saved: {plot_filename}")

if __name__ == "__main__":
    # Load data
    df = load_and_analyze_data('data/234_01.csv')
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create statistical plots
    create_statistical_plots(df, timestamp)
    
    # Print summary statistics
    sensor_cols = [col for col in df.columns if col not in ['Time', 'Elapsed_Seconds']]
    print("\n=== FLIGHT TEST DATA SUMMARY ===")
    print(f"Analysis timestamp: {timestamp}")
    print(f"Total data points: {len(df)}")
    print(f"Duration: {df['Elapsed_Seconds'].max() - df['Elapsed_Seconds'].min():.2f} seconds")
    print(f"Number of sensors: {len(sensor_cols)}")
    
    print("\n=== SENSOR STATISTICS ===")
    for sensor in sensor_cols:
        data = df[sensor]
        print(f"\n{sensor}:")
        print(f"  Mean: {data.mean():.2f} A")
        print(f"  Std:  {data.std():.2f} A")
        print(f"  Min:  {data.min():.2f} A")
        print(f"  Max:  {data.max():.2f} A")
