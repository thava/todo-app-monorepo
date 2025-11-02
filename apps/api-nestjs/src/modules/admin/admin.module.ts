import { Module } from '@nestjs/common';
import { AdminController } from './admin.controller';
import { AdminService } from './admin.service';
import { PasswordService } from '../../common/services/password.service';

@Module({
  controllers: [AdminController],
  providers: [AdminService, PasswordService],
})
export class AdminModule {}
