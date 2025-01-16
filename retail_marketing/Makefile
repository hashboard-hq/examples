all: ./data_catalog/sales_data.parquet ./data_catalog/customers.parquet ./data_catalog/campaigns.parquet target/manifest.json upload_data deploy_hb

./data_catalog/sales_data.parquet : generate_data.py
	uv run generate_data.py

./data_catalog/customers.parquet : generate_customers.py ./data_catalog/sales_data.parquet
	uv run generate_customers.py

./data_catalog/campaigns.parquet :  generate_marketing.py ./data_catalog/sales_data.parquet
	uv run generate_marketing.py

./target/manifest.json ./data_catalog/dbt/customers.parquet : ./data_catalog/sales_data.parquet ./data_catalog/customers.parquet ./data_catalog/sales_data.parquet
	uv run dbt build

upload_data : target/manifest.json
	uv run hb datasource upload ./data_catalog/dbt/*.parquet

deploy_hb : upload_data
	uv run hb build

clean :
	rm -f ./data_catalog/*.parquet ./data_catalog/dbt/*.parquet
	rm -f target/manifest.json
