# Hashboard Marketing and Retail example using dbt + duckdb 

[Hashboard](https://hashboard.com) supports defining models, views, and dashboards as code, which can then be deployed to your project using [DataOps](https://docs.hashboard.com/docs/data-ops/). This repository contains some examples to help you get started. You can see and explore a live demo of these resources at: https://demo.hashboard.com

## Usage

``` bash
git clone https://github.com/hashboard-hq/examples.git

cd 04_retail_marketing

# with python 2.9+
pip install -r requirements.txt

# you need to get your authorization key setup locally
# see docs here: https://docs.hashboard.com/docs/data-ops/cli#1-create-an-access-key

# you can run all of the below step just with make:
make -B

# generate synthetic data:
python generate_data.py
python generate_customers.py
python generate_marketing.py

# run dbt
dbt build

# you can upload the files in data manually, or progromatically
for file in ./data_catalog/dbt/*; do hb upload Uploads "$$file"; done

# run hashboard:
hb preview --dbt
```

