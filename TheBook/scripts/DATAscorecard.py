import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# Load the datasets
df_macro = pd.read_csv('LIST_MACRO_INDICATOR_TEST.csv', sep=';', engine='python')
df_mex = pd.read_csv('cleaned_BRA_FINAL_TEST_scorecard.csv', sep=',')  # ensure correct delimiter
df_x_test = pd.read_csv('X_TEST.csv')  # Load X_TEST.csv for Brazil Z-scores

# Merge the macro data with the scorecard data on the symbol to bring in the area and criterion information
df_merged = pd.merge(df_mex, df_macro[['symbol', 'area', 'criterion']], on='symbol', how='left')

# Calculate mean Z-scores and grades for each area
area_scores = df_merged.groupby('area')[['z_score', 'z_score_1y', 'z_score_3y']].mean().reset_index()
area_grades = df_merged.groupby('area')[['z_score_grade', 'z_score_1y_grade', 'z_score_3y_grade']].mean().reset_index()

# Calculate the mean grades for Brazil
overall_grade = area_grades[['z_score_grade']].mean().values[0]
overall_1y_grade = area_grades[['z_score_1y_grade']].mean().values[0]
overall_3y_grade = area_grades[['z_score_3y_grade']].mean().values[0]

# Define criterion_grades and criterion_scores
criterion_grades = df_merged.groupby('criterion')[['z_score_grade', 'z_score_1y_grade', 'z_score_3y_grade']].mean().reset_index()
criterion_scores = df_merged.groupby('criterion')[['z_score', 'z_score_1y', 'z_score_3y']].mean().reset_index()

# Define contribution_grades and contribution_z_scores
contribution_grades = pd.pivot_table(df_merged, values='z_score_grade', index='criterion', columns='area', aggfunc='mean').fillna(0)
contribution_z_scores = pd.pivot_table(df_merged, values='z_score', index='criterion', columns='area', aggfunc='mean').fillna(0)

# Function to create enhanced radar (spider) charts with axis labels and transparent filling
def create_enhanced_radar_chart(categories, values_list, labels, title, colors):
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for values, label, color in zip(values_list, labels, colors):
        values += values[:1]
        ax.fill(angles, values, color=color, alpha=0.1)
        ax.plot(angles, values, color=color, linewidth=2, label=label)
    
    ax.set_yticks([1, 2, 3, 4, 5])  # Ensure fixed ticks for Y axis
    ax.set_yticklabels(range(1, 6), color="grey", size=10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title(title, size=20, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

# Prepare the summary tables for Grades and Z-Scores
summary_table_grades = round(area_grades.copy(),2)
summary_table_z_scores = round(area_scores.copy(),2)

# Generate the PDF report with one visual per page
pdf_file = 'FINAL_Macro_Analysis_Report_with_Brazil_Chart.pdf'
with PdfPages(pdf_file) as pdf:
    # First Page: Country name and grades
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    ax.text(0.5, 0.8, "Country: BRASIL", fontsize=24, ha='center')
    ax.text(0.5, 0.6, f"Mean Grade: {overall_grade:.2f}", fontsize=18, ha='center')
    ax.text(0.5, 0.5, f"1 Year Grade: {overall_1y_grade:.2f}", fontsize=18, ha='center')
    ax.text(0.5, 0.4, f"3 Year Grade: {overall_3y_grade:.2f}", fontsize=18, ha='center')
    ax.text(0.5, 0.2, "Macro Analysis Report", fontsize=16, ha='center')
    pdf.savefig(fig)
    plt.close(fig)
    
    # Summary Table: Grades
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=summary_table_grades.values, colLabels=summary_table_grades.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.5, 1.5)
    ax.set_title("Summary Table of Grades by Area", fontsize=14, fontweight='bold')
    pdf.savefig(fig)
    plt.close(fig)
    
    # Summary Table: Z-Scores
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=summary_table_z_scores.values, colLabels=summary_table_z_scores.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.5, 1.5)
    ax.set_title("Summary Table of Z-Scores by Area", fontsize=14, fontweight='bold')
    pdf.savefig(fig)
    plt.close(fig)

    # Enhanced Radar Chart: Grades at Area Level Over Time
    create_enhanced_radar_chart(
        categories=area_grades['area'].tolist(),
        values_list=[
            area_grades['z_score_grade'].tolist(),
            area_grades['z_score_1y_grade'].tolist(),
            area_grades['z_score_3y_grade'].tolist()
        ],
        labels=['Latest', '1 Year Ago', '3 Years Ago'],
        title='Grades at Area Level Over Time',
        colors=['green', 'orange', 'red']
    )
    pdf.savefig(plt.gcf())
    plt.close()


    # Heatmap: Grades by Criterion Over Time
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(criterion_grades.set_index('criterion'), annot=True, cmap='Greens', cbar=True, linewidths=.5)
    plt.title('Heatmap of Grades by Criterion Over Time')
    plt.yticks(rotation=0)
    pdf.savefig(fig)
    plt.close(fig)

    # Heatmap: Z-Scores by Criterion Over Time
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(criterion_scores.set_index('criterion'), annot=True, cmap='coolwarm', cbar=True, linewidths=.5)
    plt.title('Heatmap of Z-Scores by Criterion Over Time')
    plt.yticks(rotation=0)
    pdf.savefig(fig)
    plt.close(fig)

    # Heatmap: Grade Contributions by Criterion and Area
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(contribution_grades, annot=True, cmap='Greens', cbar=True, linewidths=.5)
    plt.title('Heatmap of Grade Contributions by Criterion and Area')
    plt.yticks(rotation=0)
    pdf.savefig(fig)
    plt.close(fig)

    # Heatmap: Z-Score Contributions by Criterion and Area
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(contribution_z_scores, annot=True, cmap='coolwarm', cbar=True, linewidths=.5)
    plt.title('Heatmap of Z-Score Contributions by Criterion and Area')
    plt.yticks(rotation=0)
    pdf.savefig(fig)
    plt.close(fig)

    # Add Z-scores of the last 5 years for Brazil with selected symbols
    selected_symbols = ['fx_risk_premium', 'fdi', 'gov_money_reserve']  # Example symbols

    # Filter the data for Brazil and the selected symbols
    df_brazil = df_x_test[(df_x_test['country_id'] == 'BRA') & (df_x_test['symbol'].isin(selected_symbols))]

    # Convert the 'timestamp' column to datetime format and sort by date
    df_brazil['timestamp'] = pd.to_datetime(df_brazil['timestamp'])
    df_brazil = df_brazil.sort_values(by='timestamp')

    # Filter data for the last 5 years
    five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)
    df_brazil_last_5_years = df_brazil[df_brazil['timestamp'] >= five_years_ago]

    # Generate the line chart
    fig, ax = plt.subplots(figsize=(10, 6))
    for symbol in selected_symbols:
        df_symbol = df_brazil_last_5_years[df_brazil_last_5_years['symbol'] == symbol]
        ax.plot(df_symbol['timestamp'], df_symbol['z_score'], label=symbol)

    # Set plot details for aesthetics
    ax.set_title('Z-Scores of Selected Symbols in Brazil Over Last 5 Years', fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Z-Score', fontsize=12)
    ax.legend(title='Symbols')
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to the PDF
    pdf.savefig(fig)
    plt.close(fig)

# Confirm that the file is saved
print(f"PDF report saved as: {pdf_file}")
