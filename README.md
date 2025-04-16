# Smart Lamp Market Analysis

## Overview

This project analyzes potential European markets for a smart night lamp that connects to hotel smart networks, allowing guests to control the lamp using their smart TV remote. The analysis combines two Eurostat datasets to identify the most promising national markets for initial product launch.

## Data Sources

The analysis uses two Eurostat datasets from 2016:

1. **TOUR_CAP_NAT**: Number of establishments, bedrooms and bed-places
   - Filtered for "BEDPL" (bed-places), "NR" (number), "I551" (hotels), and year 2016

2. **isoc_ci_dev_i**: Devices used to access the internet
   - Filtered for "IND_TOTAL" (all individuals), "I_IUG_TV" (smart TV usage), "PC_IND" (percentage of individuals), and year 2016

Special data handling:
- Missing values (":") were excluded
- Unreliable data (OBS_FLAG containing "u" or "bu") was removed
- EU/EA aggregate codes were excluded

## Project Structure

```
├── input_data/
│   ├── estat_isoc_ci_dev_i_en.csv
│   └── estat_tour_cap_nat_en.csv
├── output_data/
│   ├── geo_beds_tv_df.csv
│   ├── market_segmentation.png
│   ├── market_share_pie.png
│   └── top_5_market_size.png
├── app.py
└── README.txt
```

## Methodology

The project follows these steps:

1. **Data Loading and Cleaning**:
   - Loads both datasets and filters according to specified criteria
   - Removes missing values and unreliable data
   - Excludes EU/EA aggregate codes

2. **Data Merging**:
   - Combines the datasets on country code ("geo")
   - Creates a dataset with three columns: "Country Code", "Number of Bed-places", "Percentage of individuals"

3. **Market Size Calculation**:
   - Calculates estimated market size as: (Percentage of individuals with smart TVs / 100) × Number of hotel bed-places
   - Ranks countries by market size potential

4. **Visualization**:
   - Creates three visualizations to help identify target markets:
     1. Market Share Distribution (pie chart)
     2. Top 5 Markets by Size (bar chart)
     3. Market Segmentation (scatter plot with clustering)

## Visualizations

The project creates three visualizations:

1. **Market Share Pie Chart**: Shows the relative market share distribution among the top 5 countries
2. **Top 5 Markets Bar Chart**: Highlights the countries with the largest estimated market potential
3. **Market Segmentation Scatter Plot**: Visualizes countries based on hotel capacity and smart TV adoption rates, grouped into three market segments:
   - Primary Target Markets (High-High) ---> main target of our assignment.
   - Secondary Target Markets (High-Low)
   - Markets to Avoid Initially (Low-Low)

## Assumptions taken during analysis
- The "% of individuals" is the share of the general population who use a TV to access the internet, not specifically hotel guests. This assumes hotel guests are similar to the general population in their tech habits.
- Bed-places ≠ Unique Guests: "Bed-places" is the number of beds available, not the number of guests per year. Actual guest numbers could be higher (if beds are used by multiple guests per year) or lower (if occupancy is low).
- Not All Guests Will Use the Feature: Even if someone uses a smart TV at home, they may not use it in a hotel.
- Market Size Estimate: This calculation gives you a relative market size for comparison between countries.
- Removed some countries data for simplicity. 
- Assumed that "b" value is also not reliable. 
