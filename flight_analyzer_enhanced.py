import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import traceback
import io
from datetime import datetime, timedelta
from scipy.fft import fft, fftfreq

# --- Page Configuration ---
st.set_page_config(
    page_title="Enhanced Flight Data Analyzer",
    page_icon="✈️",
    layout="wide"
)

# --- App Title and Description ---
st.title("✈️ Enhanced Flight Data Analyzer")
st.markdown("""
Advanced flight test data analysis tool with enhanced visualizations and flight-specific metrics.
Upload your tab-separated flight data file to visualize and analyze key parameters with specialized flight test features.
""")

# --- Utility Functions ---
@st.cache_data
def load_data(file):
    """
    Enhanced data loading with proper parsing and validation.
    """
    try:
        # Read the file content
        content = file.read().decode('utf-8-sig')
        lines = content.strip().split('\n')
        
        if len(lines) < 3:
            st.error("File must have at least 2 header rows and 1 data row")
            return pd.DataFrame()
        
        # Parse the header lines
        header1 = lines[0].split(',')  # Parameter names
        header2 = lines[1].split(',')  # Units
        
        # Create proper column names
        columns = []
        for i, (param, unit) in enumerate(zip(header1, header2)):
            if i == 0:  # First column is timestamp
                columns.append('Timestamp')
            else:
                if unit and unit.strip() and unit.strip() not in ['EU', '']:
                    columns.append(f"{param} ({unit})")
                else:
                    columns.append(param)
        
        # Parse the data rows
        data_rows = []
        for line in lines[2:]:  # Skip header lines
            if line.strip():  # Skip empty lines
                row = line.split(',')
                if len(row) == len(columns):  # Ensure row has correct number of columns
                    data_rows.append(row)
        
        if not data_rows:
            st.error("No valid data rows found")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        
        # Convert timestamp column
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%j:%H:%M:%S.%f', errors='coerce')
        
        # Remove rows with invalid timestamps
        df = df[df['Timestamp'].notna()]
        
        if df.empty:
            st.error("No valid timestamps found. Expected format: day:hour:minute:second.millisecond")
            return pd.DataFrame()
        
        # Convert numeric columns
        for col in df.columns:
            if col != 'Timestamp':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate elapsed time
        start_time = df['Timestamp'].min()
        df['Elapsed Time (s)'] = (df['Timestamp'] - start_time).dt.total_seconds()
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
    
def perform_frequency_analysis(df, column, sampling_rate=1.0):
    signal = df[column].dropna().values
    n = len(signal)
    yf = fft(signal)
    xf = fftfreq(n, 1 / sampling_rate)[:n // 2]
    magnitude = 2.0 / n * np.abs(yf[:n // 2])
    
    dominant_freq = xf[np.argmax(magnitude)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xf, y=magnitude, mode='lines'))
    fig.update_layout(
        title=f"Frequency Spectrum of {column}",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        hovermode="closest"
    )
    
    return fig, dominant_freq

def identify_flight_parameters(df):
    """
    Identify and categorize flight parameters based on common naming conventions.
    """
    categories = {
        'Altitude': [],
        'Speed': [],
        'Temperature': [],
        'Pressure': [],
        'Rate': [],
        'Other': []
    }
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['altitude', 'alt']):
            categories['Altitude'].append(col)
        elif any(keyword in col_lower for keyword in ['speed', 'airspeed', 'cas', 'tas', 'mach']):
            categories['Speed'].append(col)
        elif any(keyword in col_lower for keyword in ['temperature', 'temp', 'tat']):
            categories['Temperature'].append(col)
        elif any(keyword in col_lower for keyword in ['pressure', 'press']):
            categories['Pressure'].append(col)
        elif any(keyword in col_lower for keyword in ['rate']):
            categories['Rate'].append(col)
        else:
            if col not in ['Timestamp', 'Elapsed Time (s)']:
                categories['Other'].append(col)
    
    return categories

def calculate_performance_metrics(df):
    """
    Calculate flight performance metrics.
    """
    metrics = {}
    
    # Find altitude and speed columns
    altitude_cols = [col for col in df.columns if 'altitude' in col.lower()]
    speed_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['speed', 'cas', 'tas'])]
    
    if altitude_cols:
        alt_col = altitude_cols[0]
        metrics['Max Altitude (ft)'] = df[alt_col].max()
        metrics['Min Altitude (ft)'] = df[alt_col].min()
        metrics['Altitude Range (ft)'] = metrics['Max Altitude (ft)'] - metrics['Min Altitude (ft)']
        
        # Calculate climb rate if altitude rate column exists
        alt_rate_cols = [col for col in df.columns if 'altitude' in col.lower() and 'rate' in col.lower()]
        if alt_rate_cols:
            metrics['Max Climb Rate (ft/min)'] = df[alt_rate_cols[0]].max()
            metrics['Max Descent Rate (ft/min)'] = abs(df[alt_rate_cols[0]].min())
    
    if speed_cols:
        speed_col = speed_cols[0]
        metrics['Max Speed (kt)'] = df[speed_col].max()
        metrics['Min Speed (kt)'] = df[speed_col].min()
        metrics['Average Speed (kt)'] = df[speed_col].mean()
    
    # Flight duration
    if 'Elapsed Time (s)' in df.columns:
        metrics['Flight Duration (min)'] = df['Elapsed Time (s)'].max() / 60
    
    return metrics

