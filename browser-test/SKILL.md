---
name: browser-test
description: 浏览器自动化测试技能。读取 Markdown 格式的测试用例文档，通过 Sub-Agent 使用 Playwright 执行浏览器操作（点击、表单填写、页面导航），捕获截图和页面内容，验证预期结果（页面展示、接口响应），输出测试报告。触发条件：(1) 用户要求执行浏览器测试用例，(2) 用户说"跑一下测试"并提供测试用例文件路径，(3) 用户说"/browser-test"。不触发：纯接口测试（无浏览器操作）、编写测试用例文档（无执行需求）。
---

# 浏览器自动化测试技能

## 概述

通过 Markdown 测试用例文档驱动 Playwright 浏览器自动化，执行测试并生成报告。

## 工作流程

### 第一步：解析测试用例

读取用户指定的 Markdown 测试用例文件，解析出：
- **前置条件**：初始 URL、登录步骤等
- **操作步骤**：逐步的浏览器操作（点击、填写、导航等）
- **预期结果**：页面内容验证、URL 验证、接口响应验证

向用户展示解析后的测试概要，确认无误后继续。

### 第二步：环境检查

检查测试脚本运行环境：

```bash
# 检查虚拟环境是否存在
VENV_DIR="$HOME/.claude/skills/browser-test/scripts/.venv"
if [ ! -d "$VENV_DIR" ]; then
    cd $HOME/.claude/skills/browser-test/scripts
    uv venv .venv
    uv pip install playwright
    .venv/bin/playwright install chromium
fi
```

### 第三步：委派 Sub-Agent 执行

使用 Agent 工具创建 Sub-Agent，传入以下信息：

**Sub-Agent 的 prompt 模板：**

```
你是一个浏览器自动化测试执行器。你的任务是：

1. 根据以下测试用例生成 Playwright Python 脚本
2. 执行脚本并捕获结果
3. 比对预期结果，输出分析报告

## 环境信息
- Python 虚拟环境：$HOME/.claude/skills/browser-test/scripts/.venv
- 脚本存放目录：$HOME/.claude/skills/browser-test/scripts/tests/
- 截图存放目录：$HOME/.claude/skills/browser-test/scripts/screenshots/
- 使用有头模式（headless=False）运行浏览器

## 测试用例内容
{测试用例的完整 Markdown 内容}

## 执行要求

### 脚本生成规则
- 使用 playwright.sync_api
- 有头模式运行：browser = p.chromium.launch(headless=False)
- 每个关键步骤后截图，保存到 screenshots/ 目录
- 元素定位优先级：
  1. 如果提供了选择器（CSS/XPath），直接使用
  2. 如果提供了关键词，使用 page.get_by_text() 或 page.get_by_role() 定位
  3. 如果是自然语言描述，使用 page.get_by_label()、page.get_by_placeholder() 等语义定位
- 每个操作步骤之间使用 page.wait_for_load_state() 确保页面加载完成
- 脚本以场景名命名，相同场景复用同一脚本文件

### 结果捕获
- 页面截图（PNG 格式）
- 页面文本内容（page.content() 或特定元素的 inner_text()）
- 当前 URL
- 如果需要接口验证，使用 page.expect_response() 或 requests 库调用

### 结果比对
对每个预期结果项逐一比对，输出格式：

```
## 测试结果报告

### 测试用例：{用例名称}
执行时间：{时间}

| 序号 | 验证项 | 预期结果 | 实际结果 | 状态 |
|------|--------|----------|----------|------|
| 1 | 页面跳转 | /dashboard | /dashboard | ✅ 通过 |
| 2 | 页面文字 | "欢迎回来" | "欢迎回来" | ✅ 通过 |
| 3 | 接口响应 | username=admin | username=admin | ✅ 通过 |

### 截图记录
- 步骤1：[截图路径]
- 步骤2：[截图路径]

### 总结
通过：X/Y | 失败：Z/Y
```

如果页面内容无法通过文本比对确认，读取截图文件进行视觉分析。
```

### 第四步：展示测试报告

接收 Sub-Agent 返回的结果，向用户展示：
1. 测试结果汇总表
2. 失败项的详细分析
3. 关键步骤的截图路径（用户可以查看）

## 脚本管理

### 目录结构
```
scripts/
├── .venv/                  # Python 虚拟环境（uv 管理）
├── tests/                  # 测试脚本（按场景命名）
│   ├── login_test.py
│   ├── order_create_test.py
│   └── ...
└── screenshots/            # 测试截图
    ├── login_step1.png
    ├── login_step2.png
    └── ...
```

### 脚本复用
- 脚本以测试场景命名（如 `login_test.py`）
- 如果相同场景的脚本已存在且测试步骤未变化，直接复用
- 如果测试步骤有变化，更新脚本内容

## 注意事项

1. **安全性**：测试凭证不要硬编码在脚本中，通过测试用例文档传入
2. **等待策略**：使用 Playwright 内置的 auto-wait 机制，避免硬编码 sleep
3. **错误处理**：脚本执行失败时，捕获错误信息和最后一帧截图，返回给主 Agent 分析
4. **有头模式**：默认使用有头模式（headless=False），方便用户观察执行过程
5. **超时设置**：单个操作默认超时 30 秒，整个测试默认超时 5 分钟
