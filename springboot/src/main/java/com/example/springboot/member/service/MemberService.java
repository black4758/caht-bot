package com.example.springboot.member.service;

import com.example.springboot.global.exception.BusinessException;
import com.example.springboot.global.exception.ErrorCode;
import com.example.springboot.global.jwt.JwtTokenProvider;
import com.example.springboot.member.dto.TokenInfo;
import com.example.springboot.member.dto.LoginRequestDto;
import com.example.springboot.member.dto.PasswordChangeRequestDto;
import com.example.springboot.member.dto.PasswordResetRequestDto;
import com.example.springboot.member.dto.PasswordVerifyCodeRequestDto;
import com.example.springboot.member.dto.PasswordVerifyCodeResponseDto;
import com.example.springboot.member.dto.SignUpRequestDto;
import com.example.springboot.member.dto.SignUpResponseDto;
import com.example.springboot.member.dto.TokenRefreshResponseDto;
import com.example.springboot.member.entity.Member;
import com.example.springboot.member.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class MemberService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final RedisTemplate<String, String> redisTemplate;

    @Value("${jwt.access-token-expiration}")
    private long accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration;

    @Transactional
    public SignUpResponseDto signUp(SignUpRequestDto signUpRequestDto) {
        if (memberRepository.findByEmail(signUpRequestDto.getEmail()).isPresent()) {
            throw new BusinessException(ErrorCode.DUPLICATE_EMAIL);
        }

        String encodedPassword = passwordEncoder.encode(signUpRequestDto.getPassword());
        Member member = signUpRequestDto.toEntity(encodedPassword);

        Member savedMember = memberRepository.save(member);

        return new SignUpResponseDto(savedMember);
    }

    @Transactional
    public TokenInfo login(LoginRequestDto loginRequestDto) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        loginRequestDto.getEmail(),
                        loginRequestDto.getPassword()
                )
        );

        Member member = memberRepository.findByEmail(authentication.getName())
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        String accessToken = jwtTokenProvider.generateToken(member.getId(), member.getEmail(), member.getName(), accessTokenExpiration);
        String refreshToken = jwtTokenProvider.generateToken(member.getId(), member.getEmail(), member.getName(), refreshTokenExpiration);

        // Save refresh token to Redis
        redisTemplate.opsForValue().set(authentication.getName(), refreshToken, refreshTokenExpiration, TimeUnit.MILLISECONDS);

        return new TokenInfo(accessToken, accessTokenExpiration / 1000, refreshToken, member.getId(), member.getName(), member.getEmail());
    }

    public void logout(String refreshToken) {
        String email = jwtTokenProvider.getEmailFromToken(refreshToken);
        redisTemplate.delete(email);
    }

    public TokenRefreshResponseDto refreshToken(String refreshToken) {

        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new BusinessException(ErrorCode.INVALID_TOKEN);
        }

        String email = jwtTokenProvider.getEmailFromToken(refreshToken);
        String storedRefreshToken = redisTemplate.opsForValue().get(email);

        if (storedRefreshToken == null || !storedRefreshToken.equals(refreshToken)) {
            throw new BusinessException(ErrorCode.TOKEN_NOT_MATCH);
        }

        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        String newAccessToken = jwtTokenProvider.generateToken(member.getId(), member.getEmail(), member.getName(), accessTokenExpiration);
        String newRefreshToken = jwtTokenProvider.generateToken(member.getId(), member.getEmail(), member.getName(), refreshTokenExpiration);

        redisTemplate.opsForValue().set(email, newRefreshToken, refreshTokenExpiration, TimeUnit.MILLISECONDS);

        return new TokenRefreshResponseDto(newAccessToken, accessTokenExpiration / 1000);
    }

    @Transactional
    public void requestPasswordReset(PasswordResetRequestDto passwordResetRequestDto) {
        String email = passwordResetRequestDto.getEmail();
        String name = passwordResetRequestDto.getName();

        Optional<Member> memberOptional = memberRepository.findByEmail(email);
        if (memberOptional.isPresent()) {
            Member member = memberOptional.get();
            if (member.getName().equals(name)) {
                String verificationCode = UUID.randomUUID().toString().substring(0, 6);
                redisTemplate.opsForValue().set("password_reset:" + email, verificationCode, 5, TimeUnit.MINUTES);
                System.out.println("Password reset code for " + email + ": " + verificationCode);
            }
        }
        // Always return success to prevent user enumeration
    }

    public PasswordVerifyCodeResponseDto verifyPasswordResetCode(PasswordVerifyCodeRequestDto passwordVerifyCodeRequestDto) {
        String email = passwordVerifyCodeRequestDto.getEmail();
        String code = passwordVerifyCodeRequestDto.getCode();

        String storedCode = redisTemplate.opsForValue().get("password_reset:" + email);

        if (storedCode == null || !storedCode.equals(code)) {
            throw new BusinessException(ErrorCode.INVALID_VERIFICATION_CODE);
        }
        // Code is valid, remove it from Redis to prevent reuse
        redisTemplate.delete("password_reset:" + email);

        String resetToken = UUID.randomUUID().toString();
        redisTemplate.opsForValue().set("password_reset_token:" + resetToken, email, 10, TimeUnit.MINUTES); // Token valid for 10 minutes

        return new PasswordVerifyCodeResponseDto(resetToken);
    }

    @Transactional
    public void changePassword(String resetToken, PasswordChangeRequestDto passwordChangeRequestDto) {
        String newPassword = passwordChangeRequestDto.getNewPassword();

        String email = redisTemplate.opsForValue().get("password_reset_token:" + resetToken);
        if (email == null) {
            throw new BusinessException(ErrorCode.INVALID_RESET_TOKEN);
        }

        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        member.updatePassword(passwordEncoder.encode(newPassword));
        memberRepository.save(member);

        redisTemplate.delete("password_reset_token:" + resetToken);
    }
}