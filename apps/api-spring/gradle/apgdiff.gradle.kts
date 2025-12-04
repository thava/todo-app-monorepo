import java.io.ByteArrayOutputStream

/**
 * Custom Gradle tasks for PostgreSQL schema management using apgdiff
 *
 * Tasks:
 * - dumpSchema: Dump current database schema to docs/database/current-schema.sql
 * - compareSchema: Compare current database schema with expected schema
 */

val dbUrl = System.getenv("SPRING_DATABASE_URL") ?: "jdbc:postgresql://localhost:5434/todo_spring_dev"
val dbHost = dbUrl.substringAfter("://").substringBefore("/").substringBefore(":")
val dbPort = dbUrl.substringAfter(":").substringBefore("/").substringAfterLast(":")
val dbName = dbUrl.substringAfterLast("/").substringBefore("?")
val dbUser = System.getenv("SPRING_DATABASE_USER") ?: "todo_user"
val dbPassword = System.getenv("SPRING_DATABASE_PASSWORD") ?: "todo_password_dev"

// Set PGPASSWORD environment for pg_dump
val pgEnv = mapOf("PGPASSWORD" to dbPassword)

tasks.register<Exec>("dumpSchema") {
    group = "database"
    description = "Dump current PostgreSQL schema to docs/database/current-schema.sql"

    environment(pgEnv)

    commandLine(
        "pg_dump",
        "--host=$dbHost",
        "--port=$dbPort",
        "--username=$dbUser",
        "--schema-only",
        "--no-owner",
        "--no-privileges",
        "--no-tablespaces",
        "--no-security-labels",
        "--no-comments",
        dbName
    )

    standardOutput = ByteArrayOutputStream()

    doLast {
        val schemaFile = file("docs/database/current-schema.sql")
        schemaFile.parentFile.mkdirs()
        schemaFile.writeText(standardOutput.toString())
        println("✓ Schema dumped to ${schemaFile.path}")
    }
}

tasks.register<Exec>("compareSchema") {
    group = "database"
    description = "Compare database schema with expected schema using apgdiff"

    dependsOn("dumpSchema")

    doFirst {
        val currentSchema = file("docs/database/current-schema.sql")
        val expectedSchema = file("docs/database/expected-schema.sql")

        if (!expectedSchema.exists()) {
            println("⚠ No expected-schema.sql found. Creating from current schema...")
            expectedSchema.writeText(currentSchema.readText())
            println("✓ Created docs/database/expected-schema.sql")
            throw StopExecutionException("Please review expected-schema.sql and run again")
        }
    }

    commandLine(
        "sh", "-c",
        """
        if command -v apgdiff >/dev/null 2>&1; then
            apgdiff docs/database/expected-schema.sql docs/database/current-schema.sql
        else
            echo "⚠ apgdiff not installed. Install with: brew install apgdiff (macOS) or apt-get install apgdiff (Linux)"
            echo "Falling back to simple diff..."
            diff -u docs/database/expected-schema.sql docs/database/current-schema.sql || true
        fi
        """
    )

    isIgnoreExitValue = true

    doLast {
        println("\n✓ Schema comparison complete")
        println("  If differences shown above, database schema may need migration updates")
    }
}

tasks.register("schemaHelp") {
    group = "database"
    description = "Show help for schema management tasks"

    doLast {
        println("""
            |
            |Schema Management Tasks:
            |------------------------
            |
            |gradle dumpSchema
            |  Dumps the current database schema to docs/database/current-schema.sql
            |  Use this to document the current state of your database
            |
            |gradle compareSchema
            |  Compares current database schema with expected-schema.sql
            |  Shows DDL differences that may need migration scripts
            |  Requires apgdiff: brew install apgdiff (macOS)
            |
            |Environment Variables:
            |  SPRING_DATABASE_URL      (default: jdbc:postgresql://localhost:5434/todo_spring_dev)
            |  SPRING_DATABASE_USER     (default: todo_user)
            |  SPRING_DATABASE_PASSWORD (default: todo_password_dev)
            |
        """.trimMargin())
    }
}
