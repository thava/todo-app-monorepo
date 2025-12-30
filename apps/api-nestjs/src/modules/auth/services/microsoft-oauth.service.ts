import { Injectable, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

export interface MicrosoftTokenResponse {
  access_token: string;
  expires_in: number;
  scope: string;
  token_type: string;
  id_token: string;
  refresh_token?: string;
}

export interface MicrosoftUserInfo {
  oid: string;
  tid: string;
  sub: string;
  email: string;
  name: string;
  preferred_username?: string;
}

@Injectable()
export class MicrosoftOAuthService {
  private readonly clientId: string;
  private readonly clientSecret: string;
  private readonly authorizationEndpoint = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize';
  private readonly tokenEndpoint = 'https://login.microsoftonline.com/common/oauth2/v2.0/token';

  constructor(private readonly configService: ConfigService) {
    this.clientId = this.configService.get<string>('MS_OAUTH_CLIENT_ID') || '';
    this.clientSecret = this.configService.get<string>('MS_OAUTH_CLIENT_SECRET') || '';

    if (!this.clientId || !this.clientSecret) {
      throw new Error('Microsoft OAuth credentials must be configured');
    }
  }

  /**
   * Get the redirect URI for OAuth callback
   */
  getRedirectUri(): string {
    const apiUrl = this.configService.get<string>('NESTJS_API_URL') || 'http://localhost:3000';
    return `${apiUrl}/oauth/microsoft/callback`;
  }

  /**
   * Build Microsoft authorization URL
   */
  getAuthorizationUrl(state: string): string {
    const params = new URLSearchParams({
      client_id: this.clientId,
      response_type: 'code',
      redirect_uri: this.getRedirectUri(),
      scope: 'openid profile email',
      state: state,
      response_mode: 'query',
    });

    return `${this.authorizationEndpoint}?${params.toString()}`;
  }

  /**
   * Exchange authorization code for tokens
   */
  async exchangeCodeForTokens(code: string): Promise<MicrosoftTokenResponse> {
    const params = new URLSearchParams({
      code,
      client_id: this.clientId,
      client_secret: this.clientSecret,
      redirect_uri: this.getRedirectUri(),
      grant_type: 'authorization_code',
    });

    const response = await fetch(this.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new BadRequestException(`Failed to exchange code for tokens: ${error}`);
    }

    return response.json();
  }

  /**
   * Decode and extract Microsoft ID token claims (basic decoding)
   * In production, use a library like passport-azure-ad for proper verification
   */
  decodeIdToken(idToken: string): MicrosoftUserInfo {
    try {
      const parts = idToken.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid ID token format');
      }

      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64url').toString('utf-8')
      );

      return {
        oid: payload.oid,
        tid: payload.tid,
        sub: payload.sub,
        email: payload.email || payload.preferred_username || '',
        name: payload.name,
        preferred_username: payload.preferred_username,
      };
    } catch (error) {
      throw new BadRequestException('Failed to decode ID token');
    }
  }

  /**
   * Get user info from Microsoft OAuth
   */
  async getUserInfo(code: string): Promise<MicrosoftUserInfo> {
    const tokens = await this.exchangeCodeForTokens(code);
    return this.decodeIdToken(tokens.id_token);
  }
}
