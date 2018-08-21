.PHONY: build test-up prod-up down CLEAR_ALL_DATA add-test-records psql


test-up: build
	docker-compose -f docker-compose.yml -f docker-compose_test.yml up -d
	# Add test records at this level? Would need a clean way to test that
	# everything is up

add-test-records:
	cd test && ./add_test_records.sh

psql:
	docker exec -it matsim_stats_postgres psql -U postgres -d matsim_stats_db

prod-up: build
	docker-compose -f docker-compose.yml -f docker-compose_prod.yml up -d

build:
	docker-compose build

down:
	docker-compose down

CLEAR_ALL_DATA:
	docker-compose down --volume