def detect_anomalies(df, parameter, threshold_std=3):
    """
    Simple anomaly detection using standard deviation threshold.
    """
    if parameter not in df.columns:
        return pd.Series(dtype=bool)
    
    data = df[parameter].dropna()
    mean_val = data.mean()
    std_val = data.std()
    
    anomalies = abs(data - mean_val) > threshold_std * std_val
    return anomalies

def create_flight_envelope_plot(df):
    """
    Create a flight envelope plot (altitude vs speed).
    """
    altitude_cols = [col for col in df.columns if 'altitude' in col.lower() and 'rate' not in col.lower()]
    speed_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['cas', 'tas', 'speed']) and 'rate' not in col.lower()]
    
    if not altitude_cols or not speed_cols:
        return None
    
    alt_col = altitude_cols[0]
    speed_col = speed_cols[0]
    
    fig = px.scatter(df, x=speed_col, y=alt_col, 
                    title="Flight Envelope (Altitude vs Speed)",
                    color='Elapsed Time (s)',
                    color_continuous_scale='viridis')
    
    fig.update_layout(
        xaxis_title=speed_col,
        yaxis_title=alt_col,
        hovermode='closest'
    )
    
    return fig

def create_multi_axis_plot(df, primary_params, secondary_params):
    """
    Create a plot with multiple y-axes for parameters with different scales.
    """
    if not primary_params and not secondary_params:
        return None
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add primary parameters
    for param in primary_params:
        fig.add_trace(
            go.Scatter(x=df['Elapsed Time (s)'], y=df[param], name=param, line=dict(width=2)),
            secondary_y=False,
        )
    
    # Add secondary parameters
    for param in secondary_params:
        fig.add_trace(
            go.Scatter(x=df['Elapsed Time (s)'], y=df[param], name=param, line=dict(dash='dash')),
            secondary_y=True,
        )
    
    # Set axis titles
    fig.update_xaxes(title_text="Elapsed Time (s)")
    if primary_params:
        fig.update_yaxes(title_text="Primary Parameters", secondary_y=False)
    if secondary_params:
        fig.update_yaxes(title_text="Secondary Parameters", secondary_y=True)
    
    fig.update_layout(title="Multi-Axis Parameter Plot", hovermode="x unified")
    
    return fig

# --- Main Application ---
uploaded_file = st.file_uploader(
    "Choose a flight data file (tab-separated)",
    type=["csv", "txt"]
)

