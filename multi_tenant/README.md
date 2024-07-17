This project demonstrates how you can deploy templated models, explorations, and dashboards to downstream customers, using the Hashboard CLI and Partner Projects.

In this example, which simulates grocery sales data, we have a main production dataset in Bigquery that stores data for all of our customers. We then have two parallel datasets, containing this data filtered down to only a single customer.

Use the `BQ_DATASET` environment variable to control which Bigquery dataset the target project will use.

For example:

```bash
$ BQ_DATASET=production hb deploy
```
