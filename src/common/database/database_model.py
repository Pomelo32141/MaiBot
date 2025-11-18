"""
数据库模型定义模块

本模块使用 SQLModel (基于 Pydantic 和 SQLAlchemy) 定义所有数据库表模型。
SQLModel 提供了类型安全、数据验证和现代化的 ORM 功能。
"""

import datetime
import uuid
from typing import Optional

from sqlalchemy import Column, Float, inspect
from sqlmodel import Field, SQLModel

from .database import engine, get_session
from src.common.logger import get_logger

logger = get_logger("database_model")
# 请在此处定义您的数据库实例。
# 您需要取消注释并配置适合您的数据库的部分。
# 例如，对于 SQLite:
# db = SqliteDatabase('MaiBot.db')
#
# 对于 PostgreSQL:
# db = PostgresqlDatabase('your_db_name', user='your_user', password='your_password',
#                         host='localhost', port=5432)
#
# 对于 MySQL:
# db = MySQLDatabase('your_db_name', user='your_user', password='your_password',
#                    host='localhost', port=3306)


# 定义一个基础模型是一个好习惯，所有其他模型都应继承自它。
# 这允许您在一个地方为所有模型指定数据库。


class BaseModel(Model):
    class Meta:
        # 将下面的 'db' 替换为您实际的数据库实例变量名。
        database = db  # 例如: database = my_actual_db_instance
        pass  # 在用户定义数据库实例之前，此处为占位符


class ChatStreams(BaseModel):
    """
    用于存储流式记录数据的模型，类似于提供的 MongoDB 结构。
    """

    # stream_id: "a544edeb1a9b73e3e1d77dff36e41264"
    # 假设 stream_id 是唯一的，并为其创建索引以提高查询性能。
    stream_id = TextField(unique=True, index=True)

    # create_time: 1746096761.4490178 (时间戳，精确到小数点后7位)
    # DoubleField 用于存储浮点数，适合此类时间戳。
    create_time = DoubleField()

    # group_info 字段:
    #   platform: "qq"
    #   group_id: "941657197"
    #   group_name: "测试"
    group_platform = TextField(null=True)  # 群聊信息可能不存在
    group_id = TextField(null=True)
    group_name = TextField(null=True)

    # last_active_time: 1746623771.4825106 (时间戳，精确到小数点后7位)
    last_active_time = DoubleField()

    # platform: "qq" (顶层平台字段)
    platform = TextField()

    # user_info 字段:
    #   platform: "qq"
    #   user_id: "1787882683"
    #   user_nickname: "墨梓柒(IceSakurary)"
    #   user_cardname: ""
    user_platform = TextField()
    user_id = TextField()
    user_nickname = TextField()
    # user_cardname 可能为空字符串或不存在，设置 null=True 更具灵活性。
    user_cardname = TextField(null=True)


class LLMUsage(SQLModel, table=True):
    """
    LLM API 使用日志模型。
    
    记录每次 API 调用的详细信息,包括 token 使用量、成本和性能数据。
    """
    __tablename__ = "llm_usage"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    model_name: str = Field(index=True, max_length=255)
    model_assign_name: Optional[str] = Field(default=None, max_length=255)
    model_api_provider: Optional[str] = Field(default=None, max_length=255)
    user_id: str = Field(index=True, max_length=255)
    request_type: str = Field(index=True, max_length=255)
    endpoint: str = Field(max_length=500)
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    cost: float = Field(sa_column=Column(Float))
    time_cost: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    
    status: str = Field(max_length=255)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, index=True)


class Emoji(SQLModel, table=True):
    """
    表情包模型。
    
    管理表情包资源,包括路径、描述、使用统计等信息。
    """
    __tablename__ = "emoji"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    full_path: str = Field(unique=True, index=True, max_length=500)
    format: str = Field(max_length=50)
    emoji_hash: str = Field(index=True, max_length=255)
    description: str
    
    query_count: int = Field(default=0)
    is_registered: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    
    # 情感标签 (存储为文本,应用层序列化/反序列化)
    emotion: Optional[str] = Field(default=None)
    
    record_time: float = Field(sa_column=Column(Float))
    register_time: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    usage_count: int = Field(default=0)
    last_used_time: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))


