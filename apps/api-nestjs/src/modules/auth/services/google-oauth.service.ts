import { Injectable, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

export interface GoogleTokenResponse {
  access_token: string;
  expires_in: number;
  scope: string;
  token_type: string;
  id_token: string;
  refresh_token?: string;
}

export interface GoogleUserInfo {
  sub: string;
  email: string;
  email_verified: boolean;
  name: string;
  picture?: string;
  given_name?: string;
  family_name?: string;
}

@Injectable()
export class GoogleOAuthService {
  private readonly clientId: string;
  private readonly clientSecret: string;
  private readonly authorizationEndpoint = 'https://accounts.google.com/o/oauth2/v2/auth';
  private readonly tokenEndpoint = 'https://oauth2.googleapis.com/token';

  constructor(private readonly configService: ConfigService) {
    this.clientId = this.configService.get<string>('GOOGLE_OAUTH_CLIENT_ID') || '';
    this.clientSecret = this.configService.get<string>('GOOGLE_OAUTH_CLIENT_SECRET') || '';

    if (!this.clientId || !this.clientSecret) {
      throw new Error('Google OAuth credentials must be configured');
    }
  }

  /**
   * Get the redirect URI for OAuth callback
   */
  getRedirectUri(): string {
    const apiUrl = this.configService.get<string>('NESTJS_API_URL') || 'http://localhost:3000';
    return `${apiUrl}/oauth/google/callback`;
  }

  /**
   * Build Google authorization URL
   */
  getAuthorizationUrl(state: string): string {
    const params = new URLSearchParams({
      client_id: this.clientId,
      response_type: 'code',
      redirect_uri: this.getRedirectUri(),
      scope: 'openid profile email',
      state: state,
      access_type: 'offline',
      // prompt: 'consent',
    });

    return `${this.authorizationEndpoint}?${params.toString()}`;
  }

  /**
   * Exchange authorization code for tokens
   */
  async exchangeCodeForTokens(code: string): Promise<GoogleTokenResponse> {
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
   * Decode and verify Google ID token (basic decoding without full verification)
   * In production, use a library like google-auth-library for proper verification
   */
  decodeIdToken(idToken: string): GoogleUserInfo {
    try {
      const parts = idToken.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid ID token format');
      }

      const payload = JSON.parse(
        Buffer.from(parts[1], 'base64url').toString('utf-8')
      );

      return {
        sub: payload.sub,
        email: payload.email,
        email_verified: payload.email_verified || false,
        name: payload.name,
        picture: payload.picture,
        given_name: payload.given_name,
        family_name: payload.family_name,
      };
    } catch (error) {
      throw new BadRequestException('Failed to decode ID token');
    }
  }

  /**
   * Get user info from Google OAuth
   */
  async getUserInfo(code: string): Promise<GoogleUserInfo> {
    const tokens = await this.exchangeCodeForTokens(code);
    return this.decodeIdToken(tokens.id_token);
  }
}
