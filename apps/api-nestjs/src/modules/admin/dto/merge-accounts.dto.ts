import { ApiProperty } from '@nestjs/swagger';
import { IsUUID } from 'class-validator';

export class MergeAccountsDto {
  @ApiProperty({
    description: 'Source user ID (will be deleted after merge)',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsUUID()
  sourceUserId: string;

  @ApiProperty({
    description: 'Destination user ID (will receive merged identities)',
    example: '660e8400-e29b-41d4-a716-446655440111',
  })
  @IsUUID()
  destinationUserId: string;
}

export class MergeAccountsResponseDto {
  @ApiProperty({ description: 'Success message' })
  message: string;

  @ApiProperty({ description: 'Destination user ID' })
  destinationUserId: string;

  @ApiProperty({ description: 'Identities merged from source' })
  mergedIdentities: {
    local?: boolean;
    google?: boolean;
    microsoft?: boolean;
  };
}
