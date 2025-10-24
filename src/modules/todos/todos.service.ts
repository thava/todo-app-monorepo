import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  Inject,
} from '@nestjs/common';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq, and, desc } from 'drizzle-orm';
import * as schema from '../../database/schema';
import { todos, users } from '../../database/schema';
import { DATABASE_CONNECTION } from '../../database/database.module';
import { CreateTodoDto } from './dto/create-todo.dto';
import { UpdateTodoDto } from './dto/update-todo.dto';

@Injectable()
export class TodosService {
  constructor(
    @Inject(DATABASE_CONNECTION)
    private readonly db: PostgresJsDatabase<typeof schema>,
  ) {}

  /**
   * Create a new todo
   */
  async create(userId: string, createTodoDto: CreateTodoDto) {
    const [todo] = await this.db
      .insert(todos)
      .values({
        ownerId: userId,
        description: createTodoDto.description,
        dueDate: createTodoDto.dueDate,
        priority: createTodoDto.priority || 'medium',
      })
      .returning();

    // Get owner email
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, userId),
      columns: { email: true },
    });

    return {
      ...todo,
      ownerEmail: owner?.email,
    };
  }

  /**
   * Find all todos for current user
   */
  async findAllForUser(userId: string) {
    const userTodos = await this.db.query.todos.findMany({
      where: eq(todos.ownerId, userId),
      orderBy: [desc(todos.createdAt)],
    });

    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, userId),
      columns: { email: true },
    });

    return userTodos.map((todo) => ({
      ...todo,
      ownerEmail: owner?.email,
    }));
  }

  /**
   * Find all todos (admin only)
   */
  async findAll() {
    const allTodos = await this.db.query.todos.findMany({
      orderBy: [desc(todos.createdAt)],
      with: {
        // Note: We'll need to set up relations in schema for this
      },
    });

    // Get all owner emails
    const ownerIds = [...new Set(allTodos.map((t) => t.ownerId))];
    const owners = await this.db.query.users.findMany({
      where: (users, { inArray }) => inArray(users.id, ownerIds),
      columns: { id: true, email: true },
    });

    const ownerMap = new Map(owners.map((o) => [o.id, o.email]));

    return allTodos.map((todo) => ({
      ...todo,
      ownerEmail: ownerMap.get(todo.ownerId),
    }));
  }

  /**
   * Find one todo by ID
   */
  async findOne(id: string, userId: string, userRole: string) {
    const todo = await this.db.query.todos.findFirst({
      where: eq(todos.id, id),
    });

    if (!todo) {
      throw new NotFoundException('Todo not found');
    }

    // Check authorization
    if (userRole === 'guest' && todo.ownerId !== userId) {
      throw new ForbiddenException('You can only view your own todos');
    }

    // Get owner email
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, todo.ownerId),
      columns: { email: true },
    });

    return {
      ...todo,
      ownerEmail: owner?.email,
    };
  }

  /**
   * Update a todo
   */
  async update(
    id: string,
    userId: string,
    userRole: string,
    updateTodoDto: UpdateTodoDto,
  ) {
    const todo = await this.db.query.todos.findFirst({
      where: eq(todos.id, id),
    });

    if (!todo) {
      throw new NotFoundException('Todo not found');
    }

    // Check authorization
    if (userRole !== 'sysadmin' && todo.ownerId !== userId) {
      throw new ForbiddenException('You can only update your own todos');
    }

    const [updatedTodo] = await this.db
      .update(todos)
      .set({
        description: updateTodoDto.description,
        dueDate: updateTodoDto.dueDate,
        priority: updateTodoDto.priority,
        updatedAt: new Date(),
      })
      .where(eq(todos.id, id))
      .returning();

    // Get owner email
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, updatedTodo.ownerId),
      columns: { email: true },
    });

    return {
      ...updatedTodo,
      ownerEmail: owner?.email,
    };
  }

  /**
   * Delete a todo
   */
  async remove(id: string, userId: string, userRole: string) {
    const todo = await this.db.query.todos.findFirst({
      where: eq(todos.id, id),
    });

    if (!todo) {
      throw new NotFoundException('Todo not found');
    }

    // Check authorization
    if (userRole !== 'sysadmin' && todo.ownerId !== userId) {
      throw new ForbiddenException('You can only delete your own todos');
    }

    await this.db.delete(todos).where(eq(todos.id, id));
  }
}
