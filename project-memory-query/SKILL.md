---
name: project-memory-query
description: 查询和管理项目的业务逻辑记忆文档。支持按接口名、模块名、业务域查找文档，快速定位业务流程、数据模型、业务规则等特定章节。触发条件：(1) 用户询问某个接口的业务逻辑、流程、规则、数据模型；(2) 用户要求查看已分析的接口文档；(3) 用户询问"有哪些接口文档"或"项目里分析了哪些接口"；(4) 用户说"查看/列出记忆文档"。不触发：当用户要求分析新接口时（使用 java-business-logic-analyzer）。
---

# 项目记忆查询工具

快速查询和定位项目中已存储的业务逻辑分析文档。

## 核心功能

### 1. 列出所有记忆文档

查看项目中所有已分析的接口文档：

```bash
bash scripts/query-memory.sh list
```

### 2. 查看文档特定章节

使用脚本快速提取文档的特定章节，避免读取完整文件：

```bash
# 查看概述（接口路径、核心职责、代码位置）
bash scripts/query-memory.sh overview <文档名>

# 查看完整业务流程
bash scripts/query-memory.sh flow <文档名>

# 查看业务规则表格
bash scripts/query-memory.sh rules <文档名>

# 查看数据模型（输入输出参数）
bash scripts/query-memory.sh data <文档名>

# 查看输入参数定义
bash scripts/query-memory.sh input <文档名>

# 查看输出参数定义
bash scripts/query-memory.sh output <文档名>

# 查看外部依赖
bash scripts/query-memory.sh deps <文档名>

# 查看配置优先级
bash scripts/query-memory.sh config <文档名>

# 查看特殊场景处理
bash scripts/query-memory.sh special <文档名>

# 查看总结
bash scripts/query-memory.sh summary <文档名>
```

### 3. 按标签查找文档

根据不同维度快速定位相关文档：

```bash
# 按接口名查找
bash scripts/query-memory.sh by-interface <接口名>

# 按模块名查找
bash scripts/query-memory.sh by-module <模块名>

# 按API类型查找（如 cold-start, hot-start）
bash scripts/query-memory.sh by-api-type <类型>

# 按业务域查找（如 ad-config, game-config）
bash scripts/query-memory.sh by-domain <业务域>
```

### 4. 关键词搜索

在所有文档中搜索特定关键词：

```bash
bash scripts/query-memory.sh find <关键词>
```

## 使用 Grep 直接查询

所有记忆文档都使用标准化的标记结构，支持直接使用 Grep 进行高效查询。

### 标签体系

每个文档包含以下标记：

**文档级标签（位于文档顶部）：**
- `<!-- TAG:interface:<接口名> -->` - 接口标识
- `<!-- TAG:module:<模块名> -->` - 所属模块
- `<!-- TAG:api-type:<类型> -->` - 接口类型
- `<!-- TAG:business-domain:<业务域> -->` - 业务领域

**章节标记：**
- `<!-- SECTION:overview -->` - 概述
- `<!-- SECTION:business-flow -->` - 业务流程
- `<!-- SECTION:business-rules -->` - 业务规则
- `<!-- SECTION:data-model -->` - 数据模型
- `<!-- SECTION:config-priority -->` - 配置优先级
- `<!-- SECTION:dependencies -->` - 外部依赖
- `<!-- SECTION:security -->` - 安全机制
- `<!-- SECTION:exception-handling -->` - 异常处理
- `<!-- SECTION:special-scenarios -->` - 特殊场景
- `<!-- SECTION:summary -->` - 总结

**子章节标记：**
- `<!-- SUBSECTION:input-dto -->` - 输入参数
- `<!-- SUBSECTION:output-dto -->` - 输出参数
- `<!-- SUBSECTION:flow-controller -->` - Controller层流程
- `<!-- SUBSECTION:flow-service -->` - Service层流程

### Grep 查询示例

