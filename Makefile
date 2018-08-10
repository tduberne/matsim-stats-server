.PHONY: build test-up prod-up down CLEAR_ALL_DATA configure-superset


test-up: build
	docker-compose -f docker-compose.yml -f docker-compose_test.yml up -d


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

