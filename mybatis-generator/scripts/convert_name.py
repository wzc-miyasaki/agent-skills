#!/usr/bin/env python3
"""
数据库字段名到 Java 属性名转换工具
表名转类名 (小驼峰): user_info -> userInfo
字段名转属性名 (小驼峰): user_id -> userId
表名转 Mapper 接口名 (大驼峰 + Mapper): user_info -> UserInfoMapper
"""

import re
import sys


def to_camel_case(name: str, upper_first: bool = False) -> str:
    """将下划线命名转换为驼峰命名"""
    parts = name.lower().split('_')
    result = parts[0]
    for part in parts[1:]:
        if part:
            result += part.capitalize()
    if upper_first and result:
        result = result[0].upper() + result[1:]
    return result


def to_java_type(mysql_type: str, use_instant: bool = False) -> tuple[str, str]:
    """MySQL 类型转 Java 类型和 JdbcType

    Args:
        mysql_type: MySQL 数据类型
        use_instant: 是否使用 Instant 代替 LocalDateTime
    """
    mysql_type_upper = mysql_type.upper()

    # 日期时间类型映射（可配置）
    datetime_java_type = 'Instant' if use_instant else 'LocalDateTime'
    datetime_jdbc_type = 'TIMESTAMP'

    type_mapping = {
        'BIGINT': ('Long', 'BIGINT'),
        'INT': ('Integer', 'INTEGER'),
        'SMALLINT': ('Integer', 'SMALLINT'),
        'TINYINT': ('Integer', 'TINYINT'),
        'VARCHAR': ('String', 'VARCHAR'),
        'CHAR': ('String', 'CHAR'),
        'TEXT': ('String', 'LONGVARCHAR'),
        'LONGTEXT': ('String', 'LONGVARCHAR'),
        'MEDIUMTEXT': ('String', 'LONGVARCHAR'),
        'DATETIME': (datetime_java_type, datetime_jdbc_type),
        'TIMESTAMP': (datetime_java_type, datetime_jdbc_type),
        'DATE': ('LocalDate', 'DATE'),
        'TIME': ('LocalTime', 'TIME'),
        'DECIMAL': ('BigDecimal', 'DECIMAL'),
        'NUMERIC': ('BigDecimal', 'DECIMAL'),
        'DOUBLE': ('Double', 'DOUBLE'),
        'FLOAT': ('Float', 'REAL'),
        'BIT': ('Boolean', 'BOOLEAN'),
        'BOOLEAN': ('Boolean', 'BOOLEAN'),
    }

    # 处理 TINYINT(1) 特殊情况
    if 'TINYINT(1)' in mysql_type_upper:
        return ('Boolean', 'BOOLEAN')

    # 提取基础类型
    base_type = re.sub(r'\(.*\)', '', mysql_type_upper)

    return type_mapping.get(base_type, ('String', 'VARCHAR'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python convert_name.py <name> [--upper] [--instant]")
        sys.exit(1)

    name = sys.argv[1]
    upper = '--upper' in sys.argv
    instant = '--instant' in sys.argv

    if upper:
        print(to_camel_case(name, upper_first=True))
    else:
        print(to_camel_case(name))
