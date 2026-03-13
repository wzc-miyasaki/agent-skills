name: springboot-tech-stack-analyzer
description: Analyzes Spring Boot project's technology stack by parsing Maven dependency tree and project file structure. Outputs a concise summary of frameworks, libraries, databases, middleware, and other technologies used in the project. TRIGGER when: user provides Maven dependency tree output (mvn dependency:tree) and/or project file structure (tree/ls -R output) and asks to summarize the tech stack.

# SpringBoot Tech Stack Analyzer

## Overview

This skill analyzes a Spring Boot project's technology stack by parsing:
1. Maven dependency tree output (`mvn dependency:tree`)
2. Project file structure (`tree` or `ls -R`)

It outputs a concise summary of all technologies used in the project directly to stdout.

## Usage

Provide the dependency tree and/or file structure output, then ask Claude to analyze it.

**Example user input:**
```
Here's my mvn dependency:tree output:
[dependency tree output...]

And my project structure:
[tree output...]

What's the tech stack?
```

## Analysis Process

### Step 1: Parse Maven Dependencies

Extract and categorize dependencies by group ID patterns:

| Category | Group ID Patterns | Examples |
|----------|------------------|----------|
| **Spring Boot** | `org.springframework.boot:*` | spring-boot-starter-web, spring-boot-starter-data-jpa |
| **Spring Framework** | `org.springframework:*` | spring-web, spring-data-jpa |
| **Database** | `mysql:mysql-connector-java`, `org.postgresql:*`, `com.h2database:*` | MySQL, PostgreSQL, H2 |
| **JPA/Hibernate** | `org.hibernate:*`, `jakarta.persistence:*` | Hibernate, JPA |
| **MyBatis** | `org.mybatis:*`, `org.mybatis.spring.boot:*` | MyBatis, MyBatis-Plus |
| **Redis** | `org.springframework.boot:spring-boot-starter-data-redis`, `io.lettuce:*` | Redis, Lettuce |
| **MQ** | `org.apache.kafka:*`, `org.springframework.amqp:*`, `com.rabbitmq:*` | Kafka, RabbitMQ |
| **Cache** | `org.springframework.boot:spring-boot-starter-cache`, `com.github.ben-manes.caffeine:*` | Caffeine, Ehcache |
| **Security** | `org.springframework.boot:spring-boot-starter-security`, `org.springframework.security:*` | Spring Security |
| **Validation** | `org.hibernate.validator:*`, `jakarta.validation:*` | Hibernate Validator |
| **JSON/Serialization** | `com.fasterxml.jackson:*`, `com.alibaba.fastjson2:*` | Jackson, Fastjson2 |
| **Logging** | `org.slf4j:*`, `ch.qos.logback:*`, `org.apache.logging.log4j:*` | Logback, Log4j2 |
| **Testing** | `org.junit:*`, `org.mockito:*`, `org.springframework.boot:spring-boot-starter-test` | JUnit, Mockito |
| **Lombok** | `org.projectlombok:*` | Lombok |
| **Swagger/OpenAPI** | `org.springdoc:*`, `io.springfox:*` | SpringDoc, Swagger |
| **Alibaba** | `com.alibaba.cloud:*`, `com.alibaba.nacos:*` | Nacos, Sentinel, Seata |
| **Tencent** | `com.tencent.cloud:*` | Tencent Cloud |
| **AWS** | `com.amazonaws:*`, `software.amazon.awssdk:*` | AWS SDK |
| **Monitoring** | `io.micrometer:*`, `org.springframework.boot:spring-boot-starter-actuator` | Micrometer, Actuator |

### Step 2: Parse File Structure

Identify technologies from file patterns:

