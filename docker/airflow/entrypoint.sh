#!/bin/bash
set -e

# Function to wait for a service to be ready
wait_for_service() {
  local host="$1"
  local port="$2"
  local service="$3"
  local timeout="${4:-30}"
  
  echo "Waiting for $service to be ready at $host:$port..."
  for i in $(seq 1 $timeout); do
    nc -z "$host" "$port" >/dev/null 2>&1 && break
    echo "Waiting for $service... $i/$timeout"
    sleep 1
  done
  
  if [ "$i" -gt "$timeout" ]; then
    echo "Timeout waiting for $service at $host:$port"
    exit 1
  fi
  
  echo "$service is ready!"
}

# Wait for PostgreSQL if needed
if [ "$AIRFLOW__CORE__SQL_ALCHEMY_CONN" != "" ]; then
  # Extract host and port from the connection string
  DB_HOST=$(echo "$AIRFLOW__CORE__SQL_ALCHEMY_CONN" | sed -e 's/^.*@\(.*\):.*/\1/')
  DB_PORT=$(echo "$AIRFLOW__CORE__SQL_ALCHEMY_CONN" | sed -e 's/^.*:\([0-9]*\)\/.*/\1/')
  
  if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
    wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
  fi
fi

# Wait for Redis if needed
if [ "$AIRFLOW__CELERY__BROKER_URL" != "" ]; then
  # Extract host and port from the connection string
  REDIS_HOST=$(echo "$AIRFLOW__CELERY__BROKER_URL" | sed -e 's/^.*@\(.*\):.*/\1/')
  REDIS_PORT=$(echo "$AIRFLOW__CELERY__BROKER_URL" | sed -e 's/^.*:\([0-9]*\)\/.*/\1/')
  
  if [ ! -z "$REDIS_HOST" ] && [ ! -z "$REDIS_PORT" ]; then
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
  fi
fi

# Initialize the database if needed
if [ "$1" = "webserver" ] || [ "$1" = "scheduler" ]; then
  airflow db init
  
  # Create admin user if not exists
  if [ "$AIRFLOW_ADMIN_USER" != "" ] && [ "$AIRFLOW_ADMIN_PASSWORD" != "" ]; then
    airflow users create \
      --username "$AIRFLOW_ADMIN_USER" \
      --password "$AIRFLOW_ADMIN_PASSWORD" \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com || true
  fi
fi

# Start Airflow service
exec airflow "$@" 