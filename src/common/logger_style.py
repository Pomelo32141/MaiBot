# 定义模块颜色映射
MODULE_COLORS = {
    # 发送
    # "\033[38;5;67m" 这个颜色代码的含义如下：
    # \033         ：转义序列的起始，表示后面是控制字符（ESC）
    # [38;5;67m    ：
    #   38         ：设置前景色（字体颜色），如果是背景色则用 48
    #   5          ：表示使用8位（256色）模式
    #   67         ：具体的颜色编号（0-255），这里是较暗的蓝色
    "sender": "\033[38;5;24m",  # 67号色，较暗的蓝色，适合不显眼的日志
    "send_api": "\033[38;5;24m",  # 208号色，橙色，适合突出显示
    # 生成
    "replyer": "\033[38;5;208m",  # 橙色
    "llm_api": "\033[38;5;208m",  # 橙色
    # 消息处理
    "chat": "\033[38;5;82m",  # 亮蓝色
    "chat_image": "\033[38;5;68m",  # 浅蓝色
    # emoji
    "emoji": "\033[38;5;214m",  # 橙黄色，偏向橙色
    "emoji_api": "\033[38;5;214m",  # 橙黄色，偏向橙色
    # 核心模块
    "main": "\033[1;97m",  # 亮白色+粗体 (主程序)
    "memory": "\033[38;5;34m",  # 天蓝色
    "config": "\033[93m",  # 亮黄色
    "common": "\033[95m",  # 亮紫色
    "tools": "\033[96m",  # 亮青色
    "lpmm": "\033[96m",
    "plugin_system": "\033[91m",  # 亮红色
    "person_info": "\033[32m",  # 绿色
    "manager": "\033[35m",  # 紫色
    "llm_models": "\033[36m",  # 青色
    "remote": "\033[38;5;242m",  # 深灰色，更不显眼
    "planner": "\033[36m",
    "relation": "\033[38;5;139m",  # 柔和的紫色，不刺眼
    # 聊天相关模块
    "hfc": "\033[38;5;175m",  # 柔和的粉色，不显眼但保持粉色系
    "bc": "\033[38;5;175m",  # 柔和的粉色，不显眼但保持粉色系
    "sub_heartflow": "\033[38;5;207m",  # 粉紫色
    "subheartflow_manager": "\033[38;5;201m",  # 深粉色
    "background_tasks": "\033[38;5;240m",  # 灰色
    "chat_message": "\033[38;5;45m",  # 青色
    "chat_stream": "\033[38;5;51m",  # 亮青色
    "message_storage": "\033[38;5;33m",  # 深蓝色
    "expressor": "\033[38;5;166m",  # 橙色
    # 插件系统
    "plugins": "\033[31m",  # 红色
    "plugin_api": "\033[33m",  # 黄色
    "plugin_manager": "\033[38;5;208m",  # 红色
    "base_plugin": "\033[38;5;202m",  # 橙红色
    "base_command": "\033[38;5;208m",  # 橙色
    "component_registry": "\033[38;5;214m",  # 橙黄色
    "stream_api": "\033[38;5;220m",  # 黄色
    "config_api": "\033[38;5;226m",  # 亮黄色
    "heartflow_api": "\033[38;5;154m",  # 黄绿色
    "action_apis": "\033[38;5;118m",  # 绿色
    "independent_apis": "\033[38;5;82m",  # 绿色
    "database_api": "\033[38;5;10m",  # 绿色
    "utils_api": "\033[38;5;14m",  # 青色
    "message_api": "\033[38;5;6m",  # 青色
    # 管理器模块
    "async_task_manager": "\033[38;5;129m",  # 紫色
    "mood": "\033[38;5;135m",  # 紫红色
    "local_storage": "\033[38;5;141m",  # 紫色
    "willing": "\033[38;5;147m",  # 浅紫色
    # 工具模块
    "tool_use": "\033[38;5;172m",  # 橙褐色
    "tool_executor": "\033[38;5;172m",  # 橙褐色
    "base_tool": "\033[38;5;178m",  # 金黄色
    # 工具和实用模块
    "prompt_build": "\033[38;5;105m",  # 紫色
    "chat_utils": "\033[38;5;111m",  # 蓝色
    "maibot_statistic": "\033[38;5;129m",  # 紫色
    # 特殊功能插件
    "mute_plugin": "\033[38;5;240m",  # 灰色
    "core_actions": "\033[38;5;117m",  # 深红色
    "tts_action": "\033[38;5;58m",  # 深黄色
    "doubao_pic_plugin": "\033[38;5;64m",  # 深绿色
    # Action组件
    "no_reply_action": "\033[38;5;214m",  # 亮橙色，显眼但不像警告
    "reply_action": "\033[38;5;46m",  # 亮绿色
    "base_action": "\033[38;5;250m",  # 浅灰色
    # 数据库和消息
    "database_model": "\033[38;5;94m",  # 橙褐色
    "maim_message": "\033[38;5;140m",  # 紫褐色
    # 日志系统
    "logger": "\033[38;5;8m",  # 深灰色
    "confirm": "\033[1;93m",  # 黄色+粗体
    # 模型相关
    "model_utils": "\033[38;5;164m",  # 紫红色
    "relationship_fetcher": "\033[38;5;170m",  # 浅紫色
    "relationship_builder": "\033[38;5;93m",  # 浅蓝色
    "conflict_tracker": "\033[38;5;82m",  # 柔和的粉色，不显眼但保持粉色系
}

# 定义模块别名映射 - 将真实的logger名称映射到显示的别名
MODULE_ALIASES = {
    # 示例映射
    "sender": "消息发送",
    "send_api": "消息发送API",
    "replyer": "言语",
    "llm_api": "生成API",
    "emoji": "表情包",
    "emoji_api": "表情包API",
    "chat": "所见",
    "chat_image": "识图",
    "action_manager": "动作",
    "memory_activator": "记忆",
    "tool_use": "工具",
    "expressor": "表达方式",
    "database_model": "数据库",
    "mood": "情绪",
    "memory": "记忆",
    "tool_executor": "工具",
    "hfc": "聊天节奏",
    "plugin_manager": "插件",
    "relationship_builder": "关系",
    "llm_models": "模型",
    "person_info": "人物",
    "chat_stream": "聊天流",
    "planner": "规划器",
    "config": "配置",
    "main": "主程序",
}
