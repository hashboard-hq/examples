# Hashboard Marketing and Retail example using dbt + duckdb 

[Hashboard](https://hashboard.com) supports defining models, views, and dashboards as code, which can then be deployed to your project using [DataOps](https://docs.hashboard.com/docs/data-ops/). This repository contains some examples to help you get started. You can see and explore a live demo of these resources at: https://demo.hashboard.com

## Usage

``` bash
git clone https://github.com/hashboard-hq/examples.git

cd retail_marketing

# install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# create virtual environment with correct python version and dependencies
uv sync

# you need to get your authorization key setup locally
# see docs here: https://docs.hashboard.com/docs/data-ops/cli#1-create-an-access-key

# you can run all of the below step just with make:
make -B

# generate synthetic data:
uv run generate_data.py
uv run generate_customers.py
uv run generate_marketing.py

# run dbt
uv run dbt build

# upload the files
uv run hb datasource upload ./data_catalog/dbt/*.parquet

# run hashboard:
uv run hb build
```

