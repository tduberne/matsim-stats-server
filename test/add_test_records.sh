#!/bin/sh

for f in records/*.json; do
	curl -H "Content-Type: application/json" --data "@$f" http://localhost:8000/api/data
done
