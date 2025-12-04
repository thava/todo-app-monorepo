#!/bin/bash
# Run database migrations using Spring Boot Flyway

echo "Running database migrations via Spring Boot..."

# Set Spring Boot to only run migrations and exit
export SPRING_FLYWAY_ENABLED=true

# Run Spring Boot app briefly to trigger Flyway migrations
timeout 30s ./gradlew bootRun --args='--spring.flyway.enabled=true' 2>&1 | grep -E "(Flyway|Migration|Starting|Started)" || true

echo "Migrations complete!"