class Messages(SQLModel, table=True):
    """
    消息记录模型。
    
    存储完整的消息数据,包括消息内容、发送者信息、处理信息等。
    """
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    message_id: str = Field(index=True, max_length=255)
    time: float = Field(sa_column=Column(Float))
    
    chat_id: str = Field(index=True, max_length=255)
    reply_to: Optional[str] = Field(default=None, max_length=255)
    
    interest_value: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    key_words: Optional[str] = Field(default=None)
    key_words_lite: Optional[str] = Field(default=None)
    
    is_mentioned: Optional[bool] = Field(default=None)
    is_at: Optional[bool] = Field(default=None)
    reply_probability_boost: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    
    # chat_info 扁平化字段
    chat_info_stream_id: str = Field(max_length=255)
    chat_info_platform: str = Field(max_length=255)
    chat_info_user_platform: str = Field(max_length=255)
    chat_info_user_id: str = Field(max_length=255)
    chat_info_user_nickname: str = Field(max_length=255)
    chat_info_user_cardname: Optional[str] = Field(default=None, max_length=255)
    chat_info_group_platform: Optional[str] = Field(default=None, max_length=255)
    chat_info_group_id: Optional[str] = Field(default=None, max_length=255)
    chat_info_group_name: Optional[str] = Field(default=None, max_length=255)
    chat_info_create_time: float = Field(sa_column=Column(Float))
    chat_info_last_active_time: float = Field(sa_column=Column(Float))
    
    # 用户信息
    user_platform: Optional[str] = Field(default=None, max_length=255)
    user_id: Optional[str] = Field(default=None, max_length=255)
    user_nickname: Optional[str] = Field(default=None, max_length=255)
    user_cardname: Optional[str] = Field(default=None, max_length=255)
    
    processed_plain_text: Optional[str] = Field(default=None)
    display_message: Optional[str] = Field(default=None)
    
    priority_mode: Optional[str] = Field(default=None, max_length=255)
    priority_info: Optional[str] = Field(default=None)
    
    additional_config: Optional[str] = Field(default=None)
    is_emoji: bool = Field(default=False)
    is_picid: bool = Field(default=False)
    is_command: bool = Field(default=False)
    is_notify: bool = Field(default=False)
    
    selected_expressions: Optional[str] = Field(default=None)


class ActionRecords(SQLModel, table=True):
    """
    动作记录模型。
    
    记录系统执行的各种动作及其详细信息。
    """
    __tablename__ = "action_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    action_id: str = Field(index=True, max_length=255)
    time: float = Field(sa_column=Column(Float))
    
    action_reasoning: Optional[str] = Field(default=None)
    action_name: str = Field(max_length=255)
    action_data: str
    action_done: bool = Field(default=False)
    
    action_build_into_prompt: bool = Field(default=False)
    action_prompt_display: str
    
    chat_id: str = Field(index=True, max_length=255)
    chat_info_stream_id: str = Field(max_length=255)
    chat_info_platform: str = Field(max_length=255)


class Images(SQLModel, table=True):
    """
    图像信息模型。
    
    管理图像资源的元数据和使用统计。
    """
    __tablename__ = "images"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    image_id: str = Field(default="", max_length=255)
    emoji_hash: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None)
    path: str = Field(unique=True, max_length=500)
    
    count: int = Field(default=1)
    timestamp: float = Field(sa_column=Column(Float))
    type: str = Field(max_length=50)
    vlm_processed: bool = Field(default=False)


class ImageDescriptions(SQLModel, table=True):
    """
    图像描述模型。
    
    存储图像的描述信息,用于图像检索和识别。
    """
    __tablename__ = "image_descriptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    type: str = Field(max_length=50)
    image_description_hash: str = Field(index=True, max_length=255)
    description: str
    timestamp: float = Field(sa_column=Column(Float))


