import { IsString, IsOptional, IsEnum, IsDateString } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateTodoDto {
  @ApiProperty({
    description: 'Description of the todo item',
    example: 'Buy groceries for the week'
  })
  @IsString()
  description: string;

  @ApiPropertyOptional({
    description: 'Due date for the todo item',
    example: '2025-12-31T23:59:59.000Z'
  })
  @IsOptional()
  @IsDateString()
  dueDate?: Date;

  @ApiPropertyOptional({
    description: 'Priority level of the todo item',
    enum: ['low', 'medium', 'high'],
    example: 'medium'
  })
  @IsOptional()
  @IsEnum(['low', 'medium', 'high'])
  priority?: 'low' | 'medium' | 'high';
}
