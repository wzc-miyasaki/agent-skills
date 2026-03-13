# 记忆文档标签体系参考

## 标签分类

### 1. 文档级标签（TAG）

位于文档顶部，用于文档分类和快速查找。

| 标签格式 | 说明 | 示例 |
|---------|------|------|
| `<!-- TAG:interface:<接口名> -->` | 接口标识，使用模块-类名-方法名格式 | `TAG:interface:app-api-coldstart` |
| `<!-- TAG:module:<模块名> -->` | 所属模块 | `TAG:module:game-sdk` |
| `<!-- TAG:api-type:<类型> -->` | 接口类型 | `TAG:api-type:cold-start` |
| `<!-- TAG:analysis-date:<日期> -->` | 分析日期 | `TAG:analysis-date:2026-03-06` |
| `<!-- TAG:related-interfaces:<接口列表> -->` | 相关接口（逗号分隔） | `TAG:related-interfaces:app-api-hotstart` |
| `<!-- TAG:related-services:<服务列表> -->` | 相关服务（逗号分隔） | `TAG:related-services:game-service,ad-source-service` |
| `<!-- TAG:business-domain:<业务域列表> -->` | 业务领域（逗号分隔） | `TAG:business-domain:cold-start,ad-config,game-config` |

### 2. 章节标记（SECTION）

标记文档的主要章节，格式：`<!-- SECTION:章节名 -->` ... `<!-- /SECTION:章节名 -->`

| 章节名 | 说明 | 典型内容 |
|--------|------|---------|
| `overview` | 概述 | 接口路径、核心职责、代码位置、服务实现 |
| `business-flow` | 业务流程 | Controller层流程、Service层流程、完整调用链 |
| `business-rules` | 业务规则 | 业务规则表格（规则描述、触发条件、处理方式、代码位置） |
| `data-model` | 数据模型 | 输入参数、输出参数的完整定义 |
| `config-priority` | 配置优先级 | 各种配置项的优先级说明 |
| `dependencies` | 外部依赖 | 依赖的服务、方法、用途 |
| `security` | 安全机制 | 加密、校验、权限控制等 |
| `offline-config` | 离线配置 | 离线配置逻辑和配置项 |
| `code-references` | 代码引用 | 关键代码位置的索引 |
| `exception-handling` | 异常处理 | 异常类型、触发条件、处理方式 |
| `special-scenarios` | 特殊场景 | 特殊场景的触发条件和处理逻辑 |
| `flow-diagram` | 流程图 | 文字描述的流程图 |
| `summary` | 总结 | 接口的总体说明和关键特性 |

### 3. 子章节标记（SUBSECTION）

标记次级章节，格式：`<!-- SUBSECTION:子章节名 -->` ... `<!-- /SUBSECTION:子章节名 -->`

| 子章节名 | 父章节 | 说明 |
|---------|--------|------|
| `flow-controller` | business-flow | Controller层的处理流程 |
| `flow-service` | business-flow | Service层的业务逻辑 |
| `input-dto` | data-model | 输入参数（DTO）定义 |
| `output-dto` | data-model | 输出参数（DTO）定义 |
| `priority-source-type` | config-priority | 广告源类型配置优先级 |
| `priority-privacy-switch` | config-priority | 隐私开关配置优先级 |
| `offline-version-compare` | offline-config | 离线配置版本比较逻辑 |
| `offline-config-items` | offline-config | 离线配置项列表 |
| `scenario-va-channel` | special-scenarios | VA渠道特殊处理 |
| `scenario-pre-env` | special-scenarios | 预发环境特殊处理 |
| `scenario-channel-replace` | special-scenarios | 广告源渠道替换 |
| `scenario-config-fallback` | special-scenarios | 配置缺失降级 |

## Grep 查询模式

### 基础查询

```bash
# 查找包含特定标签的文档
grep -l "TAG:interface:<接口名>" .claude/memory/*.md

# 提取特定章节（-A 指定读取后续行数）
grep -A <行数> "SECTION:<章节名>" .claude/memory/<文档名>.md

# 提取子章节
grep -A <行数> "SUBSECTION:<子章节名>" .claude/memory/<文档名>.md
```

### 精确提取章节内容

使用两次 grep 精确提取章节内容（从开始标记到结束标记）：

```bash
# 提取完整章节
grep -A 100 "<!-- SECTION:overview -->" file.md | grep -B 100 "<!-- /SECTION:overview -->"

# 提取完整子章节
grep -A 50 "<!-- SUBSECTION:input-dto -->" file.md | grep -B 50 "<!-- /SUBSECTION:input-dto -->"
```

### 组合查询

```bash
# 查找特定业务域的所有文档
grep -l "TAG:business-domain:.*cold-start" .claude/memory/*.md

# 在特定章节中搜索关键词
grep -A 30 "SECTION:business-rules" .claude/memory/*.md | grep "<关键词>"

# 查找某服务相关的所有接口
grep -l "TAG:related-services:.*game-service" .claude/memory/*.md
```

