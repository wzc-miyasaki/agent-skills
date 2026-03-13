#!/usr/bin/env python3
"""
查询引擎：基于倒排索引的标签匹配 + 命中数排序
用法：
  python3 query.py --tags "NullPointerException,Spring,依赖注入" [--top 5] [--include-deprecated]
"""
import json
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.json"
ENTRIES_DIR = BASE_DIR / "entries"


def load_index():
    # type: () -> dict
    if not INDEX_FILE.exists():
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_entry(entry_id):
    # type: (str) -> Optional[dict]
    """通过遍历 entries 子目录查找条目文件"""
    for yml_file in ENTRIES_DIR.rglob("*.yml"):
        if yml_file.stem == entry_id.lower() or yml_file.stem == entry_id:
            try:
                import yaml
                with open(yml_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except ImportError:
                # fallback: 简单文本解析
                return _parse_yaml_simple(yml_file)
    return None


def _parse_yaml_simple(path: Path) -> dict:
    """简易 YAML 解析，不依赖 pyyaml"""
    result = {}
    current_key = None
    current_value_lines = []
    in_multiline = False

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")

            if in_multiline:
                if stripped and not stripped[0].isspace() and ":" in stripped:
                    result[current_key] = "\n".join(current_value_lines)
                    in_multiline = False
                else:
                    current_value_lines.append(stripped)
                    continue

            if ":" in stripped and not stripped.startswith(" ") and not stripped.startswith("#"):
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

        if in_multiline:
            result[current_key] = "\n".join(current_value_lines)

    return result


def query(tags, top_n=5, include_deprecated=False):
    index = load_index()

    # 收集候选条目及其命中的标签
    candidate_hits = {}  # dict[str, list[str]]
    for tag in tags:
        # 精确匹配
        matched_ids = index.get(tag, [])
        # 模糊匹配：标签包含查询词或查询词包含标签
        if not matched_ids:
            for idx_tag, ids in index.items():
                if tag in idx_tag or idx_tag in tag:
                    matched_ids.extend(ids)

        for entry_id in matched_ids:
            if entry_id not in candidate_hits:
                candidate_hits[entry_id] = []
            if tag not in candidate_hits[entry_id]:
                candidate_hits[entry_id].append(tag)

    # 按命中标签数降序排序
    sorted_candidates = sorted(candidate_hits.items(), key=lambda x: len(x[1]), reverse=True)

    results = []
    for entry_id, hit_tags in sorted_candidates[:top_n * 2]:  # 多取一些，过滤后截断
        entry = load_entry(entry_id)
        if entry is None:
            continue
        if not include_deprecated and entry.get("deprecated", False):
            continue
        entry["_hit_tags"] = hit_tags
        entry["_hit_count"] = len(hit_tags)
        results.append(entry)
        if len(results) >= top_n:
            break

    return results


def format_result(entry: dict) -> str:
    lines = []
    lines.append(f"### [{entry.get('id', '?')}] {entry.get('title', '?')}")
    lines.append(f"命中标签({entry.get('_hit_count', 0)})：{', '.join(entry.get('_hit_tags', []))}")
    lines.append(f"场景：{entry.get('context', '-')}")
    lines.append(f"根因：{entry.get('root_cause', '-')}")
    if entry.get("code_bad"):
        lines.append(f"问题代码：\n```java\n{entry['code_bad'].strip()}\n```")
    if entry.get("code_fix"):
        lines.append(f"修复代码：\n```java\n{entry['code_fix'].strip()}\n```")
    lines.append(f"解决思路：{entry.get('solution', '-')}")
    if entry.get("deprecated"):
        lines.append(f"⚠️ 已过时：{entry.get('deprecated_reason', '')}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Java Debug Memory 查询引擎")
    parser.add_argument("--tags", required=True, help="逗号分隔的标签列表")
    parser.add_argument("--top", type=int, default=5, help="返回前 N 条结果")
    parser.add_argument("--include-deprecated", action="store_true", help="包含已过时条目")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    args = parser.parse_args()

    tag_list = [t.strip() for t in args.tags.split(",") if t.strip()]
    results = query(tag_list, args.top, args.include_deprecated)

    if not results:
        print("未找到匹配的历史排查记录。")
        sys.exit(0)

    if args.json:
        # 移除内部字段
        for r in results:
            r.pop("_hit_tags", None)
            r.pop("_hit_count", None)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"找到 {len(results)} 条匹配记录（按标签命中数排序）：\n")
        for entry in results:
            print(format_result(entry))


if __name__ == "__main__":
    main()
