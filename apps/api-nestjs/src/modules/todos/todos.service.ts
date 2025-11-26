import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  Inject,
} from '@nestjs/common';
import { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { eq, and, desc } from 'drizzle-orm';
import * as schema from '@todo-app/database';
import { todos, users } from '@todo-app/database';
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
        dueDate: createTodoDto.dueDate ? new Date(createTodoDto.dueDate) : null,
        priority: createTodoDto.priority || 'medium',
      })
      .returning();

    // Get owner information
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, userId),
      columns: { email: true, fullName: true, role: true },
    });

    return {
      ...todo,
      ownerEmail: owner?.email,
      ownerName: owner?.fullName,
      ownerRole: owner?.role,
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
      columns: { email: true, fullName: true, role: true },
    });

    return userTodos.map((todo) => ({
      ...todo,
      ownerEmail: owner?.email,
      ownerName: owner?.fullName,
      ownerRole: owner?.role,
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

    // Get all owner information
    const ownerIds = [...new Set(allTodos.map((t) => t.ownerId))];
    const owners = await this.db.query.users.findMany({
      where: (users, { inArray }) => inArray(users.id, ownerIds),
      columns: { id: true, email: true, fullName: true, role: true },
    });

    const ownerMap = new Map(owners.map((o) => [o.id, { email: o.email, fullName: o.fullName, role: o.role }]));

    return allTodos.map((todo) => {
      const ownerInfo = ownerMap.get(todo.ownerId);
      return {
        ...todo,
        ownerEmail: ownerInfo?.email,
        ownerName: ownerInfo?.fullName,
        ownerRole: ownerInfo?.role,
      };
    });
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

    // Get owner information
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, todo.ownerId),
      columns: { email: true, fullName: true, role: true },
    });

    return {
      ...todo,
      ownerEmail: owner?.email,
      ownerName: owner?.fullName,
      ownerRole: owner?.role,
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

    console.log('Todo Update: Lookup: id: ', id)
    console.log('Found todo: ', todo)

    if (!todo) {
      throw new NotFoundException('Todo not found');
    }

    // Check authorization
    if (userRole !== 'sysadmin' && todo.ownerId !== userId) {
      throw new ForbiddenException('You can only update your own todos');
    }

    // Build update object, only including provided fields
    const updateData: any = {
      updatedAt: new Date(),
    };

    if (updateTodoDto.description !== undefined) {
      updateData.description = updateTodoDto.description;
    }

    if (updateTodoDto.dueDate !== undefined) {
      updateData.dueDate = updateTodoDto.dueDate ? new Date(updateTodoDto.dueDate) : null;
    }

    if (updateTodoDto.priority !== undefined) {
      updateData.priority = updateTodoDto.priority;
    }

    const [updatedTodo] = await this.db
      .update(todos)
      .set(updateData)
      .where(eq(todos.id, id))
      .returning();

    // Get owner information
    const owner = await this.db.query.users.findFirst({
      where: eq(users.id, updatedTodo.ownerId),
      columns: { email: true, fullName: true, role: true },
    });

    return {
      ...updatedTodo,
      ownerEmail: owner?.email,
      ownerName: owner?.fullName,
      ownerRole: owner?.role,
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
