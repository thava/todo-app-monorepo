import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { AuthController } from './auth.controller';
import { OAuthController } from './oauth.controller';
import { AuthService } from './auth.service';
import { PasswordService } from '../../common/services/password.service';
import { TokenService } from '../../common/services/jwt.service';
import { JwtStrategy } from '../../common/strategies/jwt.strategy';
import { OAuthStateService } from './services/oauth-state.service';
import { GoogleOAuthService } from './services/google-oauth.service';
import { MicrosoftOAuthService } from './services/microsoft-oauth.service';

@Module({
  imports: [
    PassportModule,
    JwtModule.register({
      global: true,
    }),
  ],
  controllers: [AuthController, OAuthController],
  providers: [
    AuthService,
    PasswordService,
    TokenService,
    JwtStrategy,
    OAuthStateService,
    GoogleOAuthService,
    MicrosoftOAuthService,
  ],
  exports: [AuthService, PasswordService, TokenService],
})
export class AuthModule {}
