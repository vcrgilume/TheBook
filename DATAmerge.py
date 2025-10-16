'MERGE'
'3'
import pandas as pd

# Load the CSV files with the correct delimiters
cds_em = pd.read_csv('CDS EM.csv', delimiter=';')
out_test = pd.read_csv('CONSOLIDATED_DATASET_TEST.csv')
spread_yield_em = pd.read_csv('SPREAD YIELD EM.csv', delimiter=';')


# Convert the 'value' column to numeric in the SPREAD & YIELD EM file, forcing errors to NaN for inspection
spread_yield_em['value'] = pd.to_numeric(spread_yield_em['value'], errors='coerce')

# Merging the three datasets
merged_data = pd.concat([spread_yield_em,cds_em, out_test], ignore_index=True)

# Display the merged dataset structure to ensure everything is correct
print(merged_data.info())
print(merged_data.head())

# Save the processed data to a single output file
merged_data.to_csv("consolidatedData_TEST.csv", index=False)

