package com.example.springboot.member.dto;

import com.example.springboot.member.entity.Member;
import lombok.Getter;

@Getter
public class SignUpResponseDto {

    private final Long id;
    private final String email;
    private final String name;

    public SignUpResponseDto(Member member) {
        this.id = member.getId();
        this.email = member.getEmail();
        this.name = member.getName();
    }
}
