all: ./data_catalog/sales_data.parquet ./data_catalog/customers.parquet ./data_catalog/campaigns.parquet target/manifest.json upload_data deploy_hb

./data_catalog/sales_data.parquet : generate_data.py
	python generate_data.py

./data_catalog/customers.parquet : generate_customers.py ./data_catalog/sales_data.parquet
	python generate_customers.py

./data_catalog/campaigns.parquet :  generate_marketing.py ./data_catalog/sales_data.parquet
	python generate_marketing.py

./target/manifest.json ./data_catalog/dbt/customers.parquet : ./data_catalog/sales_data.parquet ./data_catalog/customers.parquet ./data_catalog/sales_data.parquet
	dbt build

upload_data : target/manifest.json
	hb upload ./data_catalog/dbt/*.parquet

deploy_hb : upload_data
	hb deploy --dbt

clean :
	rm -f ./data_catalog/*.parquet ./data_catalog/dbt/*.parquet
	rm -f target/manifest.json
