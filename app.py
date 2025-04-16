import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def ensure_directory_exists(directory_path):
    """
    Check if directory exists and create it if it doesn't
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def remove_if_exists(file_path):
    """
    Remove file if it exists to avoid duplicates
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed existing file: {file_path}")

def load_and_process_data():
    """
    Load and process the datasets according to the assignment requirements
    """
    # Load the datasets
    tv_df = pd.read_csv("input_data/estat_isoc_ci_dev_i_en.csv")
    beds_df = pd.read_csv("input_data/estat_tour_cap_nat_en.csv")
    
    # Process beds dataset
    beds_df = beds_df[['geo','TIME_PERIOD','accomunit', 'unit', 'nace_r2','OBS_VALUE', 'OBS_FLAG']]
    
    # Filter beds data
    beds_df_2016 = beds_df[(beds_df['accomunit'] == 'BEDPL') & 
                           (beds_df['unit'] == 'NR') & 
                           (beds_df['nace_r2'] == 'I551') & 
                           (beds_df['TIME_PERIOD'] == 2016)]
    
    # Clean beds data
    beds_df_2016 = beds_df_2016[~beds_df_2016['geo'].str.contains('EA|EU')]
    beds_df_2016['OBS_VALUE'] = beds_df_2016['OBS_VALUE'].replace(':', np.nan).astype(float)
    beds_df_2016 = beds_df_2016.dropna(subset=['OBS_VALUE'])
    beds_df_2016 = beds_df_2016[~beds_df_2016['geo'].str.contains('u|bu')]
    
    # Process TV dataset
    tv_df = tv_df[['geo','ind_type','indic_is', 'unit', 'TIME_PERIOD','OBS_VALUE', 'OBS_FLAG']]
    
    # Filter TV data
    tv_df_2016 = tv_df[(tv_df['ind_type'] == 'IND_TOTAL') & 
                       (tv_df['indic_is'] == 'I_IUG_TV') & 
                       (tv_df['unit'] == 'PC_IND') & 
                       (tv_df['TIME_PERIOD'] == 2016)]
    
    # Clean TV data
    tv_df_2016 = tv_df_2016[~tv_df_2016['geo'].str.contains('EA|EU')]
    tv_df_2016 = tv_df_2016[~tv_df_2016['OBS_FLAG'].isin(['u', 'bu', 'b'])]
    
    # Merge datasets
    geo_merged = pd.merge(beds_df_2016, tv_df_2016, on='geo', how='left', suffixes=('_beds', '_device'))
    geo_merged = geo_merged[['geo', 'OBS_VALUE_beds', 'OBS_VALUE_device']]
    geo_merged.columns = ['Country Code', 'Number of Bed-places', 'Percentage of individuals']
    
    # Remove rows with missing TV data
    geo_merged = geo_merged.dropna(subset=['Percentage of individuals'])
    
    return geo_merged

def calculate_market_size(df):
    """
    Calculate estimated market size and rank countries
    """
    df['Estimated Market Size'] = (df['Percentage of individuals'] / 100) * df['Number of Bed-places']
    df_sorted = df.sort_values(by='Estimated Market Size', ascending=False)
    df_sorted['Market Size Rank'] = range(1, len(df_sorted) + 1)
    return df_sorted