```bash
# 查找包含特定接口的文档
grep -l "TAG:interface:app-api-coldstart" .claude/memory/*.md

# 提取业务流程章节（读取后续50行）
grep -A 50 "SECTION:business-flow" .claude/memory/app-api-coldstart-analysis.md

# 只看 Service 层流程
grep -A 30 "SUBSECTION:flow-service" .claude/memory/app-api-coldstart-analysis.md

# 提取输入参数定义
grep -A 20 "SUBSECTION:input-dto" .claude/memory/*.md

# 查找冷启动相关接口
grep -l "TAG:api-type:cold-start" .claude/memory/*.md

# 在业务规则中搜索关键词
grep -A 15 "SECTION:business-rules" .claude/memory/*.md | grep "VA渠道"
```

## 工作流程

### 场景 1：用户询问某个接口的业务逻辑

当用户询问类似"coldStart 接口的业务流程是什么？"时：

1. **查找文档**：
   ```bash
   bash scripts/query-memory.sh by-interface app-api-coldstart
   ```

2. **如果找到文档**，提取相关章节：
   ```bash
   # 先看概述了解基本信息
   bash scripts/query-memory.sh overview <文档名>

   # 再看具体的业务流程
   bash scripts/query-memory.sh flow <文档名>
   ```

3. **将提取的内容呈现给用户**，用简洁的语言总结关键点

4. **如果未找到文档**，告知用户该接口尚未分析，建议使用 `java-business-logic-analyzer` skill 进行分析

### 场景 2：用户询问接口的输入输出参数

当用户询问"coldStart 接口的输入参数有哪些？"时：

1. **定位文档并提取输入参数章节**：
   ```bash
   bash scripts/query-memory.sh input app-api-coldstart-analysis.md
   ```

2. **将参数表格展示给用户**

### 场景 3：用户询问有哪些相关接口

当用户询问"有哪些冷启动相关的接口？"时：

1. **按业务域或API类型查找**：
   ```bash
   bash scripts/query-memory.sh by-api-type cold-start
   ```

2. **列出找到的文档列表**

### 场景 4：用户询问配置或特殊场景

当用户询问"coldStart 接口的配置优先级是怎样的？"或"有哪些特殊场景处理？"时：

```bash
# 查看配置优先级
bash scripts/query-memory.sh config <文档名>

# 查看特殊场景
bash scripts/query-memory.sh special <文档名>
```

## 记忆文档位置

所有记忆文档存储在项目的 `.claude/memory/` 目录中：

```
<项目根目录>/.claude/memory/
├── INDEX.md                          # 记忆索引和使用指南
├── app-api-coldstart-analysis.md     # coldStart 接口分析
└── ...                               # 其他接口分析文档
```

## 高效使用原则

1. **优先使用脚本或 Grep**：避免使用 Read 工具读取完整文档，通过标记直接定位需要的章节
2. **精确提取**：使用 Grep 的 `-A` 参数控制读取行数，只获取必要的内容
3. **组合查询**：当需要多个章节时，可以多次调用脚本分别提取
4. **缓存意识**：如果用户在同一对话中多次询问同一文档，可以适当缓存已提取的内容

## 与其他 Skill 的协作

- **java-business-logic-analyzer**：当用户要求分析新接口时，使用该 skill 进行分析并生成记忆文档
- **本 skill**：当用户询问已分析的接口时，使用本 skill 快速查询已有记忆

## 注意事项

1. **不要读取完整文档**：记忆文档可能很长，始终通过标记定位特定章节
2. **检查文档是否存在**：查询前先确认文档是否存在，如不存在则建议使用分析 skill
3. **简洁呈现**：提取内容后，用简洁的语言总结关键点，不要直接粘贴大段原始内容
4. **标签匹配**：使用标签查找时，注意标签格式要精确匹配（如 `app-api-coldstart` 而非 `coldStart`）

## 详细参考

完整的标签体系和使用示例，参见：[references/tag-system.md](references/tag-system.md)
