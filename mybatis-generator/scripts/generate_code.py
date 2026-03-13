#!/usr/bin/env python3
"""
MyBatis 代码生成器
根据表结构生成 POJO、Mapper 接口和 Mapper XML

支持配置：
- use_instant: 使用 Instant 代替 LocalDateTime 映射日期时间类型
- pojo_package: POJO 类包路径
- mapper_package: Mapper 接口包路径
- methods: 需要生成的方法列表
"""

import sys
from convert_name import to_camel_case, to_java_type


def generate_pojo(table_name: str, columns: list[tuple], package: str, use_instant: bool = False) -> str:
    """生成 POJO 类

    Args:
        table_name: 表名
        columns: 字段列表 [(col_name, col_type, comment), ...]
        package: 包路径
        use_instant: 是否使用 Instant 代替 LocalDateTime
    """
    class_name_pascal = to_camel_case(table_name, upper_first=True)

    # 收集需要的 import
    imports = {'lombok.Getter', 'lombok.Setter'}
    fields = []

    for col_name, col_type, comment in columns:
        prop_name = to_camel_case(col_name)
        java_type, _ = to_java_type(col_type, use_instant=use_instant)
        fields.append(f"    /**\n     * {comment}\n     */\n    private {java_type} {prop_name};")

        # 收集额外 import
        if java_type == 'LocalDateTime':
            imports.add('java.time.LocalDateTime')
        elif java_type == 'Instant':
            imports.add('java.time.Instant')
        elif java_type == 'LocalDate':
            imports.add('java.time.LocalDate')
        elif java_type == 'LocalTime':
            imports.add('java.time.LocalTime')
        elif java_type == 'BigDecimal':
            imports.add('java.math.BigDecimal')

    fields_code = "\n\n".join(fields)
    imports_code = "\n".join(f"import {imp};" for imp in sorted(imports))

    return f"""package {package};

import lombok.Getter;
import lombok.Setter;
{imports_code}

@Getter
@Setter
public class {class_name_pascal} {{
{fields_code}
}}
"""


def generate_mapper(table_name: str, columns: list[tuple], pojo_package: str, mapper_package: str, methods: list[str]) -> str:
    """生成 Mapper 接口

    Args:
        table_name: 表名
        columns: 字段列表
        pojo_package: POJO 包路径
        mapper_package: Mapper 包路径
        methods: 需要生成的方法列表
    """
    class_name_pascal = to_camel_case(table_name, upper_first=True)

    method_signatures = {
        'insert': f"    int insert({class_name_pascal} {to_camel_case(table_name)});",
        'insertSelective': f"    int insertSelective({class_name_pascal} {to_camel_case(table_name)});",
        'selectByPrimaryKey': f"    {class_name_pascal} selectByPrimaryKey(Long id);",
        'updateByPrimaryKey': f"    int updateByPrimaryKey({class_name_pascal} {to_camel_case(table_name)});",
        'updateByPrimaryKeySelective': f"    int updateByPrimaryKeySelective({class_name_pascal} {to_camel_case(table_name)});",
        'deleteByPrimaryKey': f"    int deleteByPrimaryKey(Long id);",
    }

    methods_code = "\n".join(method_signatures[m] for m in methods if m in method_signatures)

    if not methods_code.strip():
        methods_code = "    // TODO: 选择需要生成的方法"

    return f"""package {mapper_package};

import {pojo_package}.{class_name_pascal};

public interface {class_name_pascal}Mapper {{
{methods_code}
}}
"""


