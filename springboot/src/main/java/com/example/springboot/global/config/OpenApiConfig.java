package com.example.springboot.global.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        Info info = new Info()
                .title("Demo Project API Document")
                .version("v0.0.1")
                .description("Demo project's API document.");

        String jwtSchemeName = "jwtAuth";
        // API Key-based authentication
        SecurityRequirement securityRequirement = new SecurityRequirement().addList(jwtSchemeName);
        // Components setting
        Components components = new Components()
                .addSecuritySchemes(jwtSchemeName, new SecurityScheme()
                        .name(jwtSchemeName)
                        .type(SecurityScheme.Type.HTTP) // HTTP type
                        .scheme("bearer")
                        .bearerFormat("JWT")); // Bearer token format

        return new OpenAPI()
                .info(info)
                .addSecurityItem(securityRequirement)
                .components(components);
    }
}