class OnlineTime(SQLModel, table=True):
    """
    在线时长记录模型。
    
    追踪系统的在线时长统计。
    """
    __tablename__ = "online_time"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    duration: int  # 时长,单位:分钟
    start_timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    end_timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, index=True)

    class Meta:
        # database = db # 继承自 BaseModel
        table_name = "online_time"


class PersonInfo(BaseModel):
    """
    用于存储个人信息数据的模型。
    """

    is_known = BooleanField(default=False)  # 是否已认识
    person_id = TextField(unique=True, index=True)  # 个人唯一ID
    person_name = TextField(null=True)  # 个人名称 (允许为空)
    name_reason = TextField(null=True)  # 名称设定的原因
    platform = TextField()  # 平台
    user_id = TextField(index=True)  # 用户ID
    nickname = TextField(null=True)  # 用户昵称
    group_nick_name = TextField(null=True)  # 群昵称列表 (JSON格式，存储 [{"group_id": str, "group_nick_name": str}])
    memory_points = TextField(null=True)  # 个人印象的点
    know_times = FloatField(null=True)  # 认识时间 (时间戳)
    know_since = FloatField(null=True)  # 首次印象总结时间
    last_know = FloatField(null=True)  # 最后一次印象总结时间

    class Meta:
        # database = db # 继承自 BaseModel
        table_name = "person_info"


class GroupInfo(BaseModel):
    """
    用于存储群组信息数据的模型。
    """

    group_id = TextField(unique=True, index=True)  # 群组唯一ID
    group_name = TextField(null=True)  # 群组名称 (允许为空)
    platform = TextField()  # 平台
    group_impression = TextField(null=True)  # 群组印象
    member_list = TextField(null=True)  # 群成员列表 (JSON格式)
    topic = TextField(null=True)  # 群组基本信息

    create_time = FloatField(null=True)  # 创建时间 (时间戳)
    last_active = FloatField(null=True)  # 最后活跃时间
    member_count = IntegerField(null=True, default=0)  # 成员数量

    class Meta:
        # database = db # 继承自 BaseModel
        table_name = "group_info"


class Expression(BaseModel):
    """
    用于存储表达风格的模型。
    """

    situation = TextField()
    style = TextField()

    # new mode fields
    context = TextField(null=True)
    up_content = TextField(null=True)

    content_list = TextField(null=True)
    count = IntegerField(default=1)
    last_active_time = FloatField()
    chat_id = TextField(index=True)
    create_date = FloatField(null=True)  # 创建日期，允许为空以兼容老数据

    class Meta:
        table_name = "expression"


class Jargon(BaseModel):
    """
    用于存储俚语的模型
    """

    content = TextField()
    raw_content = TextField(null=True)
    type = TextField(null=True)
    translation = TextField(null=True)
    meaning = TextField(null=True)
    chat_id = TextField(index=True)
    is_global = BooleanField(default=False)
    count = IntegerField(default=0)
    is_jargon = BooleanField(null=True)  # None表示未判定，True表示是黑话，False表示不是黑话
    last_inference_count = IntegerField(null=True)  # 最后一次判定的count值，用于避免重启后重复判定
    is_complete = BooleanField(default=False)  # 是否已完成所有推断（count>=100后不再推断）
    inference_with_context = TextField(null=True)  # 基于上下文的推断结果（JSON格式）
    inference_content_only = TextField(null=True)  # 仅基于词条的推断结果（JSON格式）

    class Meta:
        table_name = "jargon"


class ChatHistory(BaseModel):
    """
    用于存储聊天历史概括的模型
    """

    chat_id = TextField(index=True)  # 聊天ID
    start_time = DoubleField()  # 起始时间
    end_time = DoubleField()  # 结束时间
    original_text = TextField()  # 对话原文
    participants = TextField()  # 参与的所有人的昵称，JSON格式存储
    theme = TextField()  # 主题：这段对话的主要内容，一个简短的标题
    keywords = TextField()  # 关键词：这段对话的关键词，JSON格式存储
    summary = TextField()  # 概括：对这段话的平文本概括
    count = IntegerField(default=0)  # 被检索次数
    forget_times = IntegerField(default=0)  # 被遗忘检查的次数

    class Meta:
        table_name = "chat_history"


