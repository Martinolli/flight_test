# Flight Test Data Analysis Project

This project analyzes flight test current sensor data from various aircraft systems.

## Setup Instructions

1. **Activate the virtual environment:**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the analysis:**

   ```powershell
   python plot_data.py
   ```

## Project Structure

```bash
flight_test_data/
├── data/              # Raw data files (future datasets)
├── plots/             # Generated HTML plots with timestamps
├── processed_data/    # Cleaned and processed data with statistics
├── .venv/            # Python virtual environment
├── 234.csv           # Original data file - deprecated - change to `data`
├── plot_data.py      # Main analysis script
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Data Files

- **234.csv**: Original flight test data with current measurements from various sensors
- **processed_data/**: Contains timestamped processed data and statistics for future reference

## Sensor Data

The data includes current measurements from:

- PDUL352GENCURRENT: Generator current
- PDUL354BATTCURRENT: Battery current
- MBATL340DCCURRENT: Main battery DC current
- BBATL340DCCURRENT: Backup battery DC current
- SGCUL301BSGEXCITERPOSITIVEPEAKCURRENT: Exciter positive peak current
- SGCUL303BCUDCINPUTOUTPUTCURRENT: CUD DC input/output current

## Output Files

Each analysis run creates timestamped files:

- Interactive HTML plots in `plots/` folder
- Processed CSV data in `processed_data/` folder
- Statistical summaries of sensor data

## Future Enhancements

- Add more data files to the `data/` folder
- Compare multiple flight test sessions
- Add statistical analysis and anomaly detection
- Create dashboard for real-time monitoring

## Flight Analyzer Enhanced Streamlit Interface

- To run the APP use:

   1 - Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser .venv\Scripts\Activate

   2 - Set-ExecutionPolicy Bypass -Scope Process -Force .venv\Scripts\Activate

   3- & .\.venv\Scripts\Activate.ps1

   & C:\Users\joao.bosco\OneDrive\Documentos\vscode_01\flight_test_data\.venv\Scripts\Activate.ps1
   and
   'streamlit run flight_analyzer_enhanced.py`
