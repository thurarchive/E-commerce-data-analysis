# E-commerce Data Analysis and Geospatial Dashboard by Fajri Fathur Rahman✨

## Project Overview
This project focuses on analyzing e-commerce data to understand customer behavior, product preferences, and regional purchasing trends. We use a combination of customer, order, and product data to explore purchasing patterns across different regions of Brazil. Additionally, we visualize the geospatial distribution of orders and the most popular product categories by state.

Key features of this project include:
- Merging customer, order, and product data for comprehensive analysis
- Exploratory Data Analysis (EDA) to identify key trends and insights
- Geospatial visualization using Folium to map customer distribution
- Interactive dashboard showcasing key metrics and regional product preferences

The project utilizes Python for data analysis and Streamlit for creating an interactive dashboard.

## Project Objectives
- **Customer Segmentation**: Analyze purchasing behavior to segment customers.
- **Geospatial Analysis**: Visualize customer distribution and regional trends.
- **Top Product Categories**: Identify the most popular product categories by state.
- **Dashboard**: Present an interactive dashboard with key findings.

## Setup Environment - Anaconda

To set up the environment using Anaconda, follow these steps:

1. **Create and activate a new Conda environment:**
    ```sh
    conda create --name ecommerce-analysis python=3.9
    conda activate ecommerce-analysis
    ```

2. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

## Setup Environment - Shell/Terminal

Alternatively, if you prefer to use Shell or Terminal, follow these instructions:

1. **Create and navigate to the project directory:**
    ```sh
    mkdir ecommerce_data_analysis
    cd ecommerce_data_analysis
    ```

2. **Install Pipenv and create a virtual environment:**
    ```sh
    pipenv install
    pipenv shell
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

## Run Streamlit App

Once your environment is set up and dependencies are installed, you can run the Streamlit app with the following command:

```sh
cd Dashboard
streamlit run dashboard.py