class ThinkingBack(BaseModel):
    """
    用于存储记忆检索思考过程的模型
    """

    chat_id = TextField(index=True)  # 聊天ID
    question = TextField()  # 提出的问题
    context = TextField(null=True)  # 上下文信息
    found_answer = BooleanField(default=False)  # 是否找到答案
    answer = TextField(null=True)  # 答案内容
    thinking_steps = TextField(null=True)  # 思考步骤（JSON格式）
    create_time = DoubleField()  # 创建时间
    update_time = DoubleField()  # 更新时间

    class Meta:
        table_name = "thinking_back"


MODELS = [
    ChatStreams,
    LLMUsage,
    Emoji,
    Messages,
    Images,
    ImageDescriptions,
    OnlineTime,
    PersonInfo,
    Expression,
    ActionRecords,
    Jargon,
    ChatHistory,
    ThinkingBack,
]


def create_tables():
    """
    创建所有在模型中定义的数据库表。
    """
    with db:
        db.create_tables(MODELS)


def initialize_database(sync_constraints: bool = False) -> None:
    """
    初始化数据库,检查并创建缺失的表和字段。
    
    Args:
        sync_constraints: 是否同步字段约束。默认为 False。
                         如果为 True,会检查并修复字段的 NULL 约束不一致问题。
    
    功能:
        1. 检查所有模型对应的表是否存在
        2. 如果表不存在,则创建
        3. 检查现有表的字段是否完整
        4. 自动添加缺失的字段
        5. (可选) 同步字段约束
    """

    try:
        with db:  # 管理 table_exists 检查的连接
            for model in MODELS:
                table_name = model._meta.table_name
                if not db.table_exists(model):
                    logger.warning(f"表 '{table_name}' 未找到，正在创建...")
                    db.create_tables([model])
                    logger.info(f"表 '{table_name}' 创建成功")
                    continue

                # 检查字段
                cursor = db.execute_sql(f"PRAGMA table_info('{table_name}')")
                existing_columns = {row[1] for row in cursor.fetchall()}
                model_fields = set(model._meta.fields.keys())

                if missing_fields := model_fields - existing_columns:
                    logger.warning(f"表 '{table_name}' 缺失字段: {missing_fields}")

                for field_name, field_obj in model._meta.fields.items():
                    if field_name not in existing_columns:
                        logger.info(f"表 '{table_name}' 缺失字段 '{field_name}'，正在添加...")
                        field_type = field_obj.__class__.__name__
                        sql_type = {
                            "TextField": "TEXT",
                            "IntegerField": "INTEGER",
                            "FloatField": "FLOAT",
                            "DoubleField": "DOUBLE",
                            "BooleanField": "INTEGER",
                            "DateTimeField": "DATETIME",
                        }.get(field_type, "TEXT")
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {field_name} {sql_type}"
                        alter_sql += " NULL" if field_obj.null else " NOT NULL"
                        if hasattr(field_obj, "default") and field_obj.default is not None:
                            # 正确处理不同类型的默认值，跳过lambda函数
                            default_value = field_obj.default
                            if callable(default_value):
                                # 跳过lambda函数或其他可调用对象，这些无法在SQL中表示
                                pass
                            elif isinstance(default_value, str):
                                alter_sql += f" DEFAULT '{default_value}'"
                            elif isinstance(default_value, bool):
                                alter_sql += f" DEFAULT {int(default_value)}"
                            else:
                                alter_sql += f" DEFAULT {default_value}"
                        try:
                            db.execute_sql(alter_sql)
                            logger.info(f"字段 '{field_name}' 添加成功")
                        except Exception as e:
                            logger.error(f"添加字段 '{field_name}' 失败: {e}")

                # 检查并删除多余字段（新增逻辑）
                extra_fields = existing_columns - model_fields
                if extra_fields:
                    logger.warning(f"表 '{table_name}' 存在多余字段: {extra_fields}")
                for field_name in extra_fields:
                    try:
                        logger.warning(f"表 '{table_name}' 存在多余字段 '{field_name}'，正在尝试删除...")
                        db.execute_sql(f"ALTER TABLE {table_name} DROP COLUMN {field_name}")
                        logger.info(f"字段 '{field_name}' 删除成功")
                    except Exception as e:
                        logger.error(f"删除字段 '{field_name}' 失败: {e}")

        # 如果启用了约束同步，执行约束检查和修复
        if sync_constraints:
            logger.debug("开始同步数据库字段约束...")
            sync_field_constraints()
            logger.debug("数据库字段约束同步完成")
            
    except Exception as e:
        logger.exception(f"初始化数据库时出错: {e}")
        return
    
    logger.info("数据库初始化完成")


