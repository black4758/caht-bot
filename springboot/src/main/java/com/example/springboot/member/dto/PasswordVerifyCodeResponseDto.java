package com.example.springboot.member.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class PasswordVerifyCodeResponseDto {

    private String resetToken;
}
