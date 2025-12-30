import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Param,
  Body,
  HttpCode,
  HttpStatus,
  UseGuards,
  Req,
  Ip,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import type { Request } from 'express';
import { AdminService } from './admin.service';
import { UpdateUserDto } from './dto/update-user.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { MergeAccountsDto, MergeAccountsResponseDto } from './dto/merge-accounts.dto';
import { Roles } from '../../common/decorators/roles.decorator';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { RolesGuard } from '../../common/guards/roles.guard';

@ApiTags('admin')
@ApiBearerAuth()
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Get('users')
  @Roles('admin', 'sysadmin')
  @ApiOperation({
    summary: 'Get all users',
    description: 'Retrieves all users in the system. Requires admin or sysadmin role.'
  })
  @ApiResponse({ status: 200, description: 'List of users retrieved successfully', type: [UserResponseDto] })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Requires admin or sysadmin role' })
  async getAllUsers(): Promise<UserResponseDto[]> {
    return this.adminService.getAllUsers();
  }

  @Get('users/:id')
  @Roles('admin', 'sysadmin')
  @ApiOperation({
    summary: 'Get user by ID',
    description: 'Retrieves a specific user by their ID. Requires admin or sysadmin role.'
  })
  @ApiResponse({ status: 200, description: 'User retrieved successfully', type: UserResponseDto })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Requires admin or sysadmin role' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async getUserById(@Param('id') id: string): Promise<UserResponseDto> {
    return this.adminService.getUserById(id);
  }

  @Patch('users/:id')
  @Roles('sysadmin')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Update user',
    description: 'Updates a user by their ID. Can update email, password, full name, role, and email verification status. Requires sysadmin role.'
  })
  @ApiResponse({ status: 200, description: 'User updated successfully', type: UserResponseDto })
  @ApiResponse({ status: 400, description: 'Invalid input data' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Requires sysadmin role' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async updateUser(
    @Param('id') id: string,
    @Body() updateUserDto: UpdateUserDto,
  ): Promise<UserResponseDto> {
    return this.adminService.updateUser(id, updateUserDto);
  }

  @Delete('users/:id')
  @Roles('sysadmin')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete user',
    description: 'Deletes a user by their ID. Requires sysadmin role.'
  })
  @ApiResponse({ status: 204, description: 'User deleted successfully' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Requires sysadmin role' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async deleteUser(@Param('id') id: string): Promise<void> {
    return this.adminService.deleteUser(id);
  }

  @Post('merge-users')
  @Roles('sysadmin')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Merge user accounts',
    description: 'Merges source user account into destination user account. Source account will be deleted after merge. Fails if there are overlapping identities. Requires sysadmin role.'
  })
  @ApiResponse({ status: 200, description: 'Accounts merged successfully', type: MergeAccountsResponseDto })
  @ApiResponse({ status: 400, description: 'Cannot merge - overlapping identities or invalid request' })
  @ApiResponse({ status: 401, description: 'Unauthorized' })
  @ApiResponse({ status: 403, description: 'Forbidden - Requires sysadmin role' })
  @ApiResponse({ status: 404, description: 'Source or destination user not found' })
  async mergeAccounts(
    @Body() mergeAccountsDto: MergeAccountsDto,
    @Req() req: Request,
    @Ip() ip: string,
  ): Promise<MergeAccountsResponseDto> {
    const userAgent = req.headers['user-agent'];
    return this.adminService.mergeAccounts(
      mergeAccountsDto.sourceUserId,
      mergeAccountsDto.destinationUserId,
      ip,
      userAgent,
    );
  }
}
