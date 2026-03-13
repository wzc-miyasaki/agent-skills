#!/usr/bin/env python3
"""
MyBatis 代码生成配置交互脚本
在执行前通过交互方式收集用户配置
"""

import sys
import json


def prompt_datetime_mapping() -> bool:
    """询问日期时间类型映射规则

    Returns:
        True 表示使用 Instant, False 表示使用 LocalDateTime
    """
    print("\n=== 日期时间类型映射 ===")
    print("请选择日期时间类型 (DATETIME/TIMESTAMP) 的 Java 映射:")
    print("  [1] LocalDateTime (默认)")
    print("  [2] Instant")

    while True:
        choice = input("\n请选择 (1/2, 默认 1): ").strip()
        if choice in ('', '1'):
            return False
        elif choice == '2':
            return True
        else:
            print("无效选择，请输入 1 或 2")


def prompt_file_paths() -> dict:
    """询问文件存放位置

    Returns:
        包含 pojo_package, mapper_package, xml_path 的字典
    """
    print("\n=== 文件存放位置 ===")

    pojo_package = input("POJO 类包路径 (如 com.example.entity): ").strip()
    if not pojo_package:
        pojo_package = "com.example.entity"
        print(f"  使用默认值：{pojo_package}")

    mapper_package = input("Mapper 接口包路径 (如 com.example.mapper): ").strip()
    if not mapper_package:
        mapper_package = "com.example.mapper"
        print(f"  使用默认值：{mapper_package}")

    xml_path = input("Mapper XML 文件路径 (如 src/main/resources/mapper): ").strip()
    if not xml_path:
        xml_path = "src/main/resources/mapper"
        print(f"  使用默认值：{xml_path}")

    return {
        'pojo_package': pojo_package,
        'mapper_package': mapper_package,
        'xml_path': xml_path
    }


def prompt_methods() -> list:
    """询问需要生成的方法

    Returns:
        方法名称列表
    """
    print("\n=== 生成方法选择 ===")
    print("请选择需要生成的方法（可多选，输入编号用逗号分隔）:")
    print("  [1] insert (插入全部字段)")
    print("  [2] insertSelective (插入非空字段)")
    print("  [3] selectByPrimaryKey (根据主键查询)")
    print("  [4] updateByPrimaryKey (更新全部字段)")
    print("  [5] updateByPrimaryKeySelective (更新非空字段)")
    print("  [6] deleteByPrimaryKey (根据主键删除)")
    print("\n  直接回车表示仅生成 BaseResultMap 和 Base_Column_List")

    method_map = {
        '1': 'insert',
        '2': 'insertSelective',
        '3': 'selectByPrimaryKey',
        '4': 'updateByPrimaryKey',
        '5': 'updateByPrimaryKeySelective',
        '6': 'deleteByPrimaryKey'
    }

    choice = input("\n请选择：").strip()

    if not choice:
        return []

    methods = []
    for c in choice.split(','):
        c = c.strip()
        if c in method_map:
            methods.append(method_map[c])

    return methods


def print_config_summary(table_name: str, columns: list, config: dict) -> None:
    """打印配置汇总"""
    # 简单转换类名
    def to_camel_case(name: str, upper_first: bool = False) -> str:
        parts = name.lower().split('_')
        result = parts[0]
        for part in parts[1:]:
            if part:
                result += part.capitalize()
        if upper_first and result:
            result = result[0].upper() + result[1:]
        return result

    class_name = to_camel_case(table_name, upper_first=False)
    mapper_name = to_camel_case(table_name, upper_first=True) + 'Mapper'

    datetime_type = 'Instant' if config.get('use_instant') else 'LocalDateTime'
    methods = config.get('methods', [])

    print("\n" + "=" * 50)
    print("=== 生成配置确认 ===")
    print("=" * 50)
    print(f"表名：{table_name}")
    print(f"→ 类名：{class_name}")
    print(f"→ Mapper: {mapper_name}")
    print(f"\n类型映射:")
    print(f"  DATETIME/TIMESTAMP → {datetime_type}")
    print(f"\n文件路径:")
    print(f"  POJO: {config.get('pojo_package', '未设置')}")
    print(f"  Mapper: {config.get('mapper_package', '未设置')}")
    print(f"  XML: {config.get('xml_path', '未设置')}")
    print(f"\n生成方法:")
    if methods:
        for m in methods:
            print(f"  - {m}")
    else:
        print("  仅生成 BaseResultMap 和 Base_Column_List")
    print("=" * 50)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python config_wizard.py <表名>")
        sys.exit(1)

    table_name = sys.argv[1]

    # 模拟列信息（实际使用时由用户输入）
    columns = []

    print("=" * 50)
    print("MyBatis 代码生成配置向导")
    print("=" * 50)

    # 1. 日期时间映射
    use_instant = prompt_datetime_mapping()

    # 2. 文件路径
    paths = prompt_file_paths()

    # 3. 方法选择
    methods = prompt_methods()

    # 汇总配置
    config = {
        'table_name': table_name,
        'use_instant': use_instant,
        **paths,
        'methods': methods
    }

    print_config_summary(table_name, columns, config)

    # 确认
    confirm = input("\n是否开始生成代码？(y/n, 默认 y): ").strip().lower()
    if confirm in ('', 'y', 'yes'):
        # 输出 JSON 配置供后续脚本使用
        print("\n配置已确认，输出 JSON 配置:")
        print(json.dumps(config, indent=2))
    else:
        print("\n已取消生成")
        sys.exit(0)


if __name__ == '__main__':
    main()
