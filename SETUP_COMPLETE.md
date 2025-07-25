# Flight Test Data Analysis - Quick Setup Guide

## ✅ Your Environment is Ready

Your Python environment has been successfully set up with the following structure:

```bash
flight_test_data/
├── .venv/                    # Virtual environment (Python 3.13.5)
├── data/                     # Folder for additional data files
├── plots/                    # Generated interactive HTML plots
├── processed_data/           # Processed data and statistics
├── 234.csv                   # Your original flight data
├── plot_data.py             # Main analysis script
├── advanced_analysis.py     # Statistical analysis script
├── requirements.txt         # Dependencies list
├── run_analysis.bat         # Easy-run script for main analysis
├── run_advanced_analysis.bat # Easy-run script for advanced analysis
└── README.md               # Documentation
```

## 🚀 How to Run Your Analysis

### Option 1: Double-click the batch files

- `run_analysis.bat` - Generates interactive HTML plots
- `run_advanced_analysis.bat` - Creates statistical analysis plots

### Option 2: Use VS Code terminal

```powershell
# Navigate to your project
cd "c:\Users\joao.bosco\OneDrive\Documentos\vscode_01\flight_test_data"

# Run main analysis
& ".\.venv\Scripts\python.exe" plot_data.py

# Run advanced analysis
& ".\.venv\Scripts\python.exe" advanced_analysis.py
```

## 📊 What Gets Generated

### Every analysis run creates timestamped files

1. **Interactive HTML Plots** (in `plots/` folder):
   - Generator current vs time
   - Battery current vs time
   - DC current measurements vs time
   - Exciter current vs time

2. **Processed Data** (in `processed_data/` folder):
   - Cleaned CSV with elapsed time calculations
   - Statistical summaries (mean, std, min, max)

3. **Statistical Analysis** (when running advanced_analysis.py):
   - Correlation heatmap between sensors
   - Distribution histograms
   - Outlier detection box plots
   - Time series overview

## 🔧 Adding New Data Files

1. Place new CSV files in the `data/` folder
2. Update the `file_path` variable in `plot_data.py`
3. Run the analysis scripts

## 📈 Viewing Results

- **HTML Plots**: Open any `.html` file in `plots/` folder with your web browser
- **Statistical Plots**: Open `.png` files in `plots/` folder
- **Data**: Open `.csv` files in `processed_data/` folder with Excel or any CSV viewer

## 🔄 Future Sessions

Your environment is persistent! Just run the batch files or use the terminal commands above to analyze new data or re-run existing analysis.

## 📦 Installed Packages

- pandas (data manipulation)
- plotly (interactive plots)
- matplotlib & seaborn (statistical plots)
- numpy (numerical computing)

---
**Environment created on:** July 23, 2025  
**Python version:** 3.13.5  
**Virtual environment:** Ready to use!
