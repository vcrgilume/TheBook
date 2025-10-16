'DATA'
'2'
import pandas as pd
import numpy as np

# Step 1: Load the data and manually set the column names
df = pd.read_csv("ExtractAPItacsPRINT.csv", sep=',')
df.columns = ['timestamp', 'value', 'country_id', 'symbol']

# Convert the timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d', errors='coerce')

# Step 2: Generate a missing data report
missing_data_report = df.isnull().groupby(['country_id', 'symbol']).sum()
missing_data_count = missing_data_report['value']

# Print the missing data report
print("Missing Data Report:")
print(missing_data_count[missing_data_count > 0])

# Step 3: Fill missing data
def custom_fill(group):
    before_2003 = group['timestamp'] < pd.Timestamp('2003-01-01')
    after_2023 = group['timestamp'] > pd.Timestamp('2023-01-01')
    
    # Apply backward fill for data before 2003
    group.loc[before_2003, 'value'] = group.loc[before_2003, 'value'].bfill()
    
    # Apply forward fill for data after 2023
    group.loc[after_2023, 'value'] = group.loc[after_2023, 'value'].ffill()
    
    return group

df = df.groupby(['country_id', 'symbol'], group_keys=False).apply(custom_fill)

# Function to identify and replace redundant data
def replace_redundant_data(group):
    group = group.sort_values(by='timestamp').drop_duplicates()
    year_groups = group.groupby(group['timestamp'].dt.year)

    for year, year_data in year_groups:
        if len(year_data) == 12:
            unique_values = year_data['value'].nunique()

            if unique_values == 1:  # All 12 months have the same value (Yearly replication)
                start_value = year_data['value'].iloc[0]
                if year + 1 in year_groups.groups:
                    end_value = group.loc[year_groups.groups[year + 1][0], 'value']
                else:
                    end_value = start_value
                
                # Interpolate February to December
                interpolated_values = np.linspace(start_value, end_value, num=12)
                group.loc[year_data.index[:11], 'value'] = interpolated_values[:11]
                
                # Use January value of the current year for December
                group.loc[year_data.index[11], 'value'] = interpolated_values[11]

            # Check for quarterly replication
            elif unique_values == 4:
                is_quarterly = True
                for i in range(0, 12, 3):
                    if year_data['value'].iloc[i] != year_data['value'].iloc[i+1] or year_data['value'].iloc[i] != year_data['value'].iloc[i+2]:
                        is_quarterly = False
                        break
                
                if is_quarterly:
                    for i in range(0, 12, 3):
                        start_value = year_data['value'].iloc[i]
                        if i == 9 and year + 1 in year_groups.groups:
                            end_value = group.loc[year_groups.groups[year + 1][0], 'value']
                            group.loc[year_data.index[i:i+3], 'value'] = np.linspace(start_value, end_value, num=4)[:3]
                        elif i<9:
                            end_value = year_data['value'].iloc[i+3]
                            group.loc[year_data.index[i:i+4], 'value'] = np.linspace(start_value, end_value, num=4)
                        else:
                            break
                    
            # Check for bi-annual replication
            elif unique_values == 2:
                is_bianual = True
                for i in range(0, 12, 6):
                    if year_data['value'].iloc[i] != year_data['value'].iloc[i+1] or year_data['value'].iloc[i] != year_data['value'].iloc[i+2] or year_data['value'].iloc[i] != year_data['value'].iloc[i+3] or year_data['value'].iloc[i] != year_data['value'].iloc[i+4]:
                        is_bianual = False
                        break
                
                if is_bianual:
                    for i in range(0, 12, 6):
                        start_value = year_data['value'].iloc[i]
                        if i == 6 and year + 1 in year_groups.groups:
                            end_value = group.loc[year_groups.groups[year + 1][0], 'value']
                            group.loc[year_data.index[i:i+5], 'value'] = np.linspace(start_value, end_value, num=6)[:5]
                        elif i<6:
                            end_value = year_data['value'].iloc[i+3]
                            group.loc[year_data.index[i:i+6], 'value'] = np.linspace(start_value, end_value, num=6)
                        else:
                            break
        
                    

    return group

# Apply the function to each country_id and symbol
df = df.groupby(['country_id', 'symbol'], group_keys=False).apply(replace_redundant_data)

# Save the processed data to a single output file
df.to_csv("CONSOLIDATED_DATASET_TEST.csv", index=False)

print("Processed data saved successfully.")
