select 
  cast(FARM_FINGERPRINT(pizza_type || pizza_shape || pizza_size ) as string) as id,
  pizza_size,
  pizza_shape,
  pizza_type,
  price
from {{ source("generated_sources", "sales_data") }}
group by all
