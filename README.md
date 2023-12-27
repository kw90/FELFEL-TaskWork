# FELFEL Task Work

Service for computing the quality of service QoS metric according to FELFEL's [task description](https://github.com/felfel-tech/recruiting/blob/main/taskwork_python_qos/TASK_DESCRIPTION.md).

## Requirements
- Docker
- Make

## Getting Started

To build the image and run the service in dev mode, run

```zsh
make build
make run
```

## Ingest CSVs to Postgres

To ingest the raw data provided as `.csv` files in the previously spawned PostgreSQL instance, run

```zsh
make ingest
```

This will create the data base scheme and ingest all the data found in the `raw_data/qos_curves` and `raw_data/qos_data` files.

## Testing, Linting, Type Checking, Formatting

Run the tests with

```zsh
make build-test
make test
```

Similarly, for type checking and linting:
```zsh
make mypy
make lint
```

## Clean Up

To shut down and remove the data base volume run

```zsh
make clean
```


## Future Work

The proposed algorithm is calculated by first assessing the variety of products available in the inventory over a week at a given location, focusing on the diversity rather than the quantity of each item. This availability ratio is then compared to the consumption profile of the location, emphasizing times of high customer demand. The QoS metric is then derived by calculating the area under the curve of product availability, adjusted to the consumption profile.

The computed metric is an overall value that looks at one complete week. Instead of this, we could also look at different intervals, aggregate over multiple weeks, or considering the QoS 75% (which is considered good QoS), we could penalize moments where the QoS falls below this threshold.

There are also a number of additional metrics that could be added to this
- The current metric (if maximized wrongly) could lead to a lot of waste: it could be beneficial to track rates of waste, to reduce losses and optimize stock levels.
- Algorithmic Optimization for Efficient Routing: Besides looking at the curves in this project, integrate traffic, distance and vehicle data to optimize delivery and transportation routes to minimize fuel consumption and emissions. 
- Forecast the demand using the historical data and track the accuracy against actual sales.
