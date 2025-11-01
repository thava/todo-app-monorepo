import { z } from 'zod';
import { PASSWORD_RULES } from '../constants';

/**
 * Email validation schema
 */
export const emailSchema = z
  .string()
  .email('Invalid email format')
  .toLowerCase()
  .trim();

/**
 * Password validation schema
 */
export const passwordSchema = z
  .string()
  .min(PASSWORD_RULES.MIN_LENGTH, `Password must be at least ${PASSWORD_RULES.MIN_LENGTH} characters`)
  .refine((password) => {
    let characterClasses = 0;
    if (/[a-z]/.test(password)) characterClasses++;
    if (/[A-Z]/.test(password)) characterClasses++;
    if (/[0-9]/.test(password)) characterClasses++;
    if (/[^a-zA-Z0-9]/.test(password)) characterClasses++;
    return characterClasses >= PASSWORD_RULES.MIN_CHARACTER_CLASSES;
  }, `Password must contain at least ${PASSWORD_RULES.MIN_CHARACTER_CLASSES} of: uppercase, lowercase, number, special character`);

/**
 * Register input validation
 */
export const registerInputSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  fullName: z.string().min(1, 'Full name is required').max(255),
});

/**
 * Login input validation
 */
export const loginInputSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

/**
 * Todo creation validation
 */
export const createTodoInputSchema = z.object({
  description: z.string().min(1, 'Description is required'),
  priority: z.enum(['low', 'medium', 'high']).optional().default('medium'),
  dueDate: z.string().datetime().optional(),
});

/**
 * Todo update validation
 */
export const updateTodoInputSchema = z.object({
  description: z.string().min(1).optional(),
  priority: z.enum(['low', 'medium', 'high']).optional(),
  dueDate: z.string().datetime().optional().nullable(),
});

/**
 * Pagination validation
 */
export const paginationSchema = z.object({
  page: z.number().int().positive().default(1),
  pageSize: z.number().int().positive().max(100).default(20),
});

export type RegisterInput = z.infer<typeof registerInputSchema>;
export type LoginInput = z.infer<typeof loginInputSchema>;
export type CreateTodoInput = z.infer<typeof createTodoInputSchema>;
export type UpdateTodoInput = z.infer<typeof updateTodoInputSchema>;
export type Pagination = z.infer<typeof paginationSchema>;
