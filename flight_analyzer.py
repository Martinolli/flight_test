import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Flight Data Analyzer",
    page_icon="✈️",
    layout="wide"
)

# --- App Title and Description ---
st.title("✈️ Flight Data Analyzer")
st.markdown("""
This tool allows you to upload your flight data CSV file, select the parameters you want to analyze, 
and visualize them in an interactive chart.
""")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a flight data CSV file",
    type="csv"
)

# --- Main Logic ---
if uploaded_file is not None:
    # Use Streamlit's caching to avoid reloading data on every interaction.
    @st.cache_data
    def load_data(file):
        # Assumes the first column is the time index
        df = pd.read_csv(file)
        return df

    try:
        df = load_data(uploaded_file)

        st.success("File uploaded successfully! Here's a preview of your data:")
        st.dataframe(df.head())

        # --- Column Selection ---
        st.header("2. Select Parameters to Plot")
        
        # Assume the first column is the time/index column
        time_column = df.columns[0]
        
        # Get all other columns for the user to select from
        available_columns = df.columns[1:].tolist()
        
        selected_columns = st.multiselect(
            "Select one or more parameters:",
            options=available_columns,
            default=available_columns[0] if available_columns else [] # Default to the first parameter
        )

        # --- Plotting ---
        if not selected_columns:
            st.warning("Please select at least one parameter to plot.")
        else:
            st.header("3. Analyze Your Data")
            
            # Create an interactive plot using Plotly Express
            fig = px.line(
                df,
                x=time_column,
                y=selected_columns,
                title="Flight Parameters vs. Time",
                labels={"value": "Value", "variable": "Parameter"}
            )
            
            # Update layout for better readability
            fig.update_layout(
                xaxis_title=time_column,
                yaxis_title="Selected Values",
                legend_title="Parameters"
            )
            
            # Display the plot in the app
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file to begin.")