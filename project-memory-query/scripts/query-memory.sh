#!/bin/bash
# Game SDK 记忆查询脚本
# 用法：./query-memory.sh <查询类型> [关键词]

MEMORY_DIR=".claude/memory"

show_help() {
    cat << EOF
Game SDK 记忆查询工具

用法: $0 <命令> [参数]

命令列表:
  list              列出所有记忆文档
  find <关键词>      查找包含关键词的文档

  overview <文档>   查看文档概述
  flow <文档>       查看业务流程
  rules <文档>      查看业务规则
  data <文档>       查看数据模型
  deps <文档>       查看外部依赖
  config <文档>     查看配置优先级
  special <文档>    查看特殊场景
  summary <文档>    查看总结

  by-interface <接口名>     按接口名查找
  by-module <模块名>        按模块名查找
  by-api-type <类型>        按API类型查找
  by-domain <业务域>        按业务域查找

  input <文档>      查看输入参数定义
  output <文档>     查看输出参数定义

示例:
  $0 list
  $0 find coldStart
  $0 overview app-api-coldstart-analysis.md
  $0 flow app-api-coldstart-analysis.md
  $0 by-interface app-api-coldstart
  $0 input app-api-coldstart-analysis.md

EOF
}

# 列出所有文档
list_docs() {
    echo "📋 可用的记忆文档:"
    echo ""
    find "$MEMORY_DIR" -name "*.md" ! -name "INDEX.md" -exec basename {} \; | sort
}

# 查找包含关键词的文档
find_docs() {
    local keyword="$1"
    echo "🔍 搜索包含 '$keyword' 的文档:"
    echo ""
    grep -l -r "$keyword" "$MEMORY_DIR"/*.md 2>/dev/null | while read file; do
        echo "  📄 $(basename $file)"
        grep -n "$keyword" "$file" | head -3 | sed 's/^/     /'
        echo ""
    done
}

# 查看概述
show_overview() {
    local doc="$1"
    echo "📖 概述 - $doc"
    echo ""
    grep -A 20 "<!-- SECTION:overview -->" "$MEMORY_DIR/$doc" | grep -B 20 "<!-- /SECTION:overview -->"
}

# 查看业务流程
show_flow() {
    local doc="$1"
    echo "🔄 业务流程 - $doc"
    echo ""
    grep -A 100 "<!-- SECTION:business-flow -->" "$MEMORY_DIR/$doc" | grep -B 100 "<!-- /SECTION:business-flow -->"
}

# 查看业务规则
show_rules() {
    local doc="$1"
    echo "📏 业务规则 - $doc"
    echo ""
    grep -A 30 "<!-- SECTION:business-rules -->" "$MEMORY_DIR/$doc" | grep -B 30 "<!-- /SECTION:business-rules -->"
}

# 查看数据模型
show_data() {
    local doc="$1"
    echo "📊 数据模型 - $doc"
    echo ""
    grep -A 80 "<!-- SECTION:data-model -->" "$MEMORY_DIR/$doc" | grep -B 80 "<!-- /SECTION:data-model -->"
}

# 查看外部依赖
show_deps() {
    local doc="$1"
    echo "🔗 外部依赖 - $doc"
    echo ""
    grep -A 25 "<!-- SECTION:dependencies -->" "$MEMORY_DIR/$doc" | grep -B 25 "<!-- /SECTION:dependencies -->"
}

# 查看配置优先级
show_config() {
    local doc="$1"
    echo "⚙️  配置优先级 - $doc"
    echo ""
    grep -A 40 "<!-- SECTION:config-priority -->" "$MEMORY_DIR/$doc" | grep -B 40 "<!-- /SECTION:config-priority -->"
}

# 查看特殊场景
show_special() {
    local doc="$1"
    echo "⚠️  特殊场景 - $doc"
    echo ""
    grep -A 60 "<!-- SECTION:special-scenarios -->" "$MEMORY_DIR/$doc" | grep -B 60 "<!-- /SECTION:special-scenarios -->"
}

# 查看总结
show_summary() {
    local doc="$1"
    echo "📝 总结 - $doc"
    echo ""
    grep -A 40 "<!-- SECTION:summary -->" "$MEMORY_DIR/$doc" | grep -B 40 "<!-- /SECTION:summary -->"
}

# 按接口名查找
by_interface() {
    local interface="$1"
    echo "🔍 查找接口: $interface"
    echo ""
    grep -l "TAG:interface:$interface" "$MEMORY_DIR"/*.md 2>/dev/null
}

# 按模块名查找
by_module() {
    local module="$1"
    echo "🔍 查找模块: $module"
    echo ""
    grep -l "TAG:module:$module" "$MEMORY_DIR"/*.md 2>/dev/null
}

# 按API类型查找
by_api_type() {
    local type="$1"
    echo "🔍 查找API类型: $type"
    echo ""
    grep -l "TAG:api-type:$type" "$MEMORY_DIR"/*.md 2>/dev/null
}

# 按业务域查找
by_domain() {
    local domain="$1"
    echo "🔍 查找业务域: $domain"
    echo ""
    grep -l "TAG:business-domain:.*$domain" "$MEMORY_DIR"/*.md 2>/dev/null
}

# 查看输入参数
show_input() {
    local doc="$1"
    echo "📥 输入参数 - $doc"
    echo ""
    grep -A 25 "<!-- SUBSECTION:input-dto -->" "$MEMORY_DIR/$doc" | grep -B 25 "<!-- /SUBSECTION:input-dto -->"
}

# 查看输出参数
show_output() {
    local doc="$1"
    echo "📤 输出参数 - $doc"
    echo ""
    grep -A 30 "<!-- SUBSECTION:output-dto -->" "$MEMORY_DIR/$doc" | grep -B 30 "<!-- /SUBSECTION:output-dto -->"
}

# 主逻辑
case "$1" in
    list)
        list_docs
        ;;
    find)
        find_docs "$2"
        ;;
    overview)
        show_overview "$2"
        ;;
    flow)
        show_flow "$2"
        ;;
    rules)
        show_rules "$2"
        ;;
    data)
        show_data "$2"
        ;;
    deps)
        show_deps "$2"
        ;;
    config)
        show_config "$2"
        ;;
    special)
        show_special "$2"
        ;;
    summary)
        show_summary "$2"
        ;;
    by-interface)
        by_interface "$2"
        ;;
    by-module)
        by_module "$2"
        ;;
    by-api-type)
        by_api_type "$2"
        ;;
    by-domain)
        by_domain "$2"
        ;;
    input)
        show_input "$2"
        ;;
    output)
        show_output "$2"
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
