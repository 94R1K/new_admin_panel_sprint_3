#!/bin/bash

set -e

/usr/local/bin/docker-entrypoint.sh "$@" &
ES_PID=$!

echo "Waiting for Elasticsearch..."

until curl -fs http://127.0.0.1:9200 >/dev/null 2>&1; do
    sleep 2
done

echo "Elasticsearch is ready"

if curl -fs http://127.0.0.1:9200/movies >/dev/null 2>&1; then
    echo "Index 'movies' already exists"
else
    echo "Creating index 'movies'..."

    curl -fsS \
        -X PUT \
        http://127.0.0.1:9200/movies \
        -H 'Content-Type: application/json' \
        --data-binary @/usr/share/elasticsearch/config/movies.json

    echo
    echo "Index 'movies' created"
fi

wait "$ES_PID"