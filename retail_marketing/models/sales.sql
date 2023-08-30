select 
  hash("order_id" || '_' || "item_number") as "item_id",
  "order_id",
  "item_number",
  cast(hash("pizza_type" || "pizza_shape" || "pizza_size" ) as string) as "product_id",
  "quantity",
  "customer_id",
  "item_price",
  "timestamp"
from {{ source("generated_sources", "sales_data") }}
