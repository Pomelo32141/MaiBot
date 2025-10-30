from dataclasses import fields
from tomlkit import items
import tomlkit

from .config_base import ConfigBase


def recursive_parse_item_to_table(config: ConfigBase) -> items.Table:
    """递归解析配置项为表格"""
    config_table = tomlkit.table()
    for config_item in fields(config):
        if not config_item.repr:
            continue
        value = getattr(config, config_item.name)
        if isinstance(value, ConfigBase):
            config_table.add(config_item.name, recursive_parse_item_to_table(value))
        else:
            config_table.add(config_item.name, value)
        config_table = comment_doc_string(config, config_item.name, config_table)
    return config_table


def comment_doc_string(config: ConfigBase, field_name: str, toml_table: items.Table) -> items.Table:
    """将配置类中的注释加入toml表格中"""
    if doc_string := config.field_docs.get(field_name, ""):
        doc_string_splitted = doc_string.splitlines()
        if len(doc_string_splitted) == 1:
            toml_table[field_name].comment(doc_string_splitted[0])
        else:
            for line in doc_string_splitted:
                toml_table.add(tomlkit.comment(line))
            toml_table.add(tomlkit.nl())
    return toml_table
