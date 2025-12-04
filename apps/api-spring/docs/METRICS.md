# Custom Metrics

## Overview

The Spring Boot application exposes custom business metrics using Micrometer and Prometheus for monitoring key application events.

## Available Metrics

### User Metrics

**`app.user.registrations`** (Counter)
- Description: Total number of user registrations
- Tags: `type=user`

**`app.user.registrations.by.role`** (Counter)
- Description: User registrations grouped by role
- Tags: `role={guest|admin|sysadmin}`

### Authentication Metrics

**`app.auth.login`** (Counter)
- Description: Login attempts
- Tags: `result={success|failure}`

### Todo Metrics

**`app.todo.operations`** (Counter)
- Description: Todo operations
- Tags: `operation={create|update|delete}`

**`app.todo.created.by.priority`** (Counter)
- Description: Todos created grouped by priority
- Tags: `priority={low|medium|high}`

### Email Metrics

**`app.email.sent`** (Counter)
- Description: Email sending attempts
- Tags: `result={success|failure}`

**`app.email.sent.by.type`** (Counter)
- Description: Emails sent grouped by type
- Tags: `type={verification|password_reset}`, `result={success|failure}`

## Accessing Metrics

### Prometheus Format

```bash
curl http://localhost:9000/actuator/prometheus
```

### JSON Format

```bash
# All metrics
curl http://localhost:9000/actuator/metrics

# Specific metric
curl http://localhost:9000/actuator/metrics/app.user.registrations
```

## Integration

The `MetricsService` is injected into relevant service classes:

- **UserService** - Records user registrations
- **AuthController** - Records login attempts
- **TodoService** - Records todo operations
- **EmailService** - Records email sending

### Example Usage

```java
@Service
public class UserService {
    private final MetricsService metricsService;

    public void registerUser(...) {
        // ... registration logic
        metricsService.recordUserRegistration(role.getValue());
    }
}
```

## Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'spring-boot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['localhost:9000']
```

## Grafana Dashboard

Example queries for Grafana:

```promql
# User registration rate (per minute)
rate(app_user_registrations_total[5m]) * 60

# Login success rate
rate(app_auth_login_total{result="success"}[5m]) / rate(app_auth_login_total[5m])

# Todos created per minute
rate(app_todo_operations_total{operation="create"}[5m]) * 60

# Email success rate
rate(app_email_sent_total{result="success"}[5m]) / rate(app_email_sent_total[5m])
```

## Custom Metrics

To add new metrics, use the `MeterRegistry`:

```java
@Service
public class MyService {
    private final MeterRegistry meterRegistry;

    public void recordCustomEvent() {
        Counter.builder("app.custom.event")
            .description("Custom event counter")
            .tag("type", "custom")
            .register(meterRegistry)
            .increment();
    }
}
```
