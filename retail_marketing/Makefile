.PHONY: market_data run_dbt upload_data deploy_hb

all: ./data/sales_data.parquet ./data/customers.parquet market_data run_dbt upload_data deploy_hb

./data/sales_data.parquet:
	python generate_data.py

./data/customers.parquet: ./data/sales_data.parquet
	python generate_customers.py

market_data: ./data/sales_data.parquet
	python generate_marketing.py

run_dbt: ./data/sales_data.parquet ./data/customers.parquet ./data/sales_data.parquet
	dbt build

upload_data: run_dbt
	for file in ./data/dbt/*; do hb upload Uploads "$$file"; done

deploy_hb: upload_data
	hb deploy --dbt --no-preview