def _add_missing_columns(table_name: str, model: type[SQLModel], missing_fields: set[str]) -> None:
    """
    为表添加缺失的字段。
    
    Args:
        table_name: 表名
        model: SQLModel 模型类
        missing_fields: 缺失的字段名集合
    """
    with engine.begin() as conn:
        for field_name in missing_fields:
            if field_name not in model.__fields__:
                continue
                
            field_info = model.__fields__[field_name]
            field_type = field_info.type_
            
            # 获取 SQL 类型 (使用 is 进行类型比较)
            if field_type is str:
                sql_type = 'TEXT'
            elif field_type is int:
                sql_type = 'INTEGER'
            elif field_type is float:
                sql_type = 'REAL'
            elif field_type is bool:
                sql_type = 'INTEGER'
            elif field_type is datetime.datetime:
                sql_type = 'DATETIME'
            else:
                sql_type = 'TEXT'
            
            # 构建 ALTER TABLE 语句
            nullable = "NULL" if field_info.allow_none else "NOT NULL"
            
            # 获取默认值
            default_clause = ""
            if field_info.default is not None and not callable(field_info.default):
                if isinstance(field_info.default, str):
                    default_clause = f" DEFAULT '{field_info.default}'"
                elif isinstance(field_info.default, bool):
                    default_clause = f" DEFAULT {int(field_info.default)}"
                elif isinstance(field_info.default, (int, float)):
                    default_clause = f" DEFAULT {field_info.default}"
            
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {field_name} {sql_type} {nullable}{default_clause}"
            
            try:
                conn.execute(alter_sql)
                logger.info(f"字段 '{field_name}' 添加到表 '{table_name}' 成功")
            except Exception as e:
                logger.error(f"添加字段 '{field_name}' 到表 '{table_name}' 失败: {e}")


def _remove_extra_columns(table_name: str, extra_fields: set[str]) -> None:
    """
    删除表中的多余字段。
    
    Args:
        table_name: 表名
        extra_fields: 多余的字段名集合
    
    注意:
        SQLite 不支持直接删除列,需要重建表。
        此功能仅记录警告,不执行实际删除操作。
    """
    for field_name in extra_fields:
        logger.warning(
            f"表 '{table_name}' 存在多余字段 '{field_name}'。"
            f"SQLite 不支持删除列,请手动处理或重建表。"
        )


