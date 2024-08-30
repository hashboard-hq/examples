select 
  FARM_FINGERPRINT(order_id || '_' || item_number) as item_id,
  order_id,
  item_number,
  cast(FARM_FINGERPRINT(pizza_type || pizza_shape || pizza_size ) as string) as product_id,
  quantity,
  customer_id,
  cast(item_price as decimal) as item_price,
  timestamp_seconds(cast(timestamp/1000000000 as int)) as timestamp
from {{ source("generated_sources", "sales_data") }}
