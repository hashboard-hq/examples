import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from faker import Faker

# load existing orders file
df_orders = pd.read_parquet('data/sales_data.parquet')
unique_order_ids = df_orders['order_id'].unique()

# initialize random seed and Faker for data generation
np.random.seed(0)
fake = Faker()

df_marketing_attribution = pd.DataFrame({
    'attribution_id': [f'ATTR{i:05}' for i in range(df_orders.shape[0])],
    'order_id': df_orders['order_id'],
    'touchpoint_id': [f'TOUCH{i:05}' for i in np.random.choice(range(1000), size=df_orders.shape[0])],
    'attribution_share': np.random.uniform(0, 1, df_orders.shape[0]),
    'attribution_timestamp': pd.date_range(start='2020-01-01', periods=df_orders.shape[0]),
    'attribution_model': 'Time Decay'
})

# generate marketing_touchpoints data
df_marketing_touchpoints = pd.DataFrame({
    'touchpoint_id': df_marketing_attribution['touchpoint_id'].unique(),
    'customer_id': [f'CUST{i:05}' for i in np.random.choice(range(1000), size=df_marketing_attribution['touchpoint_id'].nunique())],
    'source': np.random.choice(['Google', 'Facebook', 'Instagram', 'Twitter', 'Email'], size=df_marketing_attribution['touchpoint_id'].nunique()),
    'medium': np.random.choice(['cpc', 'organic', 'referral'], size=df_marketing_attribution['touchpoint_id'].nunique()),
    'campaign': np.random.choice([f'Campaign{i:05}' for i in range(100)], size=df_marketing_attribution['touchpoint_id'].nunique()),
    'interaction_timestamp': pd.date_range(start='2020-01-01', periods=df_marketing_attribution['touchpoint_id'].nunique()),
    'touchpoint_value': np.random.uniform(0, 1, df_marketing_attribution['touchpoint_id'].nunique())
})

# generate campaigns data
df_campaigns = pd.DataFrame({
    'campaign_id': df_marketing_touchpoints['campaign'].unique(),
    'campaign_name': [fake.catch_phrase() for _ in range(df_marketing_touchpoints['campaign'].nunique())],
    'campaign_type': np.random.choice(['Email', 'Social Media', 'Search Engine Marketing'], size=df_marketing_touchpoints['campaign'].nunique()),
    'start_date': pd.date_range(start='2020-01-01', periods=df_marketing_touchpoints['campaign'].nunique()),
    'end_date': pd.date_range(start='2020-02-01', periods=df_marketing_touchpoints['campaign'].nunique()),
    'total_budget': np.random.uniform(1000, 5000, df_marketing_touchpoints['campaign'].nunique())
})


# Calculate the number of touchpoints per campaign
touchpoints_per_campaign = df_marketing_touchpoints.groupby('campaign').size().reset_index(name='touchpoint_count')

# Merge with the campaigns dataframe to get the total budget and calculate cost per touchpoint
df_campaigns = pd.merge(df_campaigns, touchpoints_per_campaign, left_on='campaign_id', right_on='campaign')
df_campaigns['cost_per_touchpoint'] = df_campaigns['total_budget'] / df_campaigns['touchpoint_count']

# Merge df_marketing_touchpoints with df_campaigns to get the cost per touchpoint for each touchpoint
df_marketing_touchpoints = pd.merge(df_marketing_touchpoints, df_campaigns[['campaign_id', 'cost_per_touchpoint']], left_on='campaign', right_on='campaign_id', how='left')
# df_marketing_touchpoints.drop('campaign_id', axis=1, inplace=True)


# save to parquet files
df_marketing_attribution.to_parquet('data/marketing_attribution.parquet')
df_marketing_touchpoints.to_parquet('data/marketing_touchpoints.parquet')
df_campaigns.to_parquet('data/campaigns.parquet')