# README.md

## Project Overview
This project implements detailed visualizations of monthly housing prices from 2014 to 2024 and annual housing prices from 2015 to 2025. It uses the provincial capital city as a representative for each province, displaying annual housing prices and change rates on an interactive map.

## Data Description
- **monthly_price.csv**: Contains monthly housing price data for selected cities from 2015 to 2024.
- **yearly_price.csv**: Records annual housing prices and change rates for provincial capitals, special administrative regions, and autonomous regions from 2015 to 2025.

The above datasets are stored in the `housing_price` database under the database instance, in the `monthly_price_for_all` and `yearly_price_for_all` tables respectively. Field names match those in the CSV files.

## Key Code Files
- **app.py**: Main entry point file containing database connections, route configurations, and other core operations.
- **import_data.py**: Script for importing CSV data into the MySQL database.
- **worm.py**: Web scraper code for data collection.

## Disclaimer
This project is intended **for educational purposes only** and uses publicly available information from the internet. The author assumes no responsibility for any misuse, abuse, or unauthorized use of this data by malicious actors.
