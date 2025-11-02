from pathlib import Path
from typing import Optional
from collections.abc import Callable
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.api import ObservedWatch

import asyncio
import uuid

from src.config.config import CONFIG_DIR, PROJECT_ROOT

try:
    from src.common.logger import get_logger
except ImportError:
    from loguru import logger

    def get_logger(name: str):
        return logger


logger = get_logger("FileWatcher")


class WatchType(Enum):
    """监视类型枚举类"""

    BOT_CONFIG_CHANGE = 0b0001
    MODEL_CONFIG_CHANGE = 0b0010
    PLUGIN_CONFIG_CHANGE = 0b0100
    ALL_CONFIG_CHANGE = 0b0111
    PLUGIN_CODE_CHANGE = 0b1000
    ALL_CODE_CHANGE = 0b1000
    ALL_FILE_CHANGE = 0b1111


hierarchy_map: dict[WatchType, list[WatchType]] = {}


def dynamic_construct_hierarchy_map():
    global hierarchy_map
    for wt in WatchType:
        hierarchy_map[wt] = []
        for other_wt in WatchType:
            if other_wt != wt and (other_wt.value & wt.value) == other_wt.value:
                hierarchy_map[wt].append(other_wt)


class FileWatcher:
    """文件监视器类，用于监视文件的更改"""

    def __init__(self):
        self.observer = Observer()
        self.event_handler = FileSystemEventHandler() # TODO: 自定义事件处理器
        self.path_callbacks: dict[Path, set[Callable]] = {}
        self.type_callbacks: dict[WatchType, set[Callable]] = {wt: set() for wt in WatchType}
        self.callable_registration: dict[str, tuple[list[Path], list[WatchType], Callable]] = {}
        self.bot_config_path: Path = (CONFIG_DIR / "bot_config.toml").resolve().absolute()
        self.model_config_path: Path = (CONFIG_DIR / "model_config.toml").resolve().absolute()
        self.observer_watch_mapping: dict[Path, ObservedWatch] = {}
        self.excluded_paths: set[Path] = set()

    def register_callback(
        self,
        callback: Callable,
        *,
        watch_path: Optional[list[Path]] = None,
        watch_type: Optional[list[WatchType]] = None,
    ) -> str:
        """
        注册回调函数

        Args:
            callback (Callable): 回调函数
            watch_path (Optional[list[Path]]): 监视的路径列表
            watch_type (Optional[list[WatchType]]): 监视的类型列表

        watch_path和watch_type至少指定一个
        """
        assert isinstance(callback, Callable), "✍️✍️✍️回调函数必须是可调用的✍️✍️✍️"
        assert watch_path or watch_type, "✍️✍️✍️监视路径或监视类型必须指定✍️✍️✍️"
        if watch_type:
            for wt in watch_type:
                self.type_callbacks[wt].add(callback)
        if watch_path:
            for path in watch_path:
                path = path.resolve().absolute()
                self._add_path(path)
                self.path_callbacks.setdefault(path, set()).add(callback)
        uuid_str = str(uuid.uuid4())
        self.callable_registration[uuid_str] = (watch_path or [], watch_type or [], callback)
        return uuid_str

    def unregister_callback(self, uuid: str) -> None:
        """注销回调函数，移除所有与该回调函数相关的监视"""
        watch_path, watch_type, callback = self.callable_registration.get(uuid, ([], [], None))
        if not callback or not (watch_path or watch_type):
            logger.error(f"尝试注销不存在的回调函数或者函数监视为空，UUID: {uuid}")
            raise FileNotFoundError("尝试注销不存在的回调函数或者函数监视为空")
        for path in watch_path:
            path = path.resolve().absolute()
            if path in self.path_callbacks and callback in self.path_callbacks[path]:
                self.path_callbacks[path].remove(callback)
                if not self.path_callbacks[path]:
                    self._remove_path(path)
                    del self.path_callbacks[path]
        for wt in watch_type:
            if wt in self.type_callbacks and callback in self.type_callbacks[wt]:
                self.type_callbacks[wt].remove(callback)
        return

    async def call_callbacks(self, changed_path: Path, watch_type: Optional[WatchType] = None) -> None:
        """调用注册的回调函数"""
        if not changed_path.is_relative_to(PROJECT_ROOT):
            # 处理监视不在项目根目录下的路径
            for callback in self.path_callbacks.get(changed_path, []):
                await self._call_corresponding_callbacks(callback)
            return

        while changed_path != PROJECT_ROOT.parent.resolve().absolute():
            # 逐级向上查找路径对应的回调函数
            for callback in self.path_callbacks.get(changed_path, []):
                await self._call_corresponding_callbacks(callback)
            changed_path = changed_path.parent

        if watch_type:
            # 处理监视类型对应的回调函数
            for wt in hierarchy_map.get(watch_type, []):
                for callback in self.type_callbacks.get(wt, []):
                    await self._call_corresponding_callbacks(callback)

    async def _call_corresponding_callbacks(self, callback: Callable) -> None:
        """调用对应的回调函数"""
        if asyncio.iscoroutinefunction(callback):
            await callback()
        else:
            callback()

    def _add_path(self, path: Path) -> bool:
        """添加监视路径"""
        if path in self.observer_watch_mapping:
            logger.warning(f"路径已在监视列表中: {path}")
            return False
        observed_watch = self.observer.schedule(self.event_handler, str(path), recursive=True)
        self.observer_watch_mapping[path] = observed_watch
        return True

    def _remove_path(self, path: Path) -> bool:
        """移除监视路径"""
        if path not in self.observer_watch_mapping:
            logger.warning(f"尝试移除未监视的路径: {path}")
            return False
        observed_watch = self.observer_watch_mapping[path]
        self.observer.unschedule(observed_watch)
        del self.observer_watch_mapping[path]
        return True


dynamic_construct_hierarchy_map()
