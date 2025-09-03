package com.example.springboot.member.controller;

import com.example.springboot.member.dto.LoginRequestDto;
import com.example.springboot.member.dto.LoginResponseDto;

import com.example.springboot.member.dto.PasswordChangeRequestDto;
import com.example.springboot.member.dto.PasswordResetRequestDto;
import com.example.springboot.member.dto.PasswordVerifyCodeRequestDto;
import com.example.springboot.member.dto.PasswordVerifyCodeResponseDto;
import com.example.springboot.member.dto.SignUpRequestDto;
import com.example.springboot.member.dto.SignUpResponseDto;
import com.example.springboot.member.dto.TokenInfo;
import com.example.springboot.member.dto.TokenRefreshResponseDto;
import com.example.springboot.member.service.MemberService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;

    @PostMapping("/signup")
    public ResponseEntity<SignUpResponseDto> signUp(@Valid @RequestBody SignUpRequestDto signUpRequestDto) {
        SignUpResponseDto signUpResponseDto = memberService.signUp(signUpRequestDto);
        return ResponseEntity.created(URI.create("/members/" + signUpResponseDto.getId()))
                .body(signUpResponseDto);
    }

    @PostMapping("/login")
    public ResponseEntity<LoginResponseDto> login(@Valid @RequestBody LoginRequestDto loginRequestDto) {
        TokenInfo tokenInfo = memberService.login(loginRequestDto);

        ResponseCookie cookie = ResponseCookie.from("refreshToken", tokenInfo.getRefreshToken())
                .httpOnly(true)
                .secure(true)
                .path("/")
                .maxAge(60 * 60 * 24 * 14) // 2 weeks
                .build();

        LoginResponseDto loginResponseDto = new LoginResponseDto(tokenInfo.getMemberId(), tokenInfo.getMemberName(), tokenInfo.getMemberEmail());

        return ResponseEntity.ok()
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + tokenInfo.getAccessToken())
                .header(HttpHeaders.SET_COOKIE, cookie.toString())
                .body(loginResponseDto);
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@CookieValue("refreshToken") String refreshToken) {
        memberService.logout(refreshToken);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/token/refresh")
    public ResponseEntity<TokenRefreshResponseDto> refreshToken(@CookieValue("refreshToken") String refreshToken) {
        TokenRefreshResponseDto tokenRefreshResponseDto = memberService.refreshToken(refreshToken);
        return ResponseEntity.ok(tokenRefreshResponseDto);
    }

    @PostMapping("/password/reset-request")
    public ResponseEntity<Void> requestPasswordReset(@Valid @RequestBody PasswordResetRequestDto passwordResetRequestDto) {
        memberService.requestPasswordReset(passwordResetRequestDto);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/password/verify-code")
    public ResponseEntity<PasswordVerifyCodeResponseDto> verifyPasswordResetCode(@Valid @RequestBody PasswordVerifyCodeRequestDto passwordVerifyCodeRequestDto) {
        PasswordVerifyCodeResponseDto response = memberService.verifyPasswordResetCode(passwordVerifyCodeRequestDto);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/password/change")
    public ResponseEntity<Void> changePassword(@RequestHeader("X-Reset-Token") String resetToken, @Valid @RequestBody PasswordChangeRequestDto passwordChangeRequestDto) {
        memberService.changePassword(resetToken, passwordChangeRequestDto);
        return ResponseEntity.noContent().build();
    }
}
