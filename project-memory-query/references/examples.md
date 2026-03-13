# 使用示例

## 示例 1：查看所有已分析的接口

**用户问**："项目里分析了哪些接口？"

**处理步骤**：
```bash
bash scripts/query-memory.sh list
```

**输出示例**：
```
📋 可用的记忆文档:

app-api-coldstart-analysis.md
app-api-hotstart-analysis.md
user-api-login-analysis.md
```

## 示例 2：查看接口的业务流程

**用户问**："coldStart 接口的业务流程是什么？"

**处理步骤**：
1. 定位文档：
```bash
bash scripts/query-memory.sh by-interface app-api-coldstart
```

2. 提取业务流程：
```bash
bash scripts/query-memory.sh flow app-api-coldstart-analysis.md
```

**输出示例**：
```
🔄 业务流程 - app-api-coldstart-analysis.md

## 业务流程

### 主流程

1. **接收加密请求参数**（AppApi.java:57-60）
   - 接收 EncodeReqDTO 类型的加密请求体
   - 从请求头获取 SDK 版本号 x-adver
...
```

## 示例 3：查看接口的输入参数

**用户问**："coldStart 接口需要哪些输入参数？"

**处理步骤**：
```bash
bash scripts/query-memory.sh input app-api-coldstart-analysis.md
```

**输出示例**：
```
📥 输入参数 - app-api-coldstart-analysis.md

### 输入参数（ColdStartReqDTO）

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| gaid | String | 广告ID | - |
| app_key | String | 游戏应用标识（必填） | "game_12345" |
...
```

## 示例 4：查看业务规则

**用户问**："coldStart 接口有哪些业务规则？"

**处理步骤**：
```bash
bash scripts/query-memory.sh rules app-api-coldstart-analysis.md
```

## 示例 5：查找特定业务域的接口

**用户问**："有哪些冷启动相关的接口？"

**处理步骤**：
```bash
bash scripts/query-memory.sh by-api-type cold-start
```

**输出示例**：
```
🔍 查找API类型: cold-start

.claude/memory/app-api-coldstart-analysis.md
.claude/memory/game-api-coldstart-analysis.md
```

## 示例 6：查看配置优先级

**用户问**："coldStart 接口的广告源配置优先级是怎样的？"

**处理步骤**：
```bash
bash scripts/query-memory.sh config app-api-coldstart-analysis.md
```

## 示例 7：查看特殊场景处理

**用户问**："coldStart 接口有哪些特殊场景处理？"

**处理步骤**：
```bash
bash scripts/query-memory.sh special app-api-coldstart-analysis.md
```

## 示例 8：使用 Grep 直接查询

**用户问**："在所有接口中搜索 VA 渠道相关的业务规则"

**处理步骤**：
```bash
cd /path/to/project
grep -A 15 "SECTION:business-rules" .claude/memory/*.md | grep "VA渠道"
```

## 示例 9：查看外部依赖

**用户问**："coldStart 接口依赖哪些服务？"

**处理步骤**：
```bash
bash scripts/query-memory.sh deps app-api-coldstart-analysis.md
```

## 示例 10：按模块查找接口

**用户问**："game-sdk 模块有哪些接口文档？"

**处理步骤**：
```bash
bash scripts/query-memory.sh by-module game-sdk
```
