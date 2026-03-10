import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# Load the original and modified datasets
original_data = pd.read_csv("X_TEST.csv", sep=",")
modified_data = pd.read_csv("consolidatedData_TEST.csv", sep=",")

# Convert the timestamp to datetime format and strip time component
original_data['timestamp'] = pd.to_datetime(original_data['timestamp'], errors='coerce').dt.normalize()
modified_data['timestamp'] = pd.to_datetime(modified_data['timestamp'], errors='coerce').dt.normalize()

# Identify and drop rows with NaT in 'timestamp'
original_data = original_data.dropna(subset=['timestamp'])
modified_data = modified_data.dropna(subset=['timestamp'])

# Filter data to include only from 2019 onwards
original_data = original_data[original_data['timestamp'] >= '2019-01-01']
modified_data = modified_data[modified_data['timestamp'] >= '2019-01-01']

# Define the correct country column name
country = "BRA"
country_column = 'country_id'

# Filter the data for the specified country
original_filtered = original_data[original_data[country_column] == country]
modified_filtered = modified_data[modified_data[country_column] == country]

# Normalize timestamps to date-only (strip time)
original_filtered['timestamp'] = original_filtered['timestamp'].dt.floor('D')
modified_filtered['timestamp'] = modified_filtered['timestamp'].dt.floor('D')

# Find the intersection of timestamps to align the datasets
common_timestamps = original_filtered['timestamp'].isin(modified_filtered['timestamp'])
aligned_original = original_filtered[common_timestamps]
aligned_modified = modified_filtered[modified_filtered['timestamp'].isin(aligned_original['timestamp'])]

# Sort both datasets by timestamp to ensure proper alignment during plotting
aligned_original = aligned_original.sort_values(by='timestamp')
aligned_modified = aligned_modified.sort_values(by='timestamp')

# Function to format the date labels
def format_date(x, pos=None):
    return pd.to_datetime(x).strftime('%Y-%m')

# Function to plot and compare data for a given variable and country
def compare_data(variable, country):
    # Further filter based on the 'symbol' column
    original_var_data = aligned_original[aligned_original['symbol'] == variable]
    modified_var_data = aligned_modified[aligned_modified['symbol'] == variable]
    
    # Plot the original and modified data
    plt.figure(figsize=(14, 8))
    plt.plot(original_var_data['timestamp'], original_var_data['value'], label=f'Original {variable}', 
             color='#1f77b4', linestyle='-', marker='o', markersize=6)
    plt.plot(modified_var_data['timestamp'], modified_var_data['value'], label=f'Modified {variable}', 
             color='#ff7f0e', linestyle='--', marker='x', markersize=6)
    
    plt.xlabel('Date', fontsize=14)
    plt.ylabel(variable, fontsize=14)
    plt.title(f'Comparison of {variable} for {country}', fontsize=16, weight='bold')
    plt.legend(fontsize=12)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    
    # Apply date formatting
    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Change interval for more/less date labels

    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Use a clean default style instead of seaborn-whitegrid
    plt.style.use('ggplot')
    
    plt.show()

# Example usage: compare a specific variable for debugging
variable = 'gov_curr_acc'  # Start with one variable for isolated testing
compare_data(variable, country)

# Print the columns again just to verify
print("Original Data Columns:", original_data.columns)
print("Modified Data Columns:", modified_data.columns)
