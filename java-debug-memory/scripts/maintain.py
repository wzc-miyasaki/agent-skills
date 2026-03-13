#!/usr/bin/env python3
"""
维护工具：过时标记、索引重建、统计
用法：
  python3 maintain.py deprecate --id "NPE-SPRING-001" --reason "Spring Boot 3.x 已修复"
  python3 maintain.py reindex
  python3 maintain.py stats
"""
import json
import argparse
import sys
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.json"
ENTRIES_DIR = BASE_DIR / "entries"


def parse_yaml_simple(path: Path) -> dict:
    """简易 YAML 解析"""
    result = {}
    current_key = None
    current_value_lines = []
    in_multiline = False

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
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


def load_all_entries():
    entries = []
    for yml_file in ENTRIES_DIR.rglob("*.yml"):
        try:
            entry = parse_yaml_simple(yml_file)
            entry["_file"] = str(yml_file)
            entries.append(entry)
        except Exception as e:
            print(f"警告：解析 {yml_file} 失败：{e}", file=sys.stderr)
    return entries


def cmd_reindex(_args):
    """重建倒排索引"""
    entries = load_all_entries()
    index = {}
    for entry in entries:
        entry_id = entry.get("id", "")
        tags = entry.get("tags", [])
        for tag in tags:
            if tag not in index:
                index[tag] = []
            if entry_id not in index[tag]:
                index[tag].append(entry_id)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"索引重建完成：{len(entries)} 个条目，{len(index)} 个标签")


def cmd_stats(_args):
    """输出统计信息"""
    entries = load_all_entries()
    if not entries:
        print("知识库为空，暂无条目。")
        return

    # 按分类统计
    category_count = Counter()
    tag_count = Counter()
    deprecated_count = 0

    for entry in entries:
        filepath = Path(entry.get("_file", ""))
        category = filepath.parent.name if filepath.parent != ENTRIES_DIR else "general"
        category_count[category] += 1

        for tag in entry.get("tags", []):
            tag_count[tag] += 1

        if entry.get("deprecated", False):
            deprecated_count += 1

    print(f"=== Java Debug Memory 统计 ===")
    print(f"总条目数：{len(entries)}")
    print(f"已过时条目：{deprecated_count}")
    print(f"有效条目：{len(entries) - deprecated_count}")
    print()

    print("按分类：")
    for cat, cnt in category_count.most_common():
        print(f"  {cat}: {cnt}")
    print()

    print(f"标签总数：{len(tag_count)}")
    print("Top 10 高频标签：")
    for tag, cnt in tag_count.most_common(10):
        print(f"  {tag}: {cnt}")


def cmd_deprecate(args):
    """标记条目为过时"""
    target_id = args.id
    reason = args.reason or ""

    for yml_file in ENTRIES_DIR.rglob("*.yml"):
        content = yml_file.read_text(encoding="utf-8")
        entry = parse_yaml_simple(yml_file)
        if entry.get("id") == target_id:
            # 替换 deprecated 字段
            import re
            content = re.sub(r'deprecated:\s*(true|false)', 'deprecated: true', content)
            content = re.sub(r'deprecated_reason:\s*".*?"', f'deprecated_reason: "{reason}"', content)
            yml_file.write_text(content, encoding="utf-8")
            print(f"已标记 {target_id} 为过时：{reason}")
            return

    print(f"未找到条目：{target_id}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Java Debug Memory 维护工具")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("reindex", help="重建倒排索引")
    sub.add_parser("stats", help="输出统计信息")

    dep = sub.add_parser("deprecate", help="标记条目为过时")
    dep.add_argument("--id", required=True, help="条目 ID")
    dep.add_argument("--reason", default="", help="过时原因")

    args = parser.parse_args()

    if args.command == "reindex":
        cmd_reindex(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "deprecate":
        cmd_deprecate(args)


if __name__ == "__main__":
    main()
