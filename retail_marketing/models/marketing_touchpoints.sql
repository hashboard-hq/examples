select *
from {{ source("generated_sources", "marketing_touchpoints") }}
