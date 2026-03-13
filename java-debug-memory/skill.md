# Java Debug Memory - Debug 知识库技能

## 技能概述

持续积累 Java 排查经验的知识库。每次解决问题后自动总结、打标签、写入条目，下次遇到相似问题时通过标签匹配快速检索历史方案。

## 触发条件

### 自动检索（排查阶段）
当用户描述一个 Java 代码问题、异常、报错时：
1. 从用户描述中提取关键特征标签（异常类名、框架、场景关键词）
2. 调用 `scripts/query.py` 查询匹配条目
3. 如有匹配结果，将 Top 3 条目作为参考上下文辅助排查
4. 如无匹配，正常排查

### 自动记录（解决阶段）
当用户明确表示当前方案可以解决问题时（如 "可以了"、"问题解决了"、"这个方案OK"）：
1. 自动总结本次排查经验
2. AI 生成精炼标签（最简短描述问题特征）
3. 调用 `scripts/add_entry.py` 写入条目并更新索引
4. 提醒用户记录完成

## 标签管理原则

标签由 AI 维护和扩展，遵循以下原则：
- **最简短**：用最少的词描述问题特征，如 "Bean注入null"、"循环依赖"、"索引失效"
- **多维度**：每个条目至少包含：异常类型标签 + 框架/组件标签 + 场景标签
- **可复用**：优先复用 `tags.yml` 中已有标签，必要时扩展新标签
- **去重**：避免语义重复的标签（如 "NPE" 和 "NullPointerException" 只保留一个）

## 条目格式

每个条目为一个 YAML 文件，存放在 `entries/<分类>/` 下：

```yaml
id: "分类前缀-编号"          # 如 NPE-SPRING-001
title: "一句话描述问题"       # 简明扼要
tags: ["标签1", "标签2"]     # AI 生成的特征标签
context: "触发场景描述"       # 什么情况下会出现
root_cause: "根本原因"        # 为什么出现
code_bad: |                   # 问题代码片段
  // ...
code_fix: |                   # 修复代码片段
  // ...
solution: "解决思路概述"      # 简要思路
framework_version: ""         # 适用版本范围
deprecated: false             # 是否过时
deprecated_reason: ""         # 过时原因
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
```

## 工作流

```
用户描述问题
    ↓
AI 提取标签 → 调用 query.py
    ↓
├─ 有匹配 → 展示 Top3 参考方案，辅助排查
└─ 无匹配 → 正常排查
    ↓
排查过程（正常对话）
    ↓
用户确认解决
    ↓
AI 总结 → 生成标签 → 调用 add_entry.py
    ↓
提醒："已记录排查经验 [条目ID]，标签：[tags]"
```

## 脚本使用

### 查询
```bash
python3 ~/.claude/skills/java-debug-memory/scripts/query.py --tags "NullPointerException,Spring,依赖注入" --top 5
```

### 写入
```bash
python3 ~/.claude/skills/java-debug-memory/scripts/add_entry.py --yaml-file /path/to/entry.yml
```
或通过 stdin 传入 YAML 内容：
```bash
python3 ~/.claude/skills/java-debug-memory/scripts/add_entry.py --stdin <<'EOF'
id: "NPE-SPRING-001"
...
EOF
```

### 维护
```bash
# 标记过时条目
python3 ~/.claude/skills/java-debug-memory/scripts/maintain.py deprecate --id "NPE-SPRING-001" --reason "Spring Boot 3.x 已修复"

# 重建索引
python3 ~/.claude/skills/java-debug-memory/scripts/maintain.py reindex

# 统计信息
python3 ~/.claude/skills/java-debug-memory/scripts/maintain.py stats
```
