import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster

sns.set(style="darkgrid")

# Load data
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    cust = pd.read_csv(os.path.join(base_path, 'customers_dataset.csv'))
    order = pd.read_csv(os.path.join(base_path, 'orders_dataset.csv'))
    order_item = pd.read_csv(os.path.join(base_path, 'order_items_dataset.csv'))
    order_payments = pd.read_csv(os.path.join(base_path, 'order_payments_dataset.csv'))
    geolocation = pd.read_csv(os.path.join(base_path, 'geolocation_dataset.csv'))
    product = pd.read_csv(os.path.join(base_path, 'products_dataset.csv'))
    product_categories = pd.read_csv(os.path.join(base_path, 'product_category_name_translation.csv'))
    return cust, order, order_item, order_payments, geolocation, product, product_categories

cust, order, order_item, order_payments, geolocation, product, product_categories = load_data()

# Page title
st.title('E-Commerce Data Dashboard')

# Convert date columns
order['order_purchase_timestamp'] = pd.to_datetime(order['order_purchase_timestamp'])
latest_date = order['order_purchase_timestamp'].max()

# Section 1: Customer Segments (RFM)
st.header('Customer Segments')

# Calculate RFM Metrics
rfm_df = order.merge(order_payments, on='order_id', how='left').groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
    'order_id': 'count',
    'payment_value': 'sum'
}).reset_index()

rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

# RFM Scores
rfm_df['R'] = pd.qcut(rfm_df['Recency'], q=5, labels=[5, 4, 3, 2, 1])
rfm_df['F'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
rfm_df['M'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])

# Calculate RFM Score
rfm_df['RFM_Score'] = rfm_df['R'].astype(str) + rfm_df['F'].astype(str) + rfm_df['M'].astype(str)

# Define segmentation
def segment_customer(row):
    r = int(row['R'])
    f = int(row['F'])
    m = int(row['M'])

    if r >= 4 and f >= 4 and m >= 4:
        return 'Best customer'
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Loyal Customer'
    elif r >= 2 and f >= 2 and m >= 2:
        return 'Potential Customer'
    else:
        return 'Lost customer'

rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)

# Count the segments
segment_counts = rfm_df['Segment'].value_counts().sort_index()

# Pie chart of customer segments
st.write("Customer Segments Distribution")
fig, ax = plt.subplots(figsize=(15, 15))
wedges, texts, autotexts = ax.pie(segment_counts.values, 
                                  labels=segment_counts.index, 
                                  autopct=lambda p: f'{p:.1f}%\n({int(p*sum(segment_counts)/100)})',
                                  startangle=90, textprops=dict(fontsize=20))  # Increased font size

ax.axis('equal')
plt.setp(autotexts, size=12, weight="bold")  # Adjusting the percentage label font size
plt.legend(title="Segments", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.title('Customer Segments', size=16)
st.pyplot(fig)

# Section 2: Geospatial Analysis
st.header('Customer Geospatial Distribution')

# Merge geolocation data
geo_df = pd.merge(
    cust[['customer_zip_code_prefix', 'customer_city', 'customer_state']],
    geolocation[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']],
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='inner'
)

# Sample the data to reduce size 
sampled_geo_df = geo_df.sample(n=200, random_state=42)

# Visualize with Folium (using the sampled data)
st.write("Customer Geolocation Map (Sampled Data)")
locations = sampled_geo_df[['geolocation_lat', 'geolocation_lng']].dropna().values.tolist()

# Use clustering to optimize rendering
m = folium.Map(location=[-14.235, -51.925], zoom_start=3, width="100%", height="100%")
folium.TileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                 attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(m)
FastMarkerCluster(data=locations).add_to(m)
st_folium(m)

# Section 3: Sales Analysis
st.header('Sales Analysis')

# Average yearly sales
order['year'] = order['order_purchase_timestamp'].dt.year
yearly_avg = order.merge(order_item, on='order_id', how='left').groupby('year')['price'].mean().reset_index()
yearly_avg.columns = ['year', 'average_purchase']
yearly_avg['percentage_change'] = yearly_avg['average_purchase'].pct_change() * 100

# Bar chart of yearly sales
st.write("Average Yearly Sales")
fig, ax = plt.subplots(figsize=(15, 6))
ax.bar(yearly_avg['year'], yearly_avg['average_purchase'])
ax.set_title('Average Yearly Sales')
ax.set_xlabel('Year')
ax.set_ylabel('Average Purchase Amount')
for i, v in enumerate(yearly_avg['average_purchase']):
    ax.text(yearly_avg['year'][i], v, f'{v:.2f}', ha='center', va='bottom')
st.pyplot(fig)


# Merge customer data with order data
customer_order_df = pd.merge(cust, order, on='customer_id')

# Merge with order items data to get product information
customer_order_product_df = pd.merge(customer_order_df, order_item, on='order_id')

# Group by customer state and product category, then count unique orders
state_product_counts = customer_order_product_df.groupby(['customer_state', 'product_id']).agg({
    'order_id': 'nunique',
    'price': 'mean'
}).reset_index()


# Merge product categories with state_product_counts
state_product_counts = pd.merge(state_product_counts, product[['product_id', 'product_category_name']], on='product_id')
state_product_counts = pd.merge(state_product_counts, product_categories, on='product_category_name', how='left')
top_categories_by_state = state_product_counts.loc[state_product_counts.groupby('customer_state')['order_id'].idxmax()]
top_categories_by_state = top_categories_by_state.sort_values('order_id', ascending=False)

# Streamlit section for Top Product Categories by State
st.write("Top Product Categories by State")
top_5_categories_by_state = top_categories_by_state.nlargest(5, 'order_id')
# Visualize top product categories by state in Streamlit
fig, ax = plt.subplots(figsize=(15, 8)) 
sns.barplot(data=top_5_categories_by_state, 
            x='order_id', 
            y='customer_state', 
            hue='product_category_name_english', 
            ax=ax, 
            dodge=False)
# Add labels and title
ax.set_title('Top 5 Product Categories by State')
ax.set_xlabel('Number of Orders')
ax.set_ylabel('State')
st.pyplot(fig)


# Section 4: Shipping Analysis
st.header('Shipping Analysis')

# Calculate average shipping time by state
order_item['shipping_limit_date'] = pd.to_datetime(order_item['shipping_limit_date'])
shipping_df = order.merge(order_item, on='order_id', how='left').merge(cust[['customer_id', 'customer_state']], on='customer_id', how='left')
shipping_df = shipping_df.groupby('customer_state')['shipping_limit_date'].apply(lambda x: (x.max() - x.min()).days).reset_index()
shipping_df.columns = ['customer_state', 'shipping_time']

# Bar chart for shipping times
st.write("Average Shipping Time by State")
fig, ax = plt.subplots(figsize=(15, 8))
sns.barplot(x='customer_state', y='shipping_time', data=shipping_df, ax=ax)
ax.set_title('Average Shipping Time by State')
ax.set_xlabel('State')
ax.set_ylabel('Average Shipping Time (days)')
plt.xticks(rotation=90)
st.pyplot(fig)