def generate_xml(table_name: str, columns: list[tuple], pojo_package: str, mapper_package: str,
                 methods: list[str], use_instant: bool = False) -> str:
    """生成 Mapper XML

    Args:
        table_name: 表名
        columns: 字段列表
        pojo_package: POJO 包路径
        mapper_package: Mapper 包路径
        methods: 需要生成的方法列表
        use_instant: 是否使用 Instant
    """
    class_name_pascal = to_camel_case(table_name, upper_first=True)
    mapper_name = f"{mapper_package}.{class_name_pascal}Mapper"

    # 生成 resultMap
    result_map_lines = [f'        <resultMap id="BaseResultMap" type="{pojo_package}.{class_name_pascal}">']
    for col_name, col_type, _ in columns:
        prop_name = to_camel_case(col_name)
        java_type, jdbc_type = to_java_type(col_type, use_instant=use_instant)
        tag = 'id' if col_name.lower() == 'id' else 'result'
        result_map_lines.append(f'            <{tag} column="{col_name}" jdbcType="{jdbc_type}" property="{prop_name}" />')
    result_map_lines.append('        </resultMap>')
    result_map = "\n".join(result_map_lines)

    # 生成 Base_Column_List
    column_list = ", ".join(col[0] for col in columns)
    column_list_sql = f'    <sql id="Base_Column_List">\n        {column_list}\n    </sql>'

    # 生成方法 SQL
    method_sqls = []

    if 'selectByPrimaryKey' in methods:
        method_sqls.append(f'''
    <select id="selectByPrimaryKey" parameterType="java.lang.Long" resultMap="BaseResultMap">
        select
        <include refid="Base_Column_List" />
        from {table_name}
        where id = #{{id}}
    </select>''')

    if 'insert' in methods:
        insert_cols = ", ".join(col[0] for col in columns if col[0].lower() != 'id')
        insert_vals = ", ".join("#{" + to_camel_case(col[0]) + "}" for col in columns if col[0].lower() != 'id')
        method_sqls.append(f'''
    <insert id="insert" parameterType="{pojo_package}.{class_name_pascal}" useGeneratedKeys="true" keyProperty="id">
        insert into {table_name} ({insert_cols})
        values ({insert_vals})
    </insert>''')

    if 'insertSelective' in methods:
        method_sqls.append(f'''
    <insert id="insertSelective" parameterType="{pojo_package}.{class_name_pascal}" useGeneratedKeys="true" keyProperty="id">
        insert into {table_name}
        <trim prefix="(" suffix=")" suffixOverrides=",">
{chr(10).join(f'            <if test="{to_camel_case(col[0])} != null">{col[0]},</if>' for col in columns if col[0].lower() != 'id')}
        </trim>
        <trim prefix="values (" suffix=")" suffixOverrides=",">
{chr(10).join(f'            <if test="{to_camel_case(col[0])} != null">#{to_camel_case(col[0])},</if>' for col in columns if col[0].lower() != 'id')}
        </trim>
    </insert>''')

    if 'deleteByPrimaryKey' in methods:
        method_sqls.append(f'''
    <delete id="deleteByPrimaryKey" parameterType="java.lang.Long">
        delete from {table_name}
        where id = #{{id}}
    </delete>''')

    if 'updateByPrimaryKey' in methods:
        update_sets = "\n".join(
            f'            {col[0]} = #{{{to_camel_case(col[0])}}},'
            for col in columns if col[0].lower() != 'id'
        )
        method_sqls.append(f'''
    <update id="updateByPrimaryKey" parameterType="{pojo_package}.{class_name_pascal}">
        update {table_name}
        <set>
{update_sets}
        </set>
        where id = #{{id}}
    </update>''')

    if 'updateByPrimaryKeySelective' in methods:
        update_sets = "\n".join(
            f'            <if test="{to_camel_case(col[0])} != null">{col[0]} = #{{{to_camel_case(col[0])}}},</if>'
            for col in columns if col[0].lower() != 'id'
        )
        method_sqls.append(f'''
    <update id="updateByPrimaryKeySelective" parameterType="{pojo_package}.{class_name_pascal}">
        update {table_name}
        <set>
{update_sets}
        </set>
        where id = #{{id}}
    </update>''')

    methods_xml = "\n".join(method_sqls)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{mapper_name}">

{result_map}

{column_list_sql}
{methods_xml}

</mapper>
'''


def print_config_summary(table_name: str, columns: list, config: dict) -> str:
    """打印配置汇总"""
    class_name = to_camel_case(table_name, upper_first=False)
    mapper_name = to_camel_case(table_name, upper_first=True) + 'Mapper'

    datetime_type = 'Instant' if config.get('use_instant') else 'LocalDateTime'
    methods = config.get('methods', [])

    summary = f"""
=== 生成配置确认 ===
表名：{table_name}
→ 类名：{class_name}
→ Mapper: {mapper_name}

类型映射:
  DATETIME/TIMESTAMP → {datetime_type}

文件路径:
  POJO: {config.get('pojo_package', '未设置')}
  Mapper: {config.get('mapper_package', '未设置')}
  XML: {config.get('xml_path', '未设置')}

生成方法:
  {', '.join(methods) if methods else '仅生成 BaseResultMap 和 Base_Column_List'}
"""
    return summary


if __name__ == '__main__':
    print("MyBatis 代码生成器")
    print("用法：请在 Python 脚本中调用 generate_* 函数")
    print("\n可用函数:")
    print("  - generate_pojo(table_name, columns, package, use_instant)")
    print("  - generate_mapper(table_name, columns, pojo_package, mapper_package, methods)")
    print("  - generate_xml(table_name, columns, pojo_package, mapper_package, methods, use_instant)")
    print("  - print_config_summary(table_name, columns, config)")
