#!/usr/bin/env python3
"""
条目写入工具：添加新条目并更新倒排索引
用法：
  python3 add_entry.py --yaml-file /path/to/entry.yml
  python3 add_entry.py --stdin < entry.yml
  echo 'yaml content' | python3 add_entry.py --stdin
"""
import json
import argparse
import os
import sys
import re
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.json"
ENTRIES_DIR = BASE_DIR / "entries"

# 分类目录映射：根据标签自动归类
CATEGORY_KEYWORDS = {
    "spring": ["Spring", "SpringBoot", "SpringMVC", "SpringSecurity", "SpringCloud",
               "Bean", "依赖注入", "AOP", "循环依赖"],
    "mybatis": ["MyBatis", "Mapper", "XML映射"],
    "jvm": ["JVM", "GC", "OutOfMemoryError", "StackOverflowError", "ClassLoader",
            "内存泄漏", "类加载"],
    "concurrency": ["线程", "并发", "死锁", "线程池", "ConcurrentModificationException",
                     "synchronized", "Lock"],
    "database": ["MySQL", "PostgreSQL", "SQL", "索引", "慢查询", "连接池", "事务",
                  "DataAccessException", "SQLException"],
    "middleware": ["Redis", "Kafka", "RabbitMQ", "Elasticsearch", "Dubbo", "Nacos",
                   "Gateway", "Feign", "Sentinel"],
}


def detect_category(tags):
    """根据标签自动判断分类目录"""
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for tag in tags:
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in tag.lower() or tag.lower() in kw.lower():
                    scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def parse_yaml_simple(content):
    """简易 YAML 解析"""
    result = {}
    current_key = None
    current_value_lines = []
    in_multiline = False

    for line in content.split("\n"):
        stripped = line.rstrip()

        if in_multiline:
            if stripped and not stripped[0].isspace() and ":" in stripped and not stripped.startswith("#"):
                result[current_key] = "\n".join(current_value_lines)
                in_multiline = False
            else:
                current_value_lines.append(stripped)
                continue

        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped and not stripped.startswith(" "):
            idx = stripped.index(":")
            key = stripped[:idx].strip()
            val = stripped[idx + 1:].strip()

            if val == "|":
                current_key = key
                current_value_lines = []
                in_multiline = True
            elif val.startswith("[") and val.endswith("]"):
                items = val[1:-1].split(",")
                result[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            elif val.startswith('"') and val.endswith('"'):
                result[key] = val[1:-1]
            elif val.lower() == "true":
                result[key] = True
            elif val.lower() == "false":
                result[key] = False
            else:
                result[key] = val

    if in_multiline and current_key:
        result[current_key] = "\n".join(current_value_lines)

    return result


def load_index() -> dict:
    if not INDEX_FILE.exists():
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: dict):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def update_index(index, entry_id, tags):
    """将条目 ID 添加到每个标签的倒排列表中"""
    for tag in tags:
        if tag not in index:
            index[tag] = []
        if entry_id not in index[tag]:
            index[tag].append(entry_id)
    return index


def save_entry(entry):
    """将条目保存为 YAML 文件"""
    tags = entry.get("tags", [])
    category = detect_category(tags)
    category_dir = ENTRIES_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    entry_id = entry.get("id", "UNKNOWN")
    filename = entry_id.lower().replace(" ", "-") + ".yml"
    filepath = category_dir / filename

    # 手动生成 YAML（避免依赖 pyyaml）
    lines = []
    simple_fields = ["id", "title", "context", "root_cause", "solution",
                     "framework_version", "deprecated_reason", "created", "updated"]
    bool_fields = ["deprecated"]
    list_fields = ["tags"]
    multiline_fields = ["code_bad", "code_fix"]

    for field in ["id", "title"]:
        if field in entry:
            lines.append(f'{field}: "{entry[field]}"')

    if "tags" in entry:
        tag_str = ", ".join(f'"{t}"' for t in entry["tags"])
        lines.append(f"tags: [{tag_str}]")

    for field in ["context", "root_cause"]:
        if field in entry:
            lines.append(f'{field}: "{entry[field]}"')

    for field in multiline_fields:
        if field in entry and entry[field]:
            lines.append(f"{field}: |")
            for code_line in entry[field].split("\n"):
                lines.append(f"  {code_line}")

    if "solution" in entry:
        lines.append(f'{solution}: "{entry["solution"]}"' if "solution" != "solution" else f'solution: "{entry["solution"]}"')

    if "framework_version" in entry:
        lines.append(f'framework_version: "{entry["framework_version"]}"')

    lines.append(f'deprecated: {str(entry.get("deprecated", False)).lower()}')

    if entry.get("deprecated_reason"):
        lines.append(f'deprecated_reason: "{entry["deprecated_reason"]}"')
    else:
        lines.append('deprecated_reason: ""')

    today = date.today().isoformat()
    lines.append(f'created: "{entry.get("created", today)}"')
    lines.append(f'updated: "{entry.get("updated", today)}"')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Java Debug Memory 条目写入")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--yaml-file", help="YAML 条目文件路径")
    group.add_argument("--stdin", action="store_true", help="从 stdin 读取 YAML")
    args = parser.parse_args()

    if args.yaml_file:
        with open(args.yaml_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    entry = parse_yaml_simple(content)

    if "id" not in entry:
        print("错误：条目必须包含 id 字段", file=sys.stderr)
        sys.exit(1)
    if "tags" not in entry or not entry["tags"]:
        print("错误：条目必须包含至少一个标签", file=sys.stderr)
        sys.exit(1)

    # 保存条目文件
    filepath = save_entry(entry)

    # 更新倒排索引
    index = load_index()
    index = update_index(index, entry["id"], entry["tags"])
    save_index(index)

    print(f"条目已保存：{filepath}")
    print(f"标签已索引：{', '.join(entry['tags'])}")
    print(f"索引总标签数：{len(index)}")


if __name__ == "__main__":
    main()
