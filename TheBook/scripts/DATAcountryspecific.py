import pandas as pd

# Load the dataset with the computed Z-scores
df = pd.read_csv('X_TEST.csv')

# Load the CSV file with the list of countries, specifying the correct delimiter
countries_list = pd.read_csv('LIST_COUNTRIES.csv', delimiter=';')

# Check if the 'country_id' column exists
if 'country_id' not in countries_list.columns:
    raise KeyError("'country_id' column not found in LIST_COUNTRIES.csv")

# Convert the 'timestamp' column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort the data by country_id, symbol, and timestamp
df.sort_values(by=['country_id', 'symbol', 'timestamp'], inplace=True)

# Step 1: Calculate rolling Z-scores
window_1y = 12
window_3y = 36

# Calculate rolling means and standard deviations for 1y and 3y windows
df['rolling_mean_1y'] = df.groupby(['country_id', 'symbol'])['z_score'].transform(lambda x: x.rolling(window=window_1y, min_periods=1).mean())
df['rolling_std_1y'] = df.groupby(['country_id', 'symbol'])['z_score'].transform(lambda x: x.rolling(window=window_1y, min_periods=1).std())

df['rolling_mean_3y'] = df.groupby(['country_id', 'symbol'])['z_score'].transform(lambda x: x.rolling(window=window_3y, min_periods=1).mean())
df['rolling_std_3y'] = df.groupby(['country_id', 'symbol'])['z_score'].transform(lambda x: x.rolling(window=window_3y, min_periods=1).std())

df['z_score_1y'] = (df['z_score'] - df['rolling_mean_1y']) / df['rolling_std_1y']
df['z_score_3y'] = (df['z_score'] - df['rolling_mean_3y']) / df['rolling_std_3y']

# Step 2: Filter data for a specific country
def filter_country_data(df, country_id):
    return df[df['country_id'] == country_id]

# Step 3: Aggregate Z-scores by Symbol (latest z_score, mean of z_score_1y and z_score_3y)
def aggregate_by_symbol(country_data):
    country_data = country_data.sort_values(by='timestamp')
    return country_data.groupby(['symbol']).agg({
        'z_score': 'last',       # Latest z_score
        'z_score_1y': 'mean',    # Mean of z_score_1y
        'z_score_3y': 'mean'     # Mean of z_score_3y
    }).reset_index()

# Step 4: Aggregate Z-scores by Criterion
def aggregate_by_criterion(country_data):
    if 'criterion' in country_data.columns:
        return country_data.groupby(['criterion']).agg({
            'z_score': 'last',
            'z_score_1y': 'mean',
            'z_score_3y': 'mean'
        }).reset_index()
    else:
        return pd.DataFrame()  # Return an empty DataFrame if 'criterion' column is missing

# Step 5: Aggregate Z-scores by Area
def aggregate_by_area(country_data):
    if 'area' in country_data.columns:
        return country_data.groupby(['area']).agg({
            'z_score': 'last',
            'z_score_1y': 'mean',
            'z_score_3y': 'mean'
        }).reset_index()
    else:
        return pd.DataFrame()  # Return an empty DataFrame if 'area' column is missing

# Step 6: Create a complete scorecard for a country
def create_country_scorecard(df, country_id):
    country_data = filter_country_data(df, country_id)
    
    # Check if z_score_1y and z_score_3y columns are present
    if 'z_score_1y' not in country_data.columns or 'z_score_3y' not in country_data.columns:
        raise KeyError(f"Missing columns in the data for country {country_id}. Ensure that z_score_1y and z_score_3y are calculated.")

    # Layer 1: Symbol level
    symbol_scores = aggregate_by_symbol(country_data)
    
    # Layer 2: Criterion level
    criterion_scores = aggregate_by_criterion(country_data)
    
    # Layer 3: Area level
    area_scores = aggregate_by_area(country_data)
    
    # Combine the layers into a single DataFrame for the scorecard
    scorecard = {
        'Symbol Scores': symbol_scores,
        'Criterion Scores': criterion_scores,
        'Area Scores': area_scores
    }
    
    return scorecard

# Loop over each country in the list
for country in countries_list['country_id']:
    
    # Create a scorecard for the country
    country_scorecard = create_country_scorecard(df, country)
    
    # Access different levels of the scorecard
    symbol_scores_df = country_scorecard['Symbol Scores']
    criterion_scores_df = country_scorecard['Criterion Scores']
    area_scores_df = country_scorecard['Area Scores']
    
    # Create a single sheet for each country
    with pd.ExcelWriter(f'{country}TEST_scorecard3.xlsx') as writer:
        start_row = 0
        symbol_scores_df.to_excel(writer, sheet_name=country, startrow=start_row, index=False)
        start_row += len(symbol_scores_df)  # Leave a couple of rows as space
        criterion_scores_df.to_excel(writer, sheet_name=country, startrow=start_row, index=False)
        start_row += len(criterion_scores_df)  # Leave a couple of rows as space
        area_scores_df.to_excel(writer, sheet_name=country, startrow=start_row, index=False)
    
    # Print a confirmation message
    print(f"Scorecard for {country} has been generated and saved.")
