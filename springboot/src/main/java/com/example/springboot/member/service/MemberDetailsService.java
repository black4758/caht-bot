package com.example.springboot.member.service;

import com.example.springboot.member.entity.Member;
import com.example.springboot.member.entity.MemberDetails;
import com.example.springboot.member.repository.MemberRepository;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class MemberDetailsService implements UserDetailsService {

    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;

    public MemberDetailsService(MemberRepository memberRepository, @Lazy PasswordEncoder passwordEncoder) {
        this.memberRepository = memberRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Member member = memberRepository.findByEmail(email)
                .orElseGet(() -> {
                    // Dummy user for security to prevent user enumeration
                    String dummyPassword = passwordEncoder.encode(UUID.randomUUID().toString());
                    return Member.builder()
                            .email(email)
                            .password(dummyPassword)
                            .name("dummy_user") // Or any placeholder name
                            .build();
                });
        return new MemberDetails(member);
    }
}
