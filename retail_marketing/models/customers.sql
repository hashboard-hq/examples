select *
from {{ source('generated_sources', 'customers') }}
