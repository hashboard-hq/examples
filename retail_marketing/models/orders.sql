select 
  timestamp_seconds(cast(timestamp/1000000000 as int)) as timestamp,
  order_id as id,
  payment_method,
  delivery,
  type,
  customer_id,
  sum(item_price) as total_order_value,
  any_value(loyalty_status) as loyalty_status,
  any_value(discount_code) as discount_code,
  any_value(feedback_rating) as feedback_rating,
  any_value(delivery_time) as delivery_time,
  any_value(preparation_time) as preparation_time,
  -- any_value(allergens) as allergens, -- array type
  any_value(special_request) as special_request,
  any_value(referral_source) as referral_source,
  any_value(cook_id) as cook_id,
  any_value(location_id) as location_id
from {{ source("generated_sources", "sales_data") }}
group by all
