#!/bin/sh

for f in records/*.json; do
	curl -H "Content-Type: application/json" --data "@$f" http://localhost/api/data
done