| File Pattern | Technology Indication |
|-------------|----------------------|
| `pom.xml` | Maven project |
| `build.gradle` | Gradle project |
| `application.yml` / `application.properties` | Spring Boot configuration |
| `*.sql` files | Database migrations |
| `flyway/` directory | Flyway migrations |
| `liquibase/` directory | Liquibase migrations |
| `docker-compose.yml` | Docker Compose setup |
| `Dockerfile` | Docker container |
| `k8s/` or `kubernetes/` | Kubernetes manifests |
| `src/main/resources/mapper/*.xml` | MyBatis XML mappers |
| `src/main/java/**/*Controller.java` | Spring MVC Controllers |
| `src/main/java/**/*Service.java` | Service layer |
| `src/main/java/**/*Repository.java` | Repository/JPA layer |
| `src/main/java/**/*Mapper.java` | MyBatis Mapper |

### Step 3: Generate Summary Output

Output format (stdout):

```markdown
## SpringBoot Project Tech Stack Summary

**Project Type:** Spring Boot [version]

### Core Framework
- Spring Boot: [version]
- Spring Framework: [version]

### Web & API
- [Spring Web MVC / WebFlux / Actuator / etc.]

### Database & Persistence
- **Database:** [MySQL / PostgreSQL / H2 / MongoDB / etc.]
- **ORM:** [JPA+Hibernate / MyBatis / MyBatis-Plus / etc.]
- **Migration:** [Flyway / Liquibase / none]

### Middleware & Integration
- **Cache:** [Redis / Caffeine / Ehcache / none]
- **Message Queue:** [Kafka / RabbitMQ / none]
- **Config Center:** [Nacos / Apollo / none]

### Additional Libraries
- **JSON:** [Jackson / Fastjson2]
- **Validation:** [Hibernate Validator]
- **Security:** [Spring Security / none]
- **Documentation:** [SpringDoc OpenAPI / Swagger]
- **Monitoring:** [Micrometer + Prometheus / Actuator]
- **Utility:** [Lombok / MapStruct / etc.]

### Infrastructure
- **Build Tool:** Maven
- **Containerization:** [Docker / none]
- **Orchestration:** [Kubernetes / none]

### Testing
- [JUnit 5 / Mockito / Testcontainers / etc.]

---
**Total Dependencies:** [count]
**Main Technologies:** [list top 10]
```

## Examples

### Example 1: Typical Web Application

**Input:**
```
mvn dependency:tree output:
[+- org.springframework.boot:spring-boot-starter-web:jar:3.2.0
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:3.2.0
+- mysql:mysql-connector-java:jar:8.0.33
+- org.springframework.boot:spring-boot-starter-data-redis:jar:3.2.0
+- org.projectlombok:lombok:jar:1.18.30
+- com.alibaba.fastjson2:fastjson2:jar:2.0.43]
```

**Output:**
```markdown
## SpringBoot Project Tech Stack Summary

**Project Type:** Spring Boot Web Application (3.2.0)

### Core Framework
- Spring Boot: 3.2.0
- Spring Framework: 6.x

### Web & API
- Spring Web MVC
- Spring Data JPA

### Database & Persistence
- **Database:** MySQL 8.0.33
- **ORM:** JPA + Hibernate
- **Migration:** None detected

### Middleware & Integration
- **Cache:** Redis
- **Message Queue:** None detected
- **Config Center:** None detected

### Additional Libraries
- **JSON:** Fastjson2 2.0.43
- **Validation:** Hibernate Validator (included)
- **Security:** None detected
- **Documentation:** None detected
- **Monitoring:** None detected
- **Utility:** Lombok 1.18.30

### Infrastructure
- **Build Tool:** Maven
- **Containerization:** Not detected
- **Orchestration:** Not detected

### Testing
- Not detected in dependencies

---
**Total Dependencies:** 6 main libraries
**Main Technologies:** Spring Boot, Spring Web MVC, Spring Data JPA, MySQL, Redis, Lombok, Fastjson2
```

## Implementation Notes

- Prioritize extracting version numbers from dependency coordinates
- Group similar technologies together (e.g., all Spring projects)
- Mark "None detected" for categories with no matches
- Keep output concise and scannable
- Focus on production dependencies (scope: compile/runtime)
- Ignore test-only dependencies unless specifically requested