def create_visualizations(df):
    """
    Create visualizations in the specified order:
    1. Market share pie (no clustering)
    2. Top 5 markets (no clustering)
    3. Clusters scatter plot (with clustering)
    """
    output_dir = 'output_data'
    ensure_directory_exists(output_dir)
    
    # Clean up any existing visualization files
    visualization_files = [
        f"{output_dir}/market_share_pie.png",
        f"{output_dir}/top_5_market_size.png",
        f"{output_dir}/market_segmentation.png"
    ]
    
    for file_path in visualization_files:
        remove_if_exists(file_path)
    
    # Visualization 1: Market Share Pie Chart (no clustering)
    plt.figure(figsize=(10, 8))
    plt.pie(df.sort_values(by='Estimated Market Size', ascending=False).head(10)['Estimated Market Size'], 
            labels=df.sort_values(by='Estimated Market Size', ascending=False).head(10)['Country Code'], 
            autopct='%1.1f%%',
            startangle=90,
            shadow=True)
    plt.title('Market Share Distribution by Country')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/market_share_pie.png')
    plt.close()
    
    # Visualization 2: Bar chart of top 5 countries by estimated market size (no clustering)
    top_5 = df.sort_values(by='Estimated Market Size', ascending=False).head(5)
    plt.figure(figsize=(12, 8))
    bars = plt.bar(top_5['Country Code'], top_5['Estimated Market Size'], color='skyblue')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5000,
                f'{int(height):,}',
                ha='center', va='bottom', rotation=0)
    
    plt.title('Top 5 Countries by Estimated Market Size', fontsize=14)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Estimated Market Size (Bed-places × % of individuals)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_5_market_size.png')
    plt.close()
    
    # Now perform clustering for Visualization 3
    # Prepare data for clustering
    cluster_data = df[['Number of Bed-places', 'Percentage of individuals']]
    
    # Scale the data
    scaler = StandardScaler()
    scaled_cluster_data = scaler.fit_transform(cluster_data)
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(scaled_cluster_data)
    
    # Create cluster labels dictionary for interpretation
    cluster_labels = {
        0: 'Low-Low (Avoid Initially)',
        1: 'High-Low (Secondary Target)',
        2: 'High-High (Primary Target)'
    }
    
    # Map cluster numbers to descriptive labels
    df['Cluster Label'] = df['Cluster'].map(cluster_labels)
    
    # Visualization 3: Scatter plot with clusters
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df['Number of Bed-places'], 
                         df['Percentage of individuals'], 
                         s=df['Number of Bed-places']/10000, 
                         c=df['Cluster'],
                         cmap='viridis',
                         alpha=0.7)
    
    # Add country labels
    for i, row in df.iterrows():
        plt.annotate(row['Country Code'], 
                    (row['Number of Bed-places'], row['Percentage of individuals']),
                    xytext=(5, 5), 
                    textcoords='offset points')
    
    # Add legend for clusters
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=scatter.cmap(scatter.norm(i)), 
                                 markersize=10, label=label) 
                      for i, label in cluster_labels.items()]
    
    plt.legend(handles=legend_elements, title='Market Segments', loc='upper right')
    plt.title('Relationship between Hotel Capacity and Smart TV Adoption\nwith Market Segmentation', fontsize=14)
    plt.xlabel('Number of Bed-places', fontsize=12)
    plt.ylabel('Percentage of individuals using Smart TV', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/market_segmentation.png')
    plt.close()
    
    # Print cluster analysis summary
    cluster_summary = df.groupby('Cluster')[['Number of Bed-places', 'Percentage of individuals', 'Estimated Market Size']].mean()
    cluster_summary['Countries'] = df.groupby('Cluster')['Country Code'].apply(list)
    print("\n=== CLUSTER ANALYSIS SUMMARY ===")
    for cluster, row in cluster_summary.iterrows():
        print(f"\nCluster {cluster} - {cluster_labels[cluster]}:")
        print(f"  Average Bed-places: {row['Number of Bed-places']:.2f}")
        print(f"  Average Smart TV %: {row['Percentage of individuals']:.2f}%")
        print(f"  Average Market Size: {row['Estimated Market Size']:.2f}")
        print(f"  Countries: {', '.join(row['Countries'])}")

def main():
    """
    Main function to execute the data processing and visualization
    """
    print("Loading and processing data...")
    merged_data = load_and_process_data()
    # Ensure output directory exists
    ensure_directory_exists('output_data')
    
    print("Saving merged data to CSV...")
    # Check if the file already exists and remove it
    csv_file_path = 'output_data/geo_beds_tv_df.csv'
    remove_if_exists(csv_file_path)
    
    # Save only the required columns to CSV (exclude Estimated Market Size)
    merged_data.to_csv(csv_file_path, index=False)
    
    print("Calculating market size...")
    ranked_data = calculate_market_size(merged_data)
    
    print("Creating visualizations with clustering analysis...")
    create_visualizations(ranked_data)
    
    print("Analysis complete! Results saved to output_data folder.")
    print("The visualizations have been created in the requested order: 1) Market share pie, 2) Top 5 markets, 3) Clusters scatter plot")

if __name__ == "__main__":
    main()
