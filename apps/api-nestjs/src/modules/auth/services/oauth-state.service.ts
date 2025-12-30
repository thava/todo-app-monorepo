import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { sign, verify, JwtPayload } from 'jsonwebtoken';

export interface OAuthState {
  redirect: string;
  frontend: string;
  mode: 'login' | 'link';
  current_user_id?: string;
  iat: number;
  exp: number;
}

@Injectable()
export class OAuthStateService {
  private readonly stateSecret: string;
  private readonly stateExpirySeconds = 300; // 5 minutes

  constructor(private readonly configService: ConfigService) {
    this.stateSecret = this.configService.get<string>('API_SERVER_OAUTH_KEY') || '';
    if (!this.stateSecret) {
      throw new Error('API_SERVER_OAUTH_KEY must be configured for OAuth');
    }
  }

  /**
   * Create a signed OAuth state parameter
   */
  createState(params: {
    redirect: string;
    frontend: string;
    mode: 'login' | 'link';
    currentUserId?: string;
  }): string {
    const now = Math.floor(Date.now() / 1000);

    const payload: OAuthState = {
      redirect: params.redirect,
      frontend: params.frontend,
      mode: params.mode,
      iat: now,
      exp: now + this.stateExpirySeconds,
    };

    if (params.mode === 'link' && params.currentUserId) {
      payload.current_user_id = params.currentUserId;
    }

    return sign(payload, this.stateSecret);
  }

  /**
   * Verify and decode OAuth state parameter
   */
  verifyState(state: string): OAuthState {
    try {
      const decoded = verify(state, this.stateSecret) as JwtPayload;
      return decoded as OAuthState;
    } catch (error) {
      throw new Error('Invalid or expired OAuth state');
    }
  }
}
