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
uploaded_file = st.file_uploader(
    "Choose a flight data file (tab-separated)",
    type=["csv", "txt"]
)

@st.cache_data
def load_data(file):
    """
    Loads and processes the flight data file.
    - Reads the file using the first column as the index.
    - Converts the index to datetime objects.
    - Cleans and formats the column names.
    - Calculates elapsed time.
    """
    # CORRECTED: Read the data, setting the first column (timestamps) as the index
    # and treating the first two rows as a multi-level header.
    df = pd.read_csv(file, sep='\t', header=[0, 1], index_col=0)

    # --- Convert Index to Datetime ---
    # Convert the index (which contains the timestamp strings) to datetime objects.
    # We drop any rows where the timestamp string is invalid and cannot be converted.
    df.index = pd.to_datetime(df.index, format='%j:%H:%M:%S.%f', errors='coerce')
    df.dropna(axis=0, inplace=True) # Drop rows with NaT (Not a Time) in the index
    df.index.name = 'Timestamp'

    # --- Clean up column names ---
    new_columns = []
    for param, unit in df.columns:
        # Create a clean "Parameter (Unit)" name
        if pd.notna(unit) and str(unit).strip() != '':
            new_columns.append(f"{param} ({unit})")
        else:
            new_columns.append(param)
    df.columns = new_columns
    
    # Convert all data columns to numeric, coercing errors to NaN
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Move the Timestamp from the index to a regular column for easier use
    df.reset_index(inplace=True)

    # --- Calculate Elapsed Time ---
    # This check is important in case all rows were dropped
    if not df.empty:
        start_time = df['Timestamp'].min()
        df['Elapsed Time (s)'] = (df['Timestamp'] - start_time).dt.total_seconds()
    
    return df

# --- Main Logic ---
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        
        # --- ROBUSTNESS CHECK ---
        # Add a check to see if the DataFrame is empty after loading.
        # This prevents errors if no data rows could be parsed.
        if df.empty:
            st.error("Failed to parse any valid data rows from the file.")
            st.error("Please check that the file format is correct: tab-separated with two header rows and timestamps in the first column in `day:hr:min:sec.ms` format.")
        else:
            st.success("File processed successfully! Here's a preview:")
            st.dataframe(df.head())
            
            st.info(f"Time range: **{df['Timestamp'].min().time()}** to **{df['Timestamp'].max().time()}**")
            st.info(f"Duration: **{pd.to_timedelta(df['Elapsed Time (s)'].max(), unit='s')}**")
            st.info(f"Data points found: **{len(df)}**")
            
            st.markdown("---")

            # --- Column and Plot Configuration ---
            st.header("📊 Plot Configuration")
            col1, col2 = st.columns(2)

            with col1:
                available_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != 'Elapsed Time (s)']
                selected_columns = st.multiselect(
                    "Select parameters to plot:",
                    options=available_columns,
                    default=available_columns[:1] # Default to the first parameter
                )
            
            with col2:
                x_axis_choice = st.radio(
                    "Select X-Axis:",
                    options=['Elapsed Time (s)', 'Timestamp'],
                    horizontal=True
                )

            # --- Plotting ---
            if not selected_columns:
                st.warning("Please select at least one parameter to plot.")
            else:
                st.header("📈 Interactive Plot")
                fig = px.line(df, x=x_axis_choice, y=selected_columns, title="Flight Parameters Analysis")
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                # --- Data Statistics ---
                st.header("🔬 Data Statistics")
                stats = df[selected_columns].describe()
                st.dataframe(stats)

    except Exception as e:
        st.error(f"An unexpected error occurred: **{e}**")
        with st.expander("Click to see detailed error traceback"):
            st.code(traceback.format_exc())
else:
    st.info("Awaiting file upload...")

# --- Footer ---
st.markdown("---")
st.markdown("Developed with ❤️ by a fellow data enthusiast")