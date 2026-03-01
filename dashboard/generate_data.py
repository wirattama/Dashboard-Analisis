"""Script to generate dashboard data from E-commerce dataset."""
import pandas as pd
import os

# Path ke dataset: selalu relatif terhadap lokasi script (folder dashboard)
# Berjalan baik dari root proyek (python dashboard/generate_data.py) maupun dari folder dashboard (python generate_data.py)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
BASE_PATH = os.path.join(_PROJECT_ROOT, "data")

orders_df = pd.read_csv(os.path.join(BASE_PATH, "orders_dataset.csv"))
customers_df = pd.read_csv(os.path.join(BASE_PATH, "customers_dataset.csv"))
order_items_df = pd.read_csv(os.path.join(BASE_PATH, "order_items_dataset.csv"))
order_reviews_df = pd.read_csv(os.path.join(BASE_PATH, "order_reviews_dataset.csv"))
products_df = pd.read_csv(os.path.join(BASE_PATH, "products_dataset.csv"))
category_translation_df = pd.read_csv(os.path.join(BASE_PATH, "product_category_name_translation.csv"))
order_payments_df = pd.read_csv(os.path.join(BASE_PATH, "order_payments_dataset.csv"))
geolocation_df = pd.read_csv(os.path.join(BASE_PATH, "geolocation_dataset.csv"))

date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for col in date_cols:
    if col in orders_df.columns:
        orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')

orders_df = orders_df[(orders_df['order_purchase_timestamp'].dt.year >= 2017) & (orders_df['order_purchase_timestamp'].dt.year <= 2018)].copy()
orders_delivered = orders_df[(orders_df['order_status'] == 'delivered') & (orders_df['order_delivered_customer_date'].notna()) & (orders_df['order_estimated_delivery_date'].notna())].copy()
order_reviews_df = order_reviews_df.sort_values('review_creation_date').drop_duplicates(subset='order_id', keep='last')
products_df = products_df.merge(category_translation_df, on='product_category_name', how='left')
products_df['product_category_name_english'] = products_df['product_category_name_english'].fillna('unknown')

# City analysis + geospatial (lat, lng per kota) + rata-rata review
orders_with_city = orders_delivered.merge(
    customers_df[["customer_id", "customer_city", "customer_state"]],
    on="customer_id",
    how="inner",
)
orders_with_city["on_time_delivery"] = (
    orders_with_city["order_delivered_customer_date"]
    <= orders_with_city["order_estimated_delivery_date"]
)
city_analysis = (
    orders_with_city.groupby("customer_city")
    .agg(
        total_orders=("order_id", "nunique"),
        on_time_count=("on_time_delivery", "sum"),
    )
    .reset_index()
)
city_analysis["on_time_pct"] = (
    city_analysis["on_time_count"] / city_analysis["total_orders"] * 100
).round(2)

# Rata-rata review score per kota (berdasarkan order yang punya ulasan)
reviews_with_city = orders_with_city.merge(
    order_reviews_df[["order_id", "review_score"]],
    on="order_id",
    how="left",
)
city_reviews = (
    reviews_with_city.groupby("customer_city")
    .agg(
        avg_review_score=("review_score", "mean"),
        review_count=("review_score", "count"),
    )
    .reset_index()
)
city_analysis = city_analysis.merge(city_reviews, on="customer_city", how="left")

# Hitung koordinat rata-rata per kota dari geolocation
geo_city = (
    geolocation_df.groupby("geolocation_city")
    .agg(
        lat=("geolocation_lat", "mean"),
        lng=("geolocation_lng", "mean"),
    )
    .reset_index()
)
geo_city.rename(columns={"geolocation_city": "customer_city"}, inplace=True)

# Gabungkan koordinat ke city_analysis
city_analysis = city_analysis.merge(geo_city, on="customer_city", how="left")
city_analysis = city_analysis.sort_values("total_orders", ascending=False)

# Category analysis
order_ids_1718 = set(orders_df['order_id'])
order_items_filtered = order_items_df[order_items_df['order_id'].isin(order_ids_1718)]
items_with_category = order_items_filtered.merge(products_df[['product_id', 'product_category_name_english']], on='product_id', how='left')
items_with_category['product_category_name_english'] = items_with_category['product_category_name_english'].fillna('unknown')
order_payments_agg = order_payments_df.groupby('order_id')['payment_value'].sum().reset_index()
order_payments_agg.columns = ['order_id', 'order_value']
order_category = items_with_category.loc[items_with_category.groupby('order_id')['price'].idxmax()][['order_id', 'product_category_name_english']]
orders_with_value = orders_df.merge(order_payments_agg, on='order_id', how='inner')
orders_with_review = orders_with_value.merge(order_reviews_df[['order_id', 'review_score']], on='order_id', how='inner')
category_analysis_df = orders_with_review.merge(order_category, on='order_id', how='inner')
category_analysis = category_analysis_df.groupby('product_category_name_english').agg(avg_review_score=('review_score', 'mean'), avg_order_value=('order_value', 'mean'), order_count=('order_id', 'nunique')).reset_index()
category_analysis = category_analysis[category_analysis['order_count'] >= 50]

# RFM
ref_date = orders_delivered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
rfm_df = orders_delivered.merge(order_payments_df.groupby('order_id')['payment_value'].sum().reset_index(), on='order_id').groupby('customer_id').agg(Recency=('order_purchase_timestamp', lambda x: (ref_date - x.max()).days), Frequency=('order_id', 'nunique'), Monetary=('payment_value', 'sum')).reset_index()
rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], 4, labels=[4,3,2,1])
rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), 4, labels=[1,2,3,4])
def rfm_segment(row):
    if row['R_Score'] >= 3 and row['F_Score'] >= 3 and row['M_Score'] >= 3: return 'Champions'
    elif row['R_Score'] >= 3 and row['F_Score'] <= 2: return 'Potential Loyalists'
    elif row['R_Score'] <= 2 and row['F_Score'] >= 3: return 'At Risk'
    elif row['R_Score'] <= 2 and row['F_Score'] <= 2: return 'Hibernating'
    else: return 'Others'
rfm_df['Segment'] = rfm_df.apply(rfm_segment, axis=1)

os.makedirs(os.path.dirname(__file__), exist_ok=True)
city_analysis.to_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'), index=False)
category_analysis.to_csv(os.path.join(os.path.dirname(__file__), 'category_data.csv'), index=False)
rfm_df.to_csv(os.path.join(os.path.dirname(__file__), 'rfm_data.csv'), index=False)
print('Data saved to dashboard/')
