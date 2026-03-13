# 高级分析模式

## 目录

- [跨服务调用分析](#跨服务调用分析)
- [复杂业务流程分析](#复杂业务流程分析)
- [Spring Boot 常见模式识别](#spring-boot-常见模式识别)
- [代码搜索速查](#代码搜索速查)

## 跨服务调用分析

当业务逻辑涉及多个微服务时：

1. 识别 Feign Client / RestTemplate / WebClient 调用
2. 搜索模式：
   - `@FeignClient` 注解定义的接口
   - `RestTemplate` 或 `WebClient` 的 `.exchange()`, `.getForObject()` 等调用
   - `@DubboReference`, `@GrpcClient` 等 RPC 注解
3. 记录调用方向、参数、返回值
4. 标注跨服务事务边界（分布式事务 / 最终一致性）

## 复杂业务流程分析

### 状态机模式
```
搜索：enum.*Status, enum.*State
追踪：所有对 status/state 字段的赋值语句
构建：状态转换图（当前状态 × 动作 → 目标状态）
```

### 策略模式
```
搜索：implements.*Strategy, @Component + 接口实现
识别：策略选择条件（工厂方法中的 if/switch/map）
列出：每种策略的业务语义
```

### 模板方法模式
```
搜索：abstract class + protected abstract 方法
识别：固定流程步骤 vs 可变步骤
列出：各子类对可变步骤的实现差异
```

### 事件驱动模式
```
搜索：@EventListener, ApplicationEventPublisher, @TransactionalEventListener
追踪：事件发布 → 事件处理的完整链路
注意：@TransactionalEventListener 的 phase 属性（AFTER_COMMIT 等）
```

### 审批/工作流模式
```
搜索：Activiti/Flowable/Camunda 相关类
或自研审批：审批节点、审批人、审批动作
构建：审批流程图
```

## Spring Boot 常见模式识别

### AOP 切面（隐含逻辑）
- `@Aspect` + `@Around/@Before/@After`
- 常用于：日志、权限、缓存、事务
- 分析时注意切点表达式匹配范围

### 拦截器
- `HandlerInterceptor` 实现类
- `Filter` 实现类
- 影响请求的前处理/后处理逻辑

### 定时任务
- `@Scheduled` 注解的方法
- 可能影响数据状态，需在业务分析中体现

### 缓存策略
- `@Cacheable`, `@CacheEvict`, `@CachePut`
- RedisTemplate 直接操作
- 注意缓存与数据库一致性

### 事务边界
- `@Transactional` 的 propagation、isolation、rollbackFor 属性
- 编程式事务：`TransactionTemplate`
- 事务嵌套和传播行为对业务的影响

## 代码搜索速查

### 快速定位入口
```
Glob: **/controller/**/*.java
Grep: @(Get|Post|Put|Delete|Patch)Mapping
```

### 查找业务校验
```
Grep: throw new.*Exception
Grep: Assert\.(notNull|isTrue|hasText)
Grep: Preconditions\.check
Grep: @Valid|@Validated
```

### 查找状态变更
```
Grep: \.setStatus\(|\.setState\(
Grep: Status\.|State\.
Grep: enum.*(Status|State)
```

### 查找外部调用
```
Grep: @FeignClient
Grep: restTemplate\.|webClient\.
Grep: @RabbitListener|@KafkaListener
Grep: applicationEventPublisher\.publish
```

### 查找数据操作
```
Grep: @Insert|@Update|@Delete|@Select
Grep: save\(|saveAll\(|delete\(|update\(
Grep: JpaRepository|BaseMapper|CrudRepository
```
