MATSim Stats Server
===================

Server side of anonymous MATSim usage data collection


Building, Testing, Running
--------------------------

The application is built and run using `docker-compose`,
that you will need installed (together with docker,
of course).

A Makefile is provided to simplify the process:

```
make
```

Builds and runs a test environment.
All data will be lost at shutdown.

```
make prod-up
```

Builds and runs a production environment.
Data is persisted at shutdown.

```
make down
```

shuts all services down.

After the first start of the production environment
(or after each start of the testing environment),
run the following commands to configure credentials:

```
make configure-superset
```

