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
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { Roles } from '../../common/decorators/roles.decorator';
import { GetCurrentUser } from '../../common/decorators/current-user.decorator';
import { TodosService } from './todos.service';
import { CreateTodoDto } from './dto/create-todo.dto';
import { UpdateTodoDto } from './dto/update-todo.dto';

@Controller('todos')
@UseGuards(JwtAuthGuard, RolesGuard)
export class TodosController {
  constructor(private readonly todosService: TodosService) {}

  @Post()
  create(
    @GetCurrentUser('userId') userId: string,
    @Body() createTodoDto: CreateTodoDto,
  ) {
    return this.todosService.create(userId, createTodoDto);
  }

  @Get()
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
  findOne(
    @Param('id') id: string,
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
  ) {
    return this.todosService.findOne(id, userId, role);
  }

  @Patch(':id')
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
  remove(
    @Param('id') id: string,
    @GetCurrentUser('userId') userId: string,
    @GetCurrentUser('role') role: string,
  ) {
    return this.todosService.remove(id, userId, role);
  }
}
