SHELL=/bin/bash

ARGS=
FILE=test

define sql_ingest
SET datestyle = 'DMY';
CREATE TABLE IF NOT EXISTS public.products
(
		id serial NOT NULL PRIMARY KEY,
		date date NOT NULL,
		location character varying NOT NULL,
		product character varying NOT NULL,
		inventory_curve_id integer NOT NULL,
		consumption_profile_curve_id integer NOT NULL
);
CREATE TABLE IF NOT EXISTS public.temp_curves
(
		curve_id integer NOT NULL PRIMARY KEY,
		curve_type character varying NOT NULL,
		week_start date NOT NULL,
		x character varying NOT NULL,
		y character varying NOT NULL
);
CREATE TABLE IF NOT EXISTS public.curves
(
		curve_id integer NOT NULL PRIMARY KEY,
		curve_type character varying NOT NULL,
		week_start date NOT NULL,
		x integer[] NOT NULL,
		y float[] NOT NULL
);
copy public.products (date, location, product, inventory_curve_id, consumption_profile_curve_id) FROM '/ingest/qos_data.csv' DELIMITER ',' CSV HEADER;
copy public.temp_curves (curve_id, curve_type, week_start, X, Y) FROM '/ingest/qos_curves.csv' DELIMITER ',' CSV HEADER;

INSERT INTO curves (curve_id, curve_type, week_start, x, y)
SELECT
    curve_id,
    curve_type,
		week_start,
		string_to_array(trim(both '[]' from X), ',')::INTEGER[],
    string_to_array(trim(both '[]' from Y), ',')::FLOAT[]
FROM temp_curves;
DROP TABLE public.temp_curves;
CREATE TABLE IF NOT EXISTS public.qos_metrics
(
		log_id serial NOT NULL PRIMARY KEY,
		location character varying NOT NULL,
		week_start date NOT NULL,
		qos_metric float NOT NULL
);
CREATE RULE qos_insert_deter AS ON INSERT TO public.qos_metrics
WHERE (EXISTS ( SELECT * FROM public.qos_metrics as q WHERE q.location = new.location AND q.week_start = new.week_start)) DO INSTEAD NOTHING
endef

.PHONY: build run

all: mypy lint test

mypy:
	@docker compose -f docker-compose.test.yml run --rm mypy $(ARGS)

lint:
	@docker compose -f docker-compose.test.yml run --rm lint $(ARGS)

test:
	@docker compose -f docker-compose.test.yml run --rm tests $(ARGS)

build:
	@docker compose -f docker-compose.dev.yml build $(ARGS)

build-test:
	@docker compose -f docker-compose.test.yml build $(ARGS)

run:
	@docker compose -f docker-compose.dev.yml up --remove-orphans $(ARGS)

clean:
	@docker compose -f docker-compose.$(FILE).yml down --remove-orphans
	@docker volume rm felfel-taskwork_postgres-db-data

export sql_ingest
ingest:
	docker exec -it felfel-taskwork-postgres-1 psql -U felfel -d qos -c "$$sql_ingest"