if uploaded_file is not None:
    try:
        # Load and process data
        df = load_data(uploaded_file)
        
        if df.empty:
            st.error("Failed to parse any valid data rows from the file.")
            st.error("Please check that the file format is correct.")
        else:
            # Display basic information
            st.success("File processed successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Data Points", len(df))
            with col2:
                st.metric("Parameters", len([col for col in df.columns if col not in ['Timestamp', 'Elapsed Time (s)']]))
            with col3:
                if 'Elapsed Time (s)' in df.columns:
                    duration_min = df['Elapsed Time (s)'].max() / 60
                    st.metric("Duration (min)", f"{duration_min:.1f}")
            
            # Identify parameter categories
            param_categories = identify_flight_parameters(df)
            
            # Sidebar for navigation
            st.sidebar.header("Analysis Options")
            analysis_type = st.sidebar.selectbox(
                "Select Analysis Type",
                ["Basic Visualization", "Flight Envelope", "Performance Metrics", "Anomaly Detection", "Multi-Axis Plot", "Frequency Analysis"]
            )
            
            # Main content based on selection
            if analysis_type == "Basic Visualization":
                st.header("📊 Basic Parameter Visualization")
                
                # Parameter selection with categories
                st.subheader("Parameter Selection")
                selected_params = []
                
                for category, params in param_categories.items():
                    if params:
                        with st.expander(f"{category} Parameters ({len(params)})"):
                            for param in params:
                                if st.checkbox(param, key=f"basic_{param}"):
                                    selected_params.append(param)
                
                if selected_params:
                    x_axis = st.selectbox("X-Axis", ['Elapsed Time (s)', 'Timestamp'])
                    
                    fig = px.line(df, x=x_axis, y=selected_params, 
                                title="Flight Parameters Over Time")
                    fig.update_layout(hovermode="x unified", height=600)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistics
                    st.subheader("Parameter Statistics")
                    stats = df[selected_params].describe()
                    st.dataframe(stats)
                else:
                    st.warning("Please select at least one parameter to plot.")
            
            elif analysis_type == "Flight Envelope":
                st.header("🛩️ Flight Envelope Analysis")
                
                envelope_fig = create_flight_envelope_plot(df)
                if envelope_fig:
                    st.plotly_chart(envelope_fig, use_container_width=True)
                    
                    st.info("The flight envelope shows the relationship between altitude and speed throughout the flight, colored by time progression.")
                else:
                    st.warning("Flight envelope plot requires altitude and speed parameters.")
            
            elif analysis_type == "Performance Metrics":
                st.header("📈 Flight Performance Metrics")
                
                metrics = calculate_performance_metrics(df)
                
                if metrics:
                    # Display metrics in columns
                    cols = st.columns(3)
                    for i, (metric, value) in enumerate(metrics.items()):
                        with cols[i % 3]:
                            if isinstance(value, float):
                                st.metric(metric, f"{value:.2f}")
                            else:
                                st.metric(metric, value)
                    
                    # Additional analysis
                    st.subheader("Performance Analysis")
                    
                    # Time series of key parameters
                    altitude_cols = [col for col in df.columns if 'altitude' in col.lower() and 'rate' not in col.lower()]
                    speed_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['cas', 'tas', 'speed']) and 'rate' not in col.lower()]
                    
                    if altitude_cols and speed_cols:
                        fig = make_subplots(rows=2, cols=1, 
                                          subplot_titles=('Altitude Profile', 'Speed Profile'),
                                          vertical_spacing=0.1)
                        
                        fig.add_trace(go.Scatter(x=df['Elapsed Time (s)'], y=df[altitude_cols[0]], 
                                               name=altitude_cols[0], line=dict(color='blue')), 
                                     row=1, col=1)
                        
                        fig.add_trace(go.Scatter(x=df['Elapsed Time (s)'], y=df[speed_cols[0]], 
                                               name=speed_cols[0], line=dict(color='red')), 
                                     row=2, col=1)
                        
                        fig.update_xaxes(title_text="Elapsed Time (s)", row=2, col=1)
                        fig.update_yaxes(title_text=altitude_cols[0], row=1, col=1)
                        fig.update_yaxes(title_text=speed_cols[0], row=2, col=1)
                        fig.update_layout(height=600, title="Flight Profile")
                        
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No performance metrics could be calculated from the available data.")
            
            elif analysis_type == "Anomaly Detection":
                st.header("🔍 Anomaly Detection")
                
                # Parameter selection for anomaly detection
                available_params = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col not in ['Elapsed Time (s)']]
                selected_param = st.selectbox("Select parameter for anomaly detection", available_params)
                
                if selected_param:
                    threshold = st.slider("Anomaly threshold (standard deviations)", 1.0, 5.0, 3.0, 0.1)
                    
                    anomalies = detect_anomalies(df, selected_param, threshold)
                    
                    if anomalies.any():
                        st.warning(f"Found {anomalies.sum()} potential anomalies in {selected_param}")
                        
                        # Plot with anomalies highlighted
                        fig = go.Figure()
                        
                        # Normal data
                        normal_mask = ~anomalies
                        fig.add_trace(go.Scatter(
                            x=df.loc[normal_mask, 'Elapsed Time (s)'],
                            y=df.loc[normal_mask, selected_param],
                            mode='lines+markers',
                            name='Normal',
                            line=dict(color='blue'),
                            marker=dict(size=3)
                        ))
                        
                        # Anomalies
                        fig.add_trace(go.Scatter(
                            x=df.loc[anomalies, 'Elapsed Time (s)'],
                            y=df.loc[anomalies, selected_param],
                            mode='markers',
                            name='Anomalies',
                            marker=dict(color='red', size=8, symbol='x')
                        ))
                        
                        fig.update_layout(
                            title=f"Anomaly Detection: {selected_param}",
                            xaxis_title="Elapsed Time (s)",
                            yaxis_title=selected_param,
                            hovermode='closest'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show anomaly details
                        if st.checkbox("Show anomaly details"):
                            anomaly_data = df[anomalies][['Elapsed Time (s)', selected_param]]
                            st.dataframe(anomaly_data)
                    else:
                        st.success(f"No anomalies detected in {selected_param} with threshold {threshold}σ")
                        
                        # Plot normal data
                        fig = px.line(df, x='Elapsed Time (s)', y=selected_param, 
                                    title=f"{selected_param} - No Anomalies Detected")
                        st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Multi-Axis Plot":
                st.header("📊 Multi-Axis Parameter Plot")
                
                st.info("Select parameters with different scales to plot on separate y-axes.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Primary Y-Axis")
                    primary_params = []
                    for category, params in param_categories.items():
                        if params:
                            st.write(f"**{category}:**")
                            for param in params:
                                if st.checkbox(param, key=f"primary_{param}"):
                                    primary_params.append(param)
                
                with col2:
                    st.subheader("Secondary Y-Axis")
                    secondary_params = []
                    for category, params in param_categories.items():
                        if params:
                            st.write(f"**{category}:**")
                            for param in params:
                                if st.checkbox(param, key=f"secondary_{param}"):
                                    secondary_params.append(param)
                
                if primary_params or secondary_params:
                    multi_fig = create_multi_axis_plot(df, primary_params, secondary_params)
                    if multi_fig:
                        st.plotly_chart(multi_fig, use_container_width=True)
                else:
                    st.warning("Please select at least one parameter for either axis.")
                    
            elif analysis_type == "Frequency Analysis":
                st.header("🔊 Frequency Domain Analysis")
                
                # Parameter selection for frequency analysis
                available_params = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col not in ['Elapsed Time (s)', 'Timestamp']]
                selected_param = st.selectbox("Select parameter for frequency analysis", available_params)
                
                if selected_param:
                    sampling_rate = st.number_input("Sampling rate (Hz)", min_value=0.1, value=1.0, step=0.1)
                    
                    freq_fig, dominant_freq = perform_frequency_analysis(df, selected_param, sampling_rate)
                    
                    st.plotly_chart(freq_fig, use_container_width=True)
                    
                    st.info(f"Dominant frequency for {selected_param}: {dominant_freq:.2f} Hz")
                    
                    st.markdown("### Interpretation")
                    st.markdown("""
                    - The frequency spectrum shows how the signal's energy is distributed across different frequencies.
                    - The x-axis represents frequency (in Hz), and the y-axis represents the magnitude of each frequency component.
                    - The dominant frequency is the frequency with the highest magnitude, which often corresponds to the most significant periodic component in the signal.
                    - Lower frequencies represent slower changes in the signal, while higher frequencies represent faster changes.
                    """)
                else:
                    st.warning("Please select a parameter for frequency analysis.")
                        
            # Export functionality
            st.sidebar.header("Export Options")
            if st.sidebar.button("Export Processed Data"):
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.sidebar.download_button(
                    label="Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"processed_flight_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Raw data preview
            with st.expander("Raw Data Preview"):
                st.dataframe(df.head(20))

    except Exception as e:
        st.error(f"An unexpected error occurred: **{e}**")
        with st.expander("Click to see detailed error traceback"):
            st.code(traceback.format_exc())
else:
    st.info("Please upload a flight data file to begin analysis.")
    
    # Sample data format information
    with st.expander("Expected Data Format"):
        st.markdown("""
        **File Format Requirements:**
        - Tab-separated values (.csv or .txt)
        - Two header rows:
          - First row: Parameter names
          - Second row: Units
        - First column: Timestamps in format `day:hour:minute:second.millisecond`
        - Subsequent columns: Numeric flight parameters
        
        **Example:**
        ```
        Description    PARAM1    PARAM2    PARAM3
        EU            DGC       ft        kt
        198:09:40:00.000    38.31    1173    0
        198:09:40:00.100    38.31    1176    0
        ```
        """)

# --- Footer ---
st.markdown("---")
st.markdown("Enhanced Flight Data Analyzer - Advanced flight test data analysis with specialized visualizations")

