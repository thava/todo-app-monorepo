import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService as NestJwtService } from '@nestjs/jwt';

export interface AccessTokenPayload {
  sub: string; // user.id
  email: string;
  role: 'guest' | 'admin' | 'sysadmin';
}

export interface RefreshTokenPayload {
  sub: string; // user.id
  sessionId: string; // refresh_token_sessions.id
}

@Injectable()
export class TokenService {
  constructor(
    private readonly jwtService: NestJwtService,
    private readonly configService: ConfigService,
  ) {}

  /**
   * Generate access token (short-lived)
   */
  async generateAccessToken(payload: AccessTokenPayload): Promise<string> {
    return this.jwtService.signAsync(payload as any, {
      secret: this.configService.get<string>('jwt.accessSecret'),
      expiresIn: this.configService.get<string>('jwt.accessExpiry') as any,
    });
  }

  /**
   * Generate refresh token (long-lived)
   */
  async generateRefreshToken(payload: RefreshTokenPayload): Promise<string> {
    return this.jwtService.signAsync(payload as any, {
      secret: this.configService.get<string>('jwt.refreshSecret'),
      expiresIn: this.configService.get<string>('jwt.refreshExpiry') as any,
    });
  }

  /**
   * Verify and decode access token
   */
  async verifyAccessToken(token: string): Promise<AccessTokenPayload> {
    return this.jwtService.verifyAsync<AccessTokenPayload>(token, {
      secret: this.configService.get<string>('jwt.accessSecret'),
    });
  }

  /**
   * Verify and decode refresh token
   */
  async verifyRefreshToken(token: string): Promise<RefreshTokenPayload> {
    return this.jwtService.verifyAsync<RefreshTokenPayload>(token, {
      secret: this.configService.get<string>('jwt.refreshSecret'),
    });
  }

  /**
   * Decode token without verification (for debugging)
   */
  decodeToken(token: string): any {
    return this.jwtService.decode(token);
  }
}
