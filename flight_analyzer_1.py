
import streamlit as st
import pandas as pd
import plotly.express as px
import traceback

# --- Page Configuration ---
st.set_page_config(
    page_title="Flight Data Analyzer",
    page_icon="✈️",
    layout="wide"
)

# --- App Title and Description ---
st.title("✈️ Flight Data Analyzer")
st.markdown("""
Upload your tab-separated flight data file to visualize and analyze key parameters.
The file should have two header rows: the first for parameter names and the second for units.
""")

# --- File Uploader ---
# Use a more generic 'txt' or 'csv' since the format is text-based
uploaded_file = st.file_uploader(
    "Choose a flight data file (tab-separated)",
    type=["csv", "txt"]
)

@st.cache_data
def load_data(file):
    """
    Loads and processes the flight data file.
    - Reads the file using two rows for headers (parameters and units).
    - Cleans and formats the column names.
    - Converts data types for plotting.
    - Calculates elapsed time.
    """
    # Use header=[0, 1] to read the first two rows as a MultiIndex header
    df = pd.read_csv(file, sep='\t', header=[0, 1])

    # --- Clean up column names ---
    new_columns = []
    # The first column is a tuple like ('Description', 'EU'). We'll rename it.
    new_columns.append('Timestamp')

    # Iterate through the rest of the columns (which are tuples)
    for param, unit in df.columns[1:]:
        # Create a clean "Parameter (Unit)" name
        if pd.notna(unit) and unit.strip() != '':
            new_columns.append(f"{param} ({unit})")
        else:
            new_columns.append(param)
    
    # Assign the cleaned-up column names
    df.columns = new_columns
    
    # --- Convert data types ---
    # Convert Timestamp column to datetime objects
    # Format %j is for Day of the year as a zero-padded decimal number.
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%j:%H:%M:%S.%f', errors='coerce')
    
    # Convert all other columns to numeric, coercing errors to NaN
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows where all values are NaN
    df.dropna(how='all', inplace=True)

    # --- Calculate Elapsed Time ---
    if not df['Timestamp'].isna().all():
        start_time = df['Timestamp'].min()
        df['Elapsed Time (s)'] = (df['Timestamp'] - start_time).dt.total_seconds()
    else:
        df['Elapsed Time (s)'] = range(len(df))
        st.warning("No valid timestamps found. Using row numbers for elapsed time.")
    
    return df

# --- Main Logic ---
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        st.success("File processed successfully! Here's a preview:")
        st.dataframe(df.head())
        
        # Check if there are valid timestamps
        valid_timestamps = df['Timestamp'].dropna()
        if not valid_timestamps.empty:
            st.info(f"Time range: **{valid_timestamps.min().time()}** to **{valid_timestamps.max().time()}**")
            st.info(f"Duration: **{pd.to_timedelta(df['Elapsed Time (s)'].max(), unit='s')}**")
        else:
            st.warning("No valid timestamps found in the data.")
        
        st.info(f"Data points found: **{len(df)}**")
        
        st.markdown("---")

        # --- Column and Plot Configuration ---
        st.header("📊 Plot Configuration")
        col1, col2 = st.columns(2)

        with col1:
            # Get all numeric columns for the user to select from
            available_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != 'Elapsed Time (s)']
            
            selected_columns = st.multiselect(
                "Select parameters to plot:",
                options=available_columns,
                default=available_columns[0] if available_columns else []
            )
        
        with col2:
            # Allow user to choose the X-axis
            x_axis_options = ['Elapsed Time (s)']
            if not valid_timestamps.empty:
                x_axis_options.insert(0, 'Timestamp')
            
            x_axis_choice = st.radio(
                "Select X-Axis:",
                options=x_axis_options,
                horizontal=True
            )

        # --- Plotting ---
        if not selected_columns:
            st.warning("Please select at least one parameter to plot.")
        else:
            st.header("📈 Interactive Plot")
            
            fig = px.line(
                df,
                x=x_axis_choice,
                y=selected_columns,
                title="Flight Parameters Analysis",
                labels={"value": "Value", "variable": "Parameter"}
            )
            
            fig.update_layout(
                xaxis_title=x_axis_choice,
                yaxis_title="Selected Values",
                legend_title="Parameters",
                hovermode="x unified" # Great for comparing values at the same time instant
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # --- Data Statistics ---
            st.header("🔬 Data Statistics")
            st.markdown("Descriptive statistics for the selected parameters:")
            stats = df[selected_columns].describe()
            st.dataframe(stats)

    except Exception as e:
        st.error(f"An error occurred while processing the file: **{e}**")
        st.error("Please ensure your file is tab-separated and has two header rows as expected.")
        
        # SUGGESTION: Use an expander for the detailed error traceback
        with st.expander("Click to see detailed error information"):
            st.code(traceback.format_exc())
else:
    st.info("Awaiting file upload...")

# --- Footer ---
st.markdown("---")
st.markdown("Developed with ❤️ by a fellow data enthusiast")