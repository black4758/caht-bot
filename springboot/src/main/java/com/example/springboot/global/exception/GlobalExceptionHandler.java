package com.example.springboot.global.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.AuthenticationException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponseDto> handleBusinessException(BusinessException ex) {
        ErrorCode errorCode = ex.getErrorCode();
        ErrorResponseDto response = new ErrorResponseDto(errorCode.getHttpStatus().value(), errorCode.name(), errorCode.getMessage());
        log.warn("BusinessException: {}, URL: {}", errorCode.getMessage(), /* request.getRequestURI() */ ""); // Consider adding request details
        return new ResponseEntity<>(response, errorCode.getHttpStatus());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDto> handleMethodArgumentNotValidException(MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));

        ErrorCode errorCode = ErrorCode.INVALID_INPUT_VALUE;
        ErrorResponseDto response = new ErrorResponseDto(errorCode.getHttpStatus().value(), errorCode.name(), errorMessage);
        log.warn("ValidationException: {}", errorMessage);
        return new ResponseEntity<>(response, errorCode.getHttpStatus());
    }

    // 기존의 다른 핸들러들은 유지하거나 필요에 따라 추가할 수 있습니다.
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponseDto> handleIllegalArgumentException(IllegalArgumentException ex) {
        ErrorResponseDto errorResponse = new ErrorResponseDto(HttpStatus.BAD_REQUEST.value(), "ILLEGAL_ARGUMENT", ex.getMessage());
        return new ResponseEntity<>(errorResponse, org.springframework.http.HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ErrorResponseDto> handleAuthenticationException(AuthenticationException ex) {
        ErrorCode errorCode = ErrorCode.LOGIN_FAILED;
        ErrorResponseDto response = new ErrorResponseDto(errorCode.getHttpStatus().value(), errorCode.name(), errorCode.getMessage());
        log.warn("AuthenticationException: {}", ex.getMessage());
        return new ResponseEntity<>(response, errorCode.getHttpStatus());
    }
}