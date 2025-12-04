buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath("org.postgresql:postgresql:42.7.3")
    }
}

plugins {
    java
    id("org.springframework.boot") version "3.4.0"
    id("io.spring.dependency-management") version "1.1.6"
    id("org.flywaydb.flyway") version "10.20.1"
    id("nu.studer.jooq") version "9.0"
}

group = "com.todoapp"
version = "1.0.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

configurations {
    compileOnly {
        extendsFrom(configurations.annotationProcessor.get())
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot Starters
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-jooq")

    // Database
    implementation("org.postgresql:postgresql")
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")
    implementation("com.zaxxer:HikariCP")

    // jOOQ
    jooqGenerator("org.postgresql:postgresql")

    // JWT
    implementation("io.jsonwebtoken:jjwt-api:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.6")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.6")

    // MapStruct
    implementation("org.mapstruct:mapstruct:1.6.2")
    annotationProcessor("org.mapstruct:mapstruct-processor:1.6.2")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok-mapstruct-binding:0.2.0")

    // SendGrid
    implementation("com.sendgrid:sendgrid-java:4.10.3")

    // Problem+JSON (RFC7807)
    implementation("org.zalando:problem-spring-web:0.29.1")

    // OpenAPI Documentation
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.6.0")

    // Micrometer
    runtimeOnly("io.micrometer:micrometer-registry-prometheus")

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
    testImplementation("org.testcontainers:testcontainers:1.20.4")
    testImplementation("org.testcontainers:postgresql:1.20.4")
    testImplementation("org.testcontainers:junit-jupiter:1.20.4")
    testImplementation("org.wiremock:wiremock-standalone:3.9.2")
    testImplementation("org.assertj:assertj-core")
}

tasks.withType<Test> {
    useJUnitPlatform()
}

// Flyway configuration
flyway {
    driver = "org.postgresql.Driver"
    url = System.getenv("SPRING_DATABASE_URL") ?: "jdbc:postgresql://localhost:5434/todo_spring_dev"
    user = System.getenv("SPRING_DATABASE_USER") ?: "todo_user"
    password = System.getenv("SPRING_DATABASE_PASSWORD") ?: "todo_password_dev"
    locations = arrayOf("filesystem:src/main/resources/db/migration")
}

// jOOQ configuration
jooq {
    version.set("3.19.15")

    configurations {
        create("main") {
            jooqConfiguration.apply {
                jdbc.apply {
                    driver = "org.postgresql.Driver"
                    url = System.getenv("SPRING_DATABASE_URL") ?: "jdbc:postgresql://localhost:5434/todo_spring_dev"
                    user = System.getenv("SPRING_DATABASE_USER") ?: "todo_user"
                    password = System.getenv("SPRING_DATABASE_PASSWORD") ?: "todo_password_dev"
                }
                generator.apply {
                    name = "org.jooq.codegen.JavaGenerator"
                    database.apply {
                        name = "org.jooq.meta.postgres.PostgresDatabase"
                        inputSchema = "public"
                        excludes = "flyway_schema_history"
                    }
                    generate.apply {
                        isDeprecated = false
                        isRecords = true
                        isImmutablePojos = true
                        isFluentSetters = true
                        isJavaTimeTypes = true
                    }
                    target.apply {
                        packageName = "com.todoapp.infrastructure.jooq"
                        directory = "src/main/java"
                    }
                }
            }
        }
    }
}

// Make jOOQ generation depend on Flyway migration (commented out - use Spring Boot Flyway instead)
// tasks.named("generateJooq") {
//     dependsOn("flywayMigrate")
// }

// Custom tasks
tasks.register("cleanJooq") {
    group = "jooq"
    description = "Clean generated jOOQ sources"
    doLast {
        delete("src/main/java/com/todoapp/infrastructure/jooq")
    }
}

tasks.register<JavaExec>("seedDatabase") {
    group = "application"
    description = "Seed database with demo users and todos"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.todoapp.TodoAppApplication")
    args = listOf()
    systemProperty("spring.seed.enabled", "true")

    doFirst {
        println("🌱 Starting database seeding...")
        println("   Database: ${System.getenv("SPRING_DATABASE_URL") ?: "jdbc:postgresql://localhost:5434/todo_spring_dev"}")
    }
}

// Load apgdiff tasks
apply(from = "gradle/apgdiff.gradle.kts")
