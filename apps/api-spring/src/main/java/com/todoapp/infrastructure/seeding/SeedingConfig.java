package com.todoapp.infrastructure.seeding;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Getter
@Configuration
public class SeedingConfig {

    @Value("${app.seeding.enabled:true}")
    private boolean enabled;
}
