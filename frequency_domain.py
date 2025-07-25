import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Load the CSV file
df = pd.read_csv("241.csv", skiprows=1)

# Select acceleration columns labeled as 'g', 'g.1', 'g.2', 'g.3', and 'g.4'
acceleration_columns = ['g', 'g.1', 'g.2', 'g.3', 'g.4']

# Sampling rate assumption (e.g., 1 Hz if 1 sample per second)
sampling_rate = 1.0  # Hz

# Perform FFT and plot frequency spectrum for each selected column
plt.figure(figsize=(15, 10))
dominant_frequencies = {}

for i, column in enumerate(acceleration_columns, 1):
    signal = df[column].dropna().values
    n = len(signal)
    yf = fft(signal)
    xf = fftfreq(n, 1 / sampling_rate)[:n // 2]
    magnitude = 2.0 / n * np.abs(yf[:n // 2])

    plt.subplot(3, 2, i)
    plt.plot(xf, magnitude)
    plt.title(f"Frequency Spectrum of {column}")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    # Identify dominant frequency
    dominant_freq = xf[np.argmax(magnitude)]
    dominant_frequencies[column] = dominant_freq

plt.tight_layout()
plt.savefig("acceleration_frequency_spectra.png")
plt.show()

# Print dominant frequencies
for column, freq in dominant_frequencies.items():
    print(f"Dominant frequency for {column}: {freq:.2f} Hz")

