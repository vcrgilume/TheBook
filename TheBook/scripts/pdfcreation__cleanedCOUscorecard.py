'5'

import pandas as pd


# Load the dataset
df = pd.read_excel('BRATEST_scorecard3.xlsx', sheet_name='BRA')

# Print the available columns to diagnose the issue
print("Available columns:", df.columns)

# Strip any leading or trailing spaces from column names
df.columns = df.columns.str.strip()


# Clean data: Remove spaces, replace ',' with '.' for decimal numbers
df.columns = df.columns.str.strip()
df.replace({',': '.'}, regex=True, inplace=True)

# Ensure numeric columns are correctly parsed
df[['z_score', 'z_score_1y', 'z_score_3y']] = df[['z_score', 'z_score_1y', 'z_score_3y']].apply(pd.to_numeric, errors='coerce')


# Define a function to assign grades based on Z-scores
def assign_grade(z_score, scale="1_to_6"):
    if scale == "0_to_5":
        if z_score <= -2: return 0
        elif -2 < z_score <= -1: return 1
        elif -1 < z_score <= 0: return 2
        elif 0 < z_score <= 1: return 3
        elif 1 < z_score <= 2: return 4
        else: return 5

# Apply the grading function to criterion level Z-scores
df['z_score_grade'] = df['z_score'].apply(lambda x: assign_grade(x, scale="1_to_6"))
df['z_score_1y_grade'] = df['z_score_1y'].apply(lambda x: assign_grade(x, scale="1_to_6"))
df['z_score_3y_grade'] = df['z_score_3y'].apply(lambda x: assign_grade(x, scale="1_to_6"))

# Save the cleaned and processed DataFrame to a CSV file
df.to_csv('cleaned_BRA_scorecardFINAL.csv', index=False)