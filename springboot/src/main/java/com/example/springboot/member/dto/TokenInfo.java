package com.example.springboot.member.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class TokenInfo {

    private String accessToken;
    private Long expiresIn;
    private String refreshToken;
    private Long memberId;
    private String memberName;
    private String memberEmail;
}
