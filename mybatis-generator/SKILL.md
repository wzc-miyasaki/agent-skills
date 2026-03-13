---
name: mybatis-generator
description: 根据 MySQL 表结构生成 MyBatis 代码（POJO 类、Mapper 接口、Mapper XML）。支持驼峰命名转换、Lombok Getter/Setter、自增主键。使用场景：用户提供表名和表结构后，生成对应的 Java POJO 类、Mapper 接口定义和 Mapper XML 文件。执行前需通过交互确认：(1) 日期时间类型映射规则（LocalDateTime 或 Instant）、(2) POJO/Mapper/XML 文件路径、(3) 需要生成的 CRUD 方法。
---

# MyBatis 代码生成技能

## 工作流程

### 第一步：获取表结构信息

用户提供表名后，询问表结构详情（字段名、类型、注释）。如果用户已提供表结构，直接使用。

表结构格式示例：
```
表名：user_info
字段：
- id: BIGINT, 主键自增
- user_name: VARCHAR(50), 用户名
- create_time: DATETIME, 创建时间
```

---

### 第二步：配置确认（强制交互式问答）

**⚠️ 重要指令：在未获得必要配置之前，不要生成任何代码/分析。**

**必须以下列问答形式逐一询问用户，每次只问一个问题，等待用户回答后再问下一个：**

#### 问题 1：日期时间类型映射

```
【配置 1/3】日期时间类型映射

表中的 DATETIME/TIMESTAMP 类型字段将映射为：
  [1] LocalDateTime（默认）
  [2] Instant

请选择（输入编号或直接回车使用默认）：
```

#### 问题 2：文件存放位置

```
【配置 2/3】文件存放位置

请提供以下路径（可一次回答全部，或逐项提供）：
  [1] POJO 类包路径（如：com.example.entity）
  [2] Mapper 接口包路径（如：com.example.mapper）
  [3] Mapper XML 文件路径（如：src/main/resources/mapper 或具体目录）

如使用默认路径（当前目录），可直接回车跳过。
```

#### 问题 3：生成方法选择

```
【配置 3/3】生成方法选择

请选择需要生成的 CRUD 方法（可多选，输入编号用逗号分隔）：
  [1] insert（插入全部字段）
  [2] insertSelective（插入非空字段）
  [3] selectByPrimaryKey（根据主键查询）
  [4] updateByPrimaryKey（更新全部字段）
  [5] updateByPrimaryKeySelective（更新非空字段）
  [6] deleteByPrimaryKey（根据主键删除）
  [7] 自定义查询方法

  [回车] 仅生成 BaseResultMap 和 Base_Column_List（不生成具体方法）

请选择：
```

---

### 第三步：确认汇总

**在获得全部 3 项配置后，向用户展示配置汇总并请求最终确认：**

```
=== 生成配置确认 ===
表名：user_info
→ 类名：userInfo
→ Mapper：UserInfoMapper

【类型映射】
  DATETIME/TIMESTAMP → Instant

【文件路径】
  POJO: com.example.entity
  Mapper: com.example.mapper
  XML: src/main/resources/mapper

【生成方法】
  - insert
  - selectByPrimaryKey
  - deleteByPrimaryKey

────────────────────────────────
⚠️ 请确认以上配置是否正确？（回复"确认"开始生成，或指出需要修改的地方）
```

**⚠️ 必须等待用户明确回复"确认"后，才能进入第四步生成代码。**

---

### 第四步：生成代码

按照用户确认的配置生成代码。

## 命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| 表→类 | `user_info` → `userInfo` (小驼峰) | `user_info_log` → `userInfoLog` |
| 表→接口 | `user_info` → `UserInfoMapper` | `user_info_log` → `UserInfoLogMapper` |
| 字段→属性 | `user_id` → `userId` (小驼峰) | `create_time` → `createTime` |
| XML 命名 | 与接口方法一致 | `BaseResultMap`, `Base_Column_List` |

## 代码规范

### POJO 类

```java
package ${pojoPackage};

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class ${ClassName} {
    /**
     * 主键 (自增)
     */
    private Long id;

    /**
     * 其他字段
     */
    private String fieldName;
}
```

### Mapper 接口

```java
package ${mapperPackage};

import ${pojoPackage}.${ClassName};

public interface ${ClassName}Mapper {
    // 默认包含基础 CRUD 方法，具体生成哪些询问用户
}
```

### Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="${mapperPackage}.${ClassName}Mapper">

    <resultMap id="BaseResultMap" type="${pojoPackage}.${ClassName}">
        <id column="id" jdbcType="BIGINT" property="id" />
        <!-- 其他字段 -->
    </resultMap>

    <sql id="Base_Column_List">
        id, field_name, ...
    </sql>

    <!-- 其他方法：根据用户需求生成 -->
</mapper>
```

## 数据类型映射

### 基础类型映射

| MySQL 类型 | Java 类型 | JdbcType |
|------------|-----------|----------|
| BIGINT | Long | BIGINT |
| INT | Integer | INTEGER |
| VARCHAR | String | VARCHAR |
| DECIMAL/NUMERIC | BigDecimal | DECIMAL |
| TINYINT(1) | Boolean | BOOLEAN |
| TEXT/LONGTEXT | String | LONGVARCHAR |

### 日期时间类型映射（可配置）

| MySQL 类型 | 选项 1 | 选项 2 |
|------------|--------|--------|
| DATETIME | LocalDateTime | Instant |
| TIMESTAMP | LocalDateTime | Instant |
| DATE | LocalDate | - |
| TIME | LocalTime | - |

## 公共 SQL 片段

对于共享的查询条件（如公共 WHERE 语句），在 XML 中使用 `<sql>` 片段定义：

```xml
<sql id="Where_Condition">
    <where>
        <if test="id != null">AND id = #{id}</if>
        <if test="name != null">AND name = #{name}</if>
    </where>
</sql>
```

## 注意事项

1. **必须使用自增主键**：主键字段命名为 `id`，类型为 `Long`
2. **Lombok 简化**：只使用 `@Getter` 和 `@Setter`，不使用其他 Lombok 注解
3. **不使用 MyBatis-Plus**：纯 MyBatis 实现
4. **XML 必须包含**：`BaseResultMap` 和 `Base_Column_List`（默认生成）
5. **强制交互式确认**：
   - ⚠️ 必须按顺序逐一询问 3 项配置（类型映射 → 文件路径 → 生成方法）
   - ⚠️ 每次只问一个问题，等待用户回答后再问下一个
   - ⚠️ 必须展示配置汇总并获得用户明确"确认"后才能生成代码
   - ⚠️ 在未获得必要配置之前，不要生成任何代码/分析