## 常用查询场景

### 场景 1：查找接口文档

```bash
# 方法1：按接口名精确查找
grep -l "TAG:interface:app-api-coldstart" .claude/memory/*.md

# 方法2：按关键词模糊查找
grep -l "coldstart" .claude/memory/*.md
```

### 场景 2：查看接口基本信息

```bash
# 提取概述章节
grep -A 10 "SECTION:overview" .claude/memory/app-api-coldstart-analysis.md | grep -B 10 "/SECTION:overview"
```

### 场景 3：查看业务流程

```bash
# 完整业务流程
grep -A 80 "SECTION:business-flow" .claude/memory/app-api-coldstart-analysis.md

# 只看 Controller 层
grep -A 25 "SUBSECTION:flow-controller" .claude/memory/app-api-coldstart-analysis.md

# 只看 Service 层
grep -A 40 "SUBSECTION:flow-service" .claude/memory/app-api-coldstart-analysis.md
```

### 场景 4：查看数据模型

```bash
# 输入参数
grep -A 20 "SUBSECTION:input-dto" .claude/memory/app-api-coldstart-analysis.md

# 输出参数
grep -A 30 "SUBSECTION:output-dto" .claude/memory/app-api-coldstart-analysis.md
```

### 场景 5：查看业务规则

```bash
# 提取业务规则表格
grep -A 15 "SECTION:business-rules" .claude/memory/app-api-coldstart-analysis.md

# 在规则中搜索关键词
grep -A 15 "SECTION:business-rules" .claude/memory/*.md | grep "VA渠道"
```

### 场景 6：查看配置和特殊场景

```bash
# 配置优先级
grep -A 40 "SECTION:config-priority" .claude/memory/app-api-coldstart-analysis.md

# 特殊场景处理
grep -A 60 "SECTION:special-scenarios" .claude/memory/app-api-coldstart-analysis.md

# 特定特殊场景
grep -A 8 "SUBSECTION:scenario-va-channel" .claude/memory/app-api-coldstart-analysis.md
```

### 场景 7：查看外部依赖

```bash
grep -A 25 "SECTION:dependencies" .claude/memory/app-api-coldstart-analysis.md
```

### 场景 8：按业务域查找相关接口

```bash
# 查找冷启动相关接口
grep -l "TAG:api-type:cold-start" .claude/memory/*.md

# 查找广告配置相关接口
grep -l "TAG:business-domain:.*ad-config" .claude/memory/*.md
```

## 编写新记忆文档时的标签使用规范

### 必需标签

每个文档必须包含：
- `TAG:interface` - 接口标识
- `TAG:module` - 所属模块
- `TAG:analysis-date` - 分析日期

### 推荐标签

根据实际情况添加：
- `TAG:api-type` - 接口类型（如 cold-start, hot-start, payment）
- `TAG:business-domain` - 业务领域（可多个，逗号分隔）
- `TAG:related-services` - 相关服务（便于追踪依赖关系）

### 必需章节

每个文档应包含：
- `SECTION:overview` - 概述
- `SECTION:business-flow` - 业务流程
- `SECTION:data-model` - 数据模型（包含 input-dto 和 output-dto 子章节）
- `SECTION:summary` - 总结

### 可选章节

根据接口特点添加：
- `SECTION:business-rules` - 有明确业务规则时添加
- `SECTION:config-priority` - 有多级配置时添加
- `SECTION:special-scenarios` - 有特殊场景处理时添加
- `SECTION:dependencies` - 有外部依赖时添加
- `SECTION:exception-handling` - 有复杂异常处理时添加

## 标签命名约定

### 接口标识（interface）
- 格式：`<模块>-<类名>-<方法名>`
- 全小写，单词用短横线连接
- 示例：`app-api-coldstart`、`user-service-login`

### 模块名（module）
- 使用项目的实际模块名
- 全小写，单词用短横线连接
- 示例：`game-sdk`、`payment-service`

### API类型（api-type）
- 描述接口的功能类型
- 全小写，单词用短横线连接
- 示例：`cold-start`、`hot-start`、`payment`、`user-auth`

### 业务域（business-domain）
- 描述接口所属的业务领域
- 可以有多个，用逗号分隔
- 全小写，单词用短横线连接
- 示例：`cold-start`、`ad-config`、`game-config`、`user-management`

## 实用技巧

1. **使用 `-l` 参数快速定位**：只返回包含匹配的文件名，不显示内容
2. **使用 `-A` 参数控制读取行数**：根据章节大小调整行数，避免读取过多
3. **两次 grep 精确提取**：先用 `-A` 读取大范围，再用 `-B` 截取到结束标记
4. **管道组合查询**：使用 `|` 连接多个 grep 进行多条件过滤
5. **使用 `head`/`tail` 限制输出**：避免终端输出过多内容
