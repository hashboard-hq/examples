# Hashboard Healthcare Claims example

[Hashboard](https://hashboard.com) supports defining models, views, and dashboards as code, which can then be deployed to your project using [DataOps](https://docs.hashboard.com/docs/data-ops/). This repository contains some examples to help you get started. [You can see and explore a live demo of these resources here](https://demo.hashboard.com/app?p=dn_sTAM59tqw20Pt).

## Usage

``` bash
git clone https://github.com/hashboard-hq/examples.git

cd healthcare_claims

# with python 2.9+
pip install -r requirements.txt

# you need to get your authorization key setup locally
hb signup # to signup

# you can run all of the below step just with make:
make -B
