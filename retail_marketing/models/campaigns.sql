select *
from {{ source("generated_sources", "campaigns") }}