def sync_field_constraints() -> None:
    """
    同步数据库字段约束,确保现有数据库字段的 NULL 约束与模型定义一致。
    
    如果发现不一致,会自动修复字段约束。
    """

    try:
        with db:
            for model in MODELS:
                table_name = model._meta.table_name
                if not db.table_exists(model):
                    logger.warning(f"表 '{table_name}' 不存在，跳过约束检查")
                    continue

                logger.debug(f"检查表 '{table_name}' 的字段约束...")

                # 获取当前表结构信息
                cursor = db.execute_sql(f"PRAGMA table_info('{table_name}')")
                current_schema = {
                    row[1]: {"type": row[2], "notnull": bool(row[3]), "default": row[4]} for row in cursor.fetchall()
                }

                # 检查每个模型字段的约束
                constraints_to_fix = []
                for field_name, field_obj in model._meta.fields.items():
                    if field_name not in current_schema:
                        continue  # 字段不存在，跳过

                    current_notnull = current_schema[field_name]["notnull"]
                    model_allows_null = field_obj.null

                    # 如果模型允许 null 但数据库字段不允许 null，需要修复
                    if model_allows_null and current_notnull:
                        constraints_to_fix.append(
                            {
                                "field_name": field_name,
                                "field_obj": field_obj,
                                "action": "allow_null",
                                "current_constraint": "NOT NULL",
                                "target_constraint": "NULL",
                            }
                        )
                        logger.warning(f"字段 '{field_name}' 约束不一致: 模型允许NULL，但数据库为NOT NULL")

                    # 如果模型不允许 null 但数据库字段允许 null，也需要修复（但要小心）
                    elif not model_allows_null and not current_notnull:
                        constraints_to_fix.append(
                            {
                                "field_name": field_name,
                                "field_obj": field_obj,
                                "action": "disallow_null",
                                "current_constraint": "NULL",
                                "target_constraint": "NOT NULL",
                            }
                        )
                        logger.warning(f"字段 '{field_name}' 约束不一致: 模型不允许NULL，但数据库允许NULL")

                # 修复约束不一致的字段
                if constraints_to_fix:
                    logger.info(f"表 '{table_name}' 需要修复 {len(constraints_to_fix)} 个字段约束")
                    _fix_table_constraints(table_name, model, constraints_to_fix)
                else:
                    logger.debug(f"表 '{table_name}' 的字段约束已同步")

    except Exception as e:
        logger.exception(f"同步字段约束时出错: {e}")


def _fix_table_constraints(
    table_name: str, 
    model: type[SQLModel], 
    constraints_to_fix: list[dict]
) -> None:
    """
    修复表的字段约束。
    
    对于 SQLite,由于不支持直接修改列约束,需要重建表。
    
    Args:
        table_name: 表名
        model: SQLModel 模型类
        constraints_to_fix: 需要修复的约束列表
    """
    try:
        backup_table = f"{table_name}_backup_{int(datetime.datetime.now().timestamp())}"
        
        logger.info(f"开始修复表 '{table_name}' 的字段约束...")
        
        with engine.begin() as conn:
            # 1. 创建备份表
            conn.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table_name}")
            logger.info(f"已创建备份表 '{backup_table}'")
            
            # 2. 删除原表
            conn.execute(f"DROP TABLE {table_name}")
            logger.info(f"已删除原表 '{table_name}'")
        
        # 3. 重新创建表
        model.metadata.create_all(engine, tables=[model.__table__])
        logger.info(f"已重新创建表 '{table_name}'")
        
        # 4. 恢复数据
        fields = list(model.__fields__.keys())
        fields_str = ", ".join(fields)
        
        # 处理 NULL 到 NOT NULL 的字段
        null_to_notnull = [c['field_name'] for c in constraints_to_fix if c['action'] == 'disallow_null']
        
        with engine.begin() as conn:
            if null_to_notnull:
                logger.warning(f"字段 {null_to_notnull} 将从允许 NULL 改为不允许 NULL")
                
                # 构建 COALESCE 语句处理 NULL 值
                select_fields = []
                for field_name in fields:
                    if field_name in null_to_notnull:
                        field_info = model.__fields__[field_name]
                        field_type = field_info.type_
                        
                        if field_type is str:
                            default = "''"
                        elif field_type in (int, float):
                            default = "0"
                        elif field_type is bool:
                            default = "0"
                        elif field_type is datetime.datetime:
                            default = f"'{datetime.datetime.now()}'"
                        else:
                            default = "''"
                        
                        select_fields.append(f"COALESCE({field_name}, {default}) as {field_name}")
                    else:
                        select_fields.append(field_name)
                
                select_str = ", ".join(select_fields)
                insert_sql = f"INSERT INTO {table_name} ({fields_str}) SELECT {select_str} FROM {backup_table}"
            else:
                insert_sql = f"INSERT INTO {table_name} ({fields_str}) SELECT {fields_str} FROM {backup_table}"
            
            conn.execute(insert_sql)
            logger.info(f"已从备份表恢复数据到 '{table_name}'")
            
            # 5. 验证数据完整性
            original_count = conn.execute(f"SELECT COUNT(*) FROM {backup_table}").scalar()
            new_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").scalar()
            
            if original_count == new_count:
                logger.info(f"数据完整性验证通过: {original_count} 行数据")
                conn.execute(f"DROP TABLE {backup_table}")
                logger.info(f"已删除备份表 '{backup_table}'")
            else:
                logger.error(
                    f"数据完整性验证失败: 原始 {original_count} 行,新表 {new_count} 行。"
                    f"备份表 '{backup_table}' 已保留。"
                )
        
        # 记录修复的约束
        for constraint in constraints_to_fix:
            logger.info(
                f"已修复字段 '{constraint['field_name']}': "
                f"{constraint['current']} -> {constraint['target']}"
            )
            
    except Exception as e:
        logger.exception(f"修复表 '{table_name}' 约束时出错: {e}")
        raise


