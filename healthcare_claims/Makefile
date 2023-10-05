all: ./data_catalog/claims.parquet upload_data deploy_hb

./data_catalog/claims.parquet : generate_claims.py
	python generate_claims.py

upload_data : ./data_catalog/claims.parquet
	hb upload ./data_catalog/*.parquet

deploy_hb : upload_data
	hb deploy

clean :
	rm -f ./data_catalog/*.parquet 
