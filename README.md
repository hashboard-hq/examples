# Hashboard project examples

[Hashboard](https://hashboard.com) supports defining models, views, and dashboards as code, which can then be deployed to your project using [DataOps](https://docs.hashboard.com/docs/data-ops/). This repository contains some examples to help you get started. You can see and explore a live demo of these resources at: https://demo.hashboard.com

## Usage

To get started with DataOps, you'll need:

1. A Hashboard Demo Project (sign up on the [Hashboard homepage](https://hashboard.com) and use the "Import Demo Project" option in the top-left menu after logging in)
2. A Hashboard [Access Key](https://docs.hashboard.com/docs/data-ops/using-the-glean-cli/#1-create-an-access-key) for your Demo Project in your local environment

To install the Hashboard CLI:

```
$ pip install hashboard-cli
```

To pull this repo locally:

```
$ git clone https://github.com/hashboard-hq/examples.git
```

To create a Preview Build:

```
$ hb preview <subdirectory>
# Example:
$ hashboard preview ./01_subscription
```
