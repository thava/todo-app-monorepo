import { plainToInstance } from 'class-transformer';
import {
  IsString,
  IsNumber,
  IsEnum,
  IsBoolean,
  IsOptional,
  IsUrl,
  validateSync,
  Min,
  Max,
} from 'class-validator';

enum Environment {
  Development = 'development',
  Test = 'test',
  Production = 'production',
}

enum LogLevel {
  Error = 'error',
  Warn = 'warn',
  Info = 'info',
  Debug = 'debug',
}

export class EnvironmentVariables {
  // Application
  @IsEnum(Environment)
  NODE_ENV: Environment = Environment.Development;

  @IsNumber()
  @Min(1)
  @Max(65535)
  PORT: number = 3000;

  @IsUrl({ require_tld: false })
  API_URL: string;

  // Database
  @IsString()
  DATABASE_URL: string;

  @IsNumber()
  @Min(1)
  DATABASE_POOL_MIN: number = 2;

  @IsNumber()
  @Min(1)
  DATABASE_POOL_MAX: number = 10;

  // JWT
  @IsString()
  JWT_ACCESS_SECRET: string;

  @IsString()
  JWT_REFRESH_SECRET: string;

  @IsString()
  JWT_ACCESS_EXPIRY: string = '15m';

  @IsString()
  JWT_REFRESH_EXPIRY: string = '7d';

  // Email Provider (optional)
  @IsOptional()
  @IsString()
  SENDGRID_API_KEY?: string;

  @IsOptional()
  @IsString()
  SMTP_HOST?: string;

  @IsOptional()
  @IsNumber()
  SMTP_PORT?: number;

  @IsOptional()
  @IsString()
  SMTP_USER?: string;

  @IsOptional()
  @IsString()
  SMTP_PASS?: string;

  @IsOptional()
  @IsBoolean()
  SMTP_SECURE?: boolean;

  // Email Settings
  @IsString()
  EMAIL_FROM: string;

  @IsString()
  EMAIL_FROM_NAME: string;

  @IsString()
  EMAIL_REPLY_TO: string;

  // CORS
  @IsString()
  CORS_ALLOWED_ORIGINS: string;

  // Rate Limiting (optional)
  @IsOptional()
  @IsString()
  REDIS_URL?: string;

  // Monitoring
  @IsBoolean()
  ENABLE_METRICS: boolean = false;

  @IsOptional()
  @IsString()
  METRICS_AUTH_TOKEN?: string;

  // Logging
  @IsEnum(LogLevel)
  LOG_LEVEL: LogLevel = LogLevel.Info;
}

export function validate(config: Record<string, unknown>) {
  const validatedConfig = plainToInstance(EnvironmentVariables, config, {
    enableImplicitConversion: true,
  });

  const errors = validateSync(validatedConfig, {
    skipMissingProperties: false,
  });

  if (errors.length > 0) {
    throw new Error(errors.toString());
  }

  return validatedConfig;
}
