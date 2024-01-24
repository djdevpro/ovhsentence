#!/bin/bash

# Load variables from .env file

if [[ -f .env ]]; then
    while IFS= read -r line; do
        # Ignore lines starting with '#' as comments
        if [[ $line =~ ^\ *# ]]; then
            continue
        fi

        key=$(echo "$line" | cut -d'=' -f1)
        value=$(echo "$line" | cut -d'=' -f2-)
        export "$key=$value"
    done < .env
fi


# Set the image name and flavor
IMAGE_NAME="djdevpro/ovhsentence:latest"
FLAVOR="ai1-1-cpu"
CPU="1"
REPLICAS="1"
HTTP_PORT="8080"
PROBE_PATH="/test/health"
PROBE_PORT="8080"
LABELS='{"owner":"djdevpro"}'
UNSECURE_HTTP="--unsecure-http"

# Define the array of environment variables and their default values
declare -A ENV=(
  ['EXPECTED_POST_TOKEN']="$EXPECTED_POST_TOKEN"
  ['ASTRA_DB_API_ENDPOINT']="$ASTRA_DB_API_ENDPOINT"
  ['ASTRA_DB_APPLICATION_TOKEN']="$ASTRA_DB_APPLICATION_TOKEN"
  ['ASTRA_DB_KEYSPACE']="$ASTRA_DB_KEYSPACE"
  ['ASTRA_DB_DIMENSION']="$ASTRA_DB_DIMENSION"
  ['ASTRA_DB_METRIC']="$ASTRA_DB_METRIC"
  ['MODEL_NAME']="$MODEL_NAME"
)

for KEY in "${!ENV[@]}"; do
  VALUE="${ENV[$KEY]:-${!KEY}}"  # Use the value from the .env file if available, otherwise use the default value
  COMMAND+=" --env ${KEY}=${VALUE}"
done



ovhai app run \
    $COMMAND \
    --name ovhsentence \
    --flavor "$FLAVOR" \
    --cpu "$CPU" \
    --replicas "$REPLICAS" \
    --default-http-port "$HTTP_PORT" \
    --probe-path "$PROBE_PATH" \
    --probe-port "$PROBE_PORT" \
    --label owner=djdevpro \
    $UNSECURE_HTTP \
    "$IMAGE_NAME:latest"

