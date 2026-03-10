import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# Load the datasets
df_macro = pd.read_csv('LIST_MACRO_INDICATOR_TEST.csv', sep=';', engine='python')
df_mex = pd.read_excel('BRATEST_scorecard3.xlsx')

# Merge the macro data with the scorecard data on the symbol to bring in the area and criterion information
df_merged = pd.merge(df_mex, df_macro[['symbol', 'area', 'criterion']], on='symbol', how='left')

# Calculate mean Z-scores for each area
area_scores = df_merged.groupby('area')[['z_score', 'z_score_1y', 'z_score_3y']].mean().reset_index()

# Define criterion_scores
criterion_scores = df_merged.groupby('criterion')[['z_score', 'z_score_1y', 'z_score_3y']].mean().reset_index()

# Define contribution_z_scores
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
    
    ax.set_yticklabels(range(1, 6), color="grey", size=10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title(title, size=20, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

# Generate the PDF report with one visual per page
with PdfPages('TEST_Enhanced_Macro_Analysis_Report.pdf') as pdf:
    # Summary Table: Z-Scores
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=area_scores.values, colLabels=area_scores.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.5, 1.5)
    ax.set_title("Summary Table of Z-Scores by Area", fontsize=14, fontweight='bold')
    pdf.savefig(fig)
    plt.close(fig)

    # Enhanced Radar Chart: Z-Scores at Area Level Over Time
    create_enhanced_radar_chart(
        categories=area_scores['area'].tolist(),
        values_list=[
            area_scores['z_score'].tolist(),
            area_scores['z_score_1y'].tolist(),
            area_scores['z_score_3y'].tolist()
        ],
        labels=['Latest', '1 Year Ago', '3 Years Ago'],
        title='Z-Scores at Area Level Over Time',
        colors=['blue', 'purple', 'brown']
    )
    pdf.savefig(plt.gcf())
    plt.close()

    # Heatmap: Z-Scores by Criterion Over Time
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(criterion_scores.set_index('criterion'), annot=True, cmap='coolwarm', cbar=True, linewidths=.5)
    plt.title('Heatmap of Z-Scores by Criterion Over Time')
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

output_pdf_path = '/mnt/data/TEST2_Enhanced_Macro_Analysis_Report.pdf'
