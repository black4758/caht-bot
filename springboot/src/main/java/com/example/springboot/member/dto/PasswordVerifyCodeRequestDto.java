package com.example.springboot.member.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class PasswordVerifyCodeRequestDto {

    @Email
    @NotBlank
    private String email;

    @NotBlank
    private String code;
}