def check_field_constraints() -> dict[str, list[dict]]:
    """
    检查但不修复字段约束,返回不一致的字段信息。
    
    用于在修复前预览需要修复的内容。
    
    Returns:
        字典,键为表名,值为不一致字段的信息列表
    """

    inconsistencies = {}

    try:
        with db:
            for model in MODELS:
                table_name = model._meta.table_name
                if not db.table_exists(model):
                    continue

                # 获取当前表结构信息
                cursor = db.execute_sql(f"PRAGMA table_info('{table_name}')")
                current_schema = {
                    row[1]: {"type": row[2], "notnull": bool(row[3]), "default": row[4]} for row in cursor.fetchall()
                }

                table_inconsistencies = []

                # 检查每个模型字段的约束
                for field_name, field_obj in model._meta.fields.items():
                    if field_name not in current_schema:
                        continue

                    current_notnull = current_schema[field_name]["notnull"]
                    model_allows_null = field_obj.null

                    if model_allows_null and current_notnull:
                        table_inconsistencies.append(
                            {
                                "field_name": field_name,
                                "issue": "model_allows_null_but_db_not_null",
                                "model_constraint": "NULL",
                                "db_constraint": "NOT NULL",
                                "recommended_action": "allow_null",
                            }
                        )
                    elif not model_allows_null and not current_notnull:
                        table_inconsistencies.append(
                            {
                                "field_name": field_name,
                                "issue": "model_not_null_but_db_allows_null",
                                "model_constraint": "NOT NULL",
                                "db_constraint": "NULL",
                                "recommended_action": "disallow_null",
                            }
                        )

                if table_inconsistencies:
                    inconsistencies[table_name] = table_inconsistencies

    except Exception as e:
        logger.exception(f"检查字段约束时出错: {e}")

    return inconsistencies


def fix_image_id() -> None:
    """
    修复图片表的 image_id 字段,为空的 image_id 生成 UUID。
    """
    try:
        with get_session() as session:
            # 查询所有 image_id 为空的记录
            images = session.query(Images).filter(
                (Images.image_id == "") | (Images.image_id.is_(None))
            ).all()
            
            for img in images:
                img.image_id = str(uuid.uuid4())
                logger.info(f"已为图片 {img.id} 生成新的 image_id: {img.image_id}")
            
            session.commit()
            logger.info(f"共修复 {len(images)} 条图片记录的 image_id")
            
    except Exception as e:
        logger.exception(f"修复 image_id 时出错: {e}")


# ==================== 模块初始化 ====================

# 模块加载时自动初始化数据库
try:
    initialize_database(sync_constraints=True)
    fix_image_id()
except Exception as e:
    logger.error(f"数据库模块初始化失败: {e}")
