import { NestFactory } from '@nestjs/core';
import { ValidationPipe, INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { stringify } from 'yaml';

import * as path from 'path';
import * as fs from 'fs';

// import * as express from 'express';

function setupDocs(app: INestApplication) {
  const config = new DocumentBuilder()
    .setTitle('Todo App API')
    .setDescription('REST API for Todo Application with authentication and role-based access control')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);

  // Setup Swagger UI at /docs
  SwaggerModule.setup('docs', app, document);

  // Write OpenAPI spec as YAML to disk
  const yamlString = stringify(document);
  // Note: dirname is dist/src directory.
  fs.mkdirSync(path.join(__dirname, '../docs'), { recursive: true });
  fs.writeFileSync(path.join(__dirname, '../docs/openapi.yaml'), yamlString);

  // ReDoc HTML template
  const redocHtml = `
<!DOCTYPE html>
<html>
  <head>
    <title>Todo App API - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
      body { margin: 0; padding: 0; }
    </style>
  </head>
  <body>
    <redoc spec-url='/api-spec'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  </body>
</html>
  `;
  fs.writeFileSync(path.join(__dirname, '../docs/redoc.html'), redocHtml);

  // Serve OpenAPI spec and ReDoc using the underlying HTTP adapter
  // This works with both Express and Fastify
  const httpAdapter = app.getHttpAdapter();
  httpAdapter.get('/api-spec', (req, res) => {
    res.setHeader('Content-Type', 'application/x-yaml');
    res.send(yamlString);
  });

  httpAdapter.get('/redoc', (req, res) => {
    res.setHeader('Content-Type', 'text/html');
    res.sendFile(path.join(__dirname, '../docs/redoc.html'));
  });

  const baseURL = `http://localhost:${process.env.NESTJS_PORT || process.env.PORT || 3000}`;
  console.log(`📚 API Documentation available at:`);
  console.log(`   - Swagger UI: ${baseURL}/docs`);
  console.log(`   - ReDoc: ${baseURL}/redoc`);
  console.log(`   - OpenAPI Spec: ${baseURL}/api-spec`);
}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable CORS
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS
    ? process.env.CORS_ALLOWED_ORIGINS.split(',')
    : ['http://localhost:4000',
       'http://localhost:4200',
       'http://localhost:4400',
       'http://localhost:3000'];

  app.enableCors({
    origin: allowedOrigins,
    credentials: false,
    methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: '*',
    // allowedHeaders: ['Content-Type', 'Authorization'],
  });

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // Setup API documentation
  setupDocs(app);

  // Log requests 
  // app.use(express.json());
  // app.use(express.urlencoded({ extended: true }));

  // app.use((req, _, next) => {
  //   // console.log(`[REQ] ${req.method} ${req.url}`);
  //   console.log(`[REQ] `, req.body);
  //   next();
  // });

  // Use NESTJS_PORT, fallback to PORT, then default to 3000
  const port = process.env.NESTJS_PORT || process.env.PORT || 3000;
  await app.listen(port);
  console.log(`🚀 NestJS API listening on http://localhost:${port}`);
  console.log(`🔓 CORS enabled for: ${allowedOrigins.join(', ')}`);
}
bootstrap();
