import {
  Controller,
  Get,
  Post,
  Body,
  Query,
  Res,
  Req,
  Ip,
  UseGuards,
  UnauthorizedException,
  BadRequestException,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import type { Request, Response } from 'express';
import { AuthService } from './auth.service';
import { OAuthStateService } from './services/oauth-state.service';
import { GoogleOAuthService } from './services/google-oauth.service';
import { MicrosoftOAuthService } from './services/microsoft-oauth.service';
import { GetCurrentUser } from '../../common/decorators/current-user.decorator';
import { Public } from '../../common/decorators/public.decorator';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { TokenService } from '../../common/services/jwt.service';
import type { AccessTokenPayload } from '../../common/services/jwt.service';

@ApiTags('oauth')
@Controller('oauth')
export class OAuthController {
  constructor(
    private readonly authService: AuthService,
    private readonly tokenService: TokenService,
    private readonly oauthStateService: OAuthStateService,
    private readonly googleOAuthService: GoogleOAuthService,
    private readonly microsoftOAuthService: MicrosoftOAuthService,
  ) {}

  @Public()
  @Get('google/login')
  @ApiOperation({
    summary: 'Initiate Google OAuth login flow',
    description: 'Redirects to Google OAuth authorization endpoint',
  })
  async googleLogin(
    @Query('redirect') redirect: string,
    @Query('frontend') frontend: string,
    @Res() res: Response,
  ): Promise<void> {
    if (!redirect || !frontend) {
      throw new BadRequestException('redirect and frontend query parameters are required');
    }

    const state = this.oauthStateService.createState({
      redirect,
      frontend,
      mode: 'login',
    });

    const authorizationUrl = this.googleOAuthService.getAuthorizationUrl(state);
    res.redirect(authorizationUrl);
  }

  @Public()
  @Post('google/link')
  @ApiOperation({
    summary: 'Initiate Google OAuth account linking flow',
    description: 'Redirects to Google OAuth to link Google account to current user. Requires access_token in request body.',
  })
  async googleLink(
    @Body() body: { redirect: string; frontend: string; access_token: string },
    @Res() res: Response,
  ): Promise<void> {
    if (!body.redirect || !body.frontend) {
      throw new BadRequestException('redirect and frontend fields are required');
    }

    if (!body.access_token) {
      throw new UnauthorizedException('access_token field is required for account linking');
    }

    // Verify the access token and extract user ID
    let userId: string;
    try {
      const payload = await this.tokenService.verifyAccessToken(body.access_token);
      userId = payload.sub;
    } catch (error) {
      throw new UnauthorizedException('Invalid or expired access token');
    }

    const state = this.oauthStateService.createState({
      redirect: body.redirect,
      frontend: body.frontend,
      mode: 'link',
      currentUserId: userId,
    });

    const authorizationUrl = this.googleOAuthService.getAuthorizationUrl(state);
    res.redirect(authorizationUrl);
  }

  @Public()
  @Get('google/callback')
  @ApiOperation({
    summary: 'Google OAuth callback endpoint',
    description: 'Handles the OAuth callback from Google',
  })
  async googleCallback(
    @Query('code') code: string,
    @Query('state') stateParam: string,
    @Req() req: Request,
    @Ip() ip: string,
    @Res() res: Response,
  ): Promise<void> {
    // Default redirect URL in case state is invalid
    let redirectUrl = 'http://localhost:4000/auth-complete';

    try {
      if (!code || !stateParam) {
        throw new BadRequestException('code and state query parameters are required');
      }

      const userAgent = req.headers['user-agent'];
      const state = this.oauthStateService.verifyState(stateParam);
      redirectUrl = state.redirect; // Use redirect from state

      const googleUserInfo = await this.googleOAuthService.getUserInfo(code);

      if (state.mode === 'login') {
        const authResponse = await this.authService.loginWithGoogle(
          googleUserInfo.sub,
          googleUserInfo.email,
          googleUserInfo.name,
          userAgent,
          ip,
        );

        redirectUrl = `${state.redirect}#access_token=${authResponse.accessToken}&refresh_token=${authResponse.refreshToken}`;
        res.redirect(redirectUrl);
      } else if (state.mode === 'link') {
        if (!state.current_user_id) {
          throw new UnauthorizedException('User ID required for account linking');
        }

        await this.authService.linkGoogleIdentity(
          state.current_user_id,
          googleUserInfo.sub,
          googleUserInfo.email,
          ip,
          userAgent,
        );

        redirectUrl = `${state.redirect}#status=linked&provider=google`;
        res.redirect(redirectUrl);
      }
    } catch (error) {
      // Always redirect to frontend with error information
      const errorCode = error.status || 500;
      const errorMessage = error.message || 'OAuth authentication failed';
      const encodedMessage = encodeURIComponent(errorMessage);

      redirectUrl = `${redirectUrl}#error=${errorCode}&message=${encodedMessage}`;
      res.redirect(redirectUrl);
    }
  }

  @Public()
  @Get('microsoft/login')
  @ApiOperation({
    summary: 'Initiate Microsoft OAuth login flow',
    description: 'Redirects to Microsoft OAuth authorization endpoint',
  })
  async microsoftLogin(
    @Query('redirect') redirect: string,
    @Query('frontend') frontend: string,
    @Res() res: Response,
  ): Promise<void> {
    if (!redirect || !frontend) {
      throw new BadRequestException('redirect and frontend query parameters are required');
    }

    const state = this.oauthStateService.createState({
      redirect,
      frontend,
      mode: 'login',
    });

    const authorizationUrl = this.microsoftOAuthService.getAuthorizationUrl(state);
    res.redirect(authorizationUrl);
  }

  @Public()
  @Post('microsoft/link')
  @ApiOperation({
    summary: 'Initiate Microsoft OAuth account linking flow',
    description: 'Redirects to Microsoft OAuth to link Microsoft account to current user. Requires access_token in request body.',
  })
  async microsoftLink(
    @Body() body: { redirect: string; frontend: string; access_token: string },
    @Res() res: Response,
  ): Promise<void> {
    if (!body.redirect || !body.frontend) {
      throw new BadRequestException('redirect and frontend fields are required');
    }

    if (!body.access_token) {
      throw new UnauthorizedException('access_token field is required for account linking');
    }

    // Verify the access token and extract user ID
    let userId: string;
    try {
      const payload = await this.tokenService.verifyAccessToken(body.access_token);
      userId = payload.sub;
    } catch (error) {
      throw new UnauthorizedException('Invalid or expired access token');
    }

    const state = this.oauthStateService.createState({
      redirect: body.redirect,
      frontend: body.frontend,
      mode: 'link',
      currentUserId: userId,
    });

    const authorizationUrl = this.microsoftOAuthService.getAuthorizationUrl(state);
    res.redirect(authorizationUrl);
  }

  @Public()
  @Get('microsoft/callback')
  @ApiOperation({
    summary: 'Microsoft OAuth callback endpoint',
    description: 'Handles the OAuth callback from Microsoft',
  })
  async microsoftCallback(
    @Query('code') code: string,
    @Query('state') stateParam: string,
    @Req() req: Request,
    @Ip() ip: string,
    @Res() res: Response,
  ): Promise<void> {
    // Default redirect URL in case state is invalid
    let redirectUrl = 'http://localhost:4000/auth-complete';

    try {
      if (!code || !stateParam) {
        throw new BadRequestException('code and state query parameters are required');
      }

      const userAgent = req.headers['user-agent'];
      const state = this.oauthStateService.verifyState(stateParam);
      redirectUrl = state.redirect; // Use redirect from state

      const msUserInfo = await this.microsoftOAuthService.getUserInfo(code);

      if (state.mode === 'login') {
        const authResponse = await this.authService.loginWithMicrosoft(
          msUserInfo.oid,
          msUserInfo.tid,
          msUserInfo.email,
          msUserInfo.name,
          userAgent,
          ip,
        );

        redirectUrl = `${state.redirect}#access_token=${authResponse.accessToken}&refresh_token=${authResponse.refreshToken}`;
        res.redirect(redirectUrl);
      } else if (state.mode === 'link') {
        if (!state.current_user_id) {
          throw new UnauthorizedException('User ID required for account linking');
        }

        await this.authService.linkMicrosoftIdentity(
          state.current_user_id,
          msUserInfo.oid,
          msUserInfo.tid,
          msUserInfo.email,
          ip,
          userAgent,
        );

        redirectUrl = `${state.redirect}#status=linked&provider=microsoft`;
        res.redirect(redirectUrl);
      }
    } catch (error) {
      // Always redirect to frontend with error information
      const errorCode = error.status || 500;
      const errorMessage = error.message || 'OAuth authentication failed';
      const encodedMessage = encodeURIComponent(errorMessage);

      redirectUrl = `${redirectUrl}#error=${errorCode}&message=${encodedMessage}`;
      res.redirect(redirectUrl);
    }
  }

  @Post('google/unlink')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiBearerAuth()
  @ApiOperation({
    summary: 'Unlink Google account from current user',
    description: 'Removes Google identity from current user account. Requires at least one other identity to remain.',
  })
  @ApiResponse({ status: 204, description: 'Google account unlinked successfully' })
  @ApiResponse({ status: 400, description: 'Cannot unlink - user must have at least one identity' })
  @ApiResponse({ status: 404, description: 'Google account not linked' })
  async unlinkGoogle(
    @GetCurrentUser('userId') userId: string,
    @Req() req: Request,
    @Ip() ip: string,
  ): Promise<void> {
    const userAgent = req.headers['user-agent'];
    await this.authService.unlinkGoogleIdentity(userId, ip, userAgent);
  }

  @Post('microsoft/unlink')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiBearerAuth()
  @ApiOperation({
    summary: 'Unlink Microsoft account from current user',
    description: 'Removes Microsoft identity from current user account. Requires at least one other identity to remain.',
  })
  @ApiResponse({ status: 204, description: 'Microsoft account unlinked successfully' })
  @ApiResponse({ status: 400, description: 'Cannot unlink - user must have at least one identity' })
  @ApiResponse({ status: 404, description: 'Microsoft account not linked' })
  async unlinkMicrosoft(
    @GetCurrentUser('userId') userId: string,
    @Req() req: Request,
    @Ip() ip: string,
  ): Promise<void> {
    const userAgent = req.headers['user-agent'];
    await this.authService.unlinkMicrosoftIdentity(userId, ip, userAgent);
  }
}
