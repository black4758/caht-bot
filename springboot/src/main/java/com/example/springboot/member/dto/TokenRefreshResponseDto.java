package com.example.springboot.member.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class TokenRefreshResponseDto {

    private String accessToken;
    private Long expiresIn;
}