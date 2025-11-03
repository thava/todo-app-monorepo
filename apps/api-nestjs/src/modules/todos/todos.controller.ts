import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { Roles } from '../../common/decorators/roles.decorator';
import { GetCurrentUser } from '../../common/decorators/current-user.decorator';
import { TodosService } from './todos.service';
import { CreateTodoDto } from './dto/create-todo.dto';
import { UpdateTodoDto } from './dto/update-todo.dto';

@ApiTags('todos')
@ApiBearerAuth()
@Controller('todos')
@UseGuards(JwtAuthGuard, RolesGuard)
export class TodosController {
  constructor(private readonly todosService: TodosService) {}

  @Post()
  @ApiOperation({
    summary: 'Create a new todo',
    description: 'Creates a new todo item for the authenticated user'
  })
  @ApiResponse({ status: 201, description: 'Todo created successfully' })
  @ApiResponse({ status: 400, description: 'Invalid input data' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  create(
    @GetCurrentUser('userId') userId: string,
    @Body() createTodoDto: CreateTodoDto,
  ) {
    return this.todosService.create(userId, createTodoDto);
  }

  @Get()
  @ApiOperation({
    summary: 'Get all todos',
    description: 'Retrieves all todos. Regular users see only their own todos, while admins and sysadmins see all todos.'
  })
  @ApiResponse({ status: 200, description: 'List of todos retrieved successfully' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  findAll(
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
  ) {
    // Admin and sysadmin can see all todos
    if (role === 'admin' || role === 'sysadmin') {
      return this.todosService.findAll();
    }
    // Regular users see only their own
    return this.todosService.findAllForUser(userId);
  }

  @Get(':id')
  @ApiOperation({
    summary: 'Get a todo by ID',
    description: 'Retrieves a specific todo by its ID. Regular users can only access their own todos.'
  })
  @ApiResponse({ status: 200, description: 'Todo retrieved successfully' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Not authorized to access this todo' })
  @ApiResponse({ status: 404, description: 'Todo not found' })
  findOne(
    @Param('id') id: string,
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
  ) {
    return this.todosService.findOne(id, userId, role);
  }

  @Patch(':id')
  @ApiOperation({
    summary: 'Update a todo',
    description: 'Updates a todo by its ID. Regular users can only update their own todos.'
  })
  @ApiResponse({ status: 200, description: 'Todo updated successfully' })
  @ApiResponse({ status: 400, description: 'Invalid input data' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Not authorized to update this todo' })
  @ApiResponse({ status: 404, description: 'Todo not found' })
  update(
    @Param('id') id: string,
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
    @Body() updateTodoDto: UpdateTodoDto,
  ) {
    return this.todosService.update(id, userId, role, updateTodoDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete a todo',
    description: 'Deletes a todo by its ID. Regular users can only delete their own todos.'
  })
  @ApiResponse({ status: 204, description: 'Todo deleted successfully' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Not authorized to delete this todo' })
  @ApiResponse({ status: 404, description: 'Todo not found' })
  remove(
    @Param('id') id: string,
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
  ) {
    return this.todosService.remove(id, userId, role);
  }
}
