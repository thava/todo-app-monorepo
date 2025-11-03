import { Controller, Get, Inject } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { sql } from 'drizzle-orm';
import { DATABASE_CONNECTION } from '../../database/database.module';
import { Public } from '../decorators/public.decorator';
import * as schema from '@todo-app/database';

@ApiTags('health')
@Controller()
export class HealthController {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
  ) {}

  @Public()
  @Get('health')
  @ApiOperation({
    summary: 'Health check',
    description: 'Basic health check endpoint. Returns OK if the service is running. Used for liveness probes in container orchestration.'
  })
  @ApiResponse({
    status: 200,
    description: 'Service is healthy',
    schema: {
      type: 'object',
      properties: {
        status: { type: 'string', example: 'ok' },
        timestamp: { type: 'string', example: '2025-01-01T00:00:00.000Z' }
      }
    }
  })
  health() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
    };
  }

  @Public()
  @Get('readiness')
  @ApiOperation({
    summary: 'Readiness check',
    description: 'Readiness check endpoint that verifies database connectivity. Returns OK if all dependencies are available. Used for readiness probes in container orchestration.'
  })
  @ApiResponse({
    status: 200,
    description: 'Service is ready',
    schema: {
      type: 'object',
      properties: {
        status: { type: 'string', example: 'ok', enum: ['ok', 'degraded'] },
        checks: {
          type: 'object',
          properties: {
            database: { type: 'string', example: 'ok', enum: ['ok', 'fail'] }
          }
        },
        timestamp: { type: 'string', example: '2025-01-01T00:00:00.000Z' }
      }
    }
  })
  async readiness() {
    let dbHealthy = false;
    try {
      const result = await this.db.execute(sql`SELECT 1 as health`);
      dbHealthy = result.length > 0;
    } catch (error) {
      console.error('Database health check failed:', error);
    }

    return {
      status: dbHealthy ? 'ok' : 'degraded',
      checks: {
        database: dbHealthy ? 'ok' : 'fail',
      },
      timestamp: new Date().toISOString(),
    };
  }
}
