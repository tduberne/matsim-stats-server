.PHONY: build test-up prod-up down CLEAR_ALL_DATA configure-superset add-test-records


test-up: build
	docker-compose -f docker-compose.yml -f docker-compose_test.yml up -d
	# Add test records at this level? Would need a clean way to test that
	# everything is up

add-test-records:
	cd test && ./add_test_records.sh

prod-up: build
	docker-compose -f docker-compose.yml -f docker-compose_prod.yml up -d
	
configure-superset:
	docker exec -it matsim_stats_superset superset-init

build:
	docker-compose build

down:
	docker-compose down

CLEAR_ALL_DATA:
	docker-compose down --volume
