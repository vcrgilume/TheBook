'4'

import pandas as pd
import numpy as np
from scipy.stats import zscore

# Load the data
data = pd.read_csv("consolidatedData_TEST.csv")
macroindicators_data = pd.read_csv("LIST_MACRO_INDICATOR_TEST.csv", delimiter=';')

# Merge the main dataset with the macroindicators data to match each indicator with its type
merged_data = pd.merge(data, macroindicators_data[['symbol', 'type']], on='symbol', how='left')

# Check if the 'type' column is present after merging
if 'type' not in merged_data.columns:
    raise KeyError("The 'type' column is missing after the merge. Check the merge operation.")

# Filter the dataset to include only rows where `value` is non-missing
filtered_data = merged_data.dropna(subset=['value'])

# 1. Winsorisation within groups
def apply_winsorisation_within_group(group, lower_percentile=2.5, upper_percentile=97.5):
    if group['type'].iloc[0] == 'A':
        cap_value = np.percentile(group['value'].dropna(), upper_percentile)
        group['winsorised_value'] = np.minimum(group['value'], cap_value)
    elif group['type'].iloc[0] == 'B':
        cap_value = np.percentile(group['value'].dropna(), lower_percentile)
        group['winsorised_value'] = np.maximum(group['value'], cap_value)
    elif group['type'].iloc[0] == 'C':
        lower_cap = np.percentile(group['value'].dropna(), lower_percentile)
        upper_cap = np.percentile(group['value'].dropna(), upper_percentile)
        group['winsorised_value'] = np.clip(group['value'], lower_cap, upper_cap)
    else:
        group['winsorised_value'] = group['value']
    return group

# Apply winsorisation within each indicator-country group
filtered_data = filtered_data.groupby(['symbol', 'country_id'], group_keys=False).apply(apply_winsorisation_within_group)

# Reset index to avoid ambiguity between index levels and column labels
filtered_data = filtered_data.reset_index(drop=True)

# 2. Standardisation (Z-score)
def calculate_z_score(group):
    if group['winsorised_value'].std(ddof=1) == 0:
        group['z_score'] = np.nan  # or another default value
    else:
        group['z_score'] = (group['winsorised_value'] - group['winsorised_value'].mean()) / group['winsorised_value'].std(ddof=1)
    return group

filtered_data = filtered_data.groupby(['country_id','symbol'], group_keys=False).apply(calculate_z_score)

# 3. Normalisation
def normalize_scores(group):
    if group['z_score'].max() != group['z_score'].min():
        group['normalized_score'] = (group['z_score'] - group['z_score'].min()) / (group['z_score'].max() - group['z_score'].min()) * 100
    else:
        group['normalized_score'] = 50  # or another default value
    return group

filtered_data = filtered_data.groupby(['symbol', 'country_id'], group_keys=False).apply(normalize_scores)

# 4. Dilation
def dilate_scores(group):
    if group['normalized_score'].max() != group['normalized_score'].min():
        group['dilated_score'] = (group['normalized_score'] - group['normalized_score'].min()) / (group['normalized_score'].max() - group['normalized_score'].min()) * 100
    else:
        group['dilated_score'] = group['normalized_score']
    return group

filtered_data = filtered_data.groupby(['symbol', 'country_id'], group_keys=False).apply(dilate_scores)

# 5. Smoothing
alpha = 0.5  # Smoothing factor
filtered_data['smoothed_score'] = filtered_data.groupby(['symbol', 'country_id'])['dilated_score'].transform(
    lambda x: x.ewm(alpha=alpha).mean()
)

# Display the first few rows to check the results
print(filtered_data[['timestamp', 'symbol', 'country_id', 'value', 'winsorised_value', 'z_score', 'normalized_score', 'dilated_score', 'smoothed_score']].head())
filtered_data.to_csv("TESTF.csv", index=False)

test_data = pd.read_csv("TESTF.csv")

# Merge the datasets on the 'symbol' column
merged_data = pd.merge(test_data, macroindicators_data[['symbol', 'area', 'criterion']], on='symbol', how='left')

# Now that you have the merged data, you can filter for a specific country or proceed with further analysis as needed.
merged_data.head()

merged_data.to_csv("X_TEST.csv", index=False)
