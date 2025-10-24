import { IsString, IsOptional, IsEnum, IsDateString } from 'class-validator';

export class CreateTodoDto {
  @IsString()
  description: string;

  @IsOptional()
  @IsDateString()
  dueDate?: Date;

  @IsOptional()
  @IsEnum(['low', 'medium', 'high'])
  priority?: 'low' | 'medium' | 'high';
}
