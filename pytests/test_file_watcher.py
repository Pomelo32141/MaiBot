# 本文件为测试文件，请忽略Lint error，内含大量的ignore标识

from importlib import util
from pathlib import Path
import sys
import asyncio
import pytest

# 日志记录器模块解决
TEST_ROOT: Path = Path(__file__).parent.absolute().resolve()
logger_file = TEST_ROOT / "logger.py"
spec = util.spec_from_file_location("src.common.logger", logger_file)
module = util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(module)  # type: ignore
sys.modules["src.common.logger"] = module

# 路径依赖解决
PROJECT_ROOT: Path = Path(__file__).parent.parent.absolute().resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.common.utils.file_watcher import FileWatcher, ChangeType  # noqa: E402


def test_file_watcher_add_remove_path(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        test_path = tmp_path / "test_dir"
        test_path.mkdir()
        test_file = test_path / "test_file.txt"
        test_file.touch()

        def callback(changed_path: Path, change_type: ChangeType):
            print(f"File changed: {changed_path}, Change type: {change_type}")

        uuid_str = await watcher.register_callback(callback, "test_callback", watch_path=[test_file])
        await watcher.unregister_callback(uuid_str)

    asyncio.run(run_test())


def test_watcher_call_on_file_modified_multiple(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        test_path = tmp_path / "a_testdir"
        test_path.mkdir(exist_ok=True)
        test_file = test_path / "000.txt"
        test_file.touch()
        test_file2 = test_path / "111.txt"

        called_1 = False
        called_2 = False

        async def callback_1(changed_path: Path, change_type: ChangeType):
            nonlocal called_1
            assert change_type == ChangeType.MODIFIED
            called_1 = True

        async def callback_2(changed_path: Path, change_type: ChangeType):
            nonlocal called_2
            assert change_type == ChangeType.CREATED
            called_2 = True

        uuid_str = await watcher.register_callback(callback_1, "test_callback", watch_path=[test_file])
        uuid_str2 = await watcher.register_callback(callback_2, "test_callback2", watch_path=[test_file2])
        await asyncio.sleep(0.1)  # 确保监视器启动
        test_file.write_text("modification 1")
        test_file2.touch(exist_ok=False)
        await asyncio.sleep(0.2)  # 等待回调执行
        await watcher.unregister_callback(uuid_str)
        await watcher.unregister_callback(uuid_str2)
        assert called_1, "Callback 1 was not called"
        assert called_2, "Callback 2 was not called"

    asyncio.run(run_test())


def test_watcher_not_call_on_canceled_callback(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        test_path = tmp_path / "b_testdir"
        test_path.mkdir(exist_ok=True)
        test_file = test_path / "testfile.txt"
        test_file.touch()

        called = False

        async def callback(changed_path: Path, change_type: ChangeType):
            nonlocal called
            called = True

        uuid_str = await watcher.register_callback(callback, "test_callback", watch_path=[test_file])
        await asyncio.sleep(0.1)  # 确保监视器启动
        await watcher.unregister_callback(uuid_str)
        test_file.write_text("modification after unregister")
        await asyncio.sleep(0.1)  # 确保回调取消
        assert not called, "Callback was called after being unregistered"

    asyncio.run(run_test())


def test_watcher_not_call_on_unrelated_file_change(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        test_path = tmp_path / "c_testdir"
        test_path.mkdir(exist_ok=True)
        test_file = test_path / "watched_file.txt"
        test_file.touch()
        unrelated_file = test_path / "unrelated_file.txt"
        unrelated_file.touch()

        called = False

        async def callback(changed_path: Path, change_type: ChangeType):
            nonlocal called
            called = True

        uuid_str = await watcher.register_callback(callback, "test_callback", watch_path=[test_file])
        await asyncio.sleep(0.1)  # 确保监视器启动
        unrelated_file.write_text("modification of unrelated file")
        await asyncio.sleep(0.2)  # 等待回调执行
        await watcher.unregister_callback(uuid_str)
        assert not called, "Callback was called for unrelated file change"

    asyncio.run(run_test())


def test_watcher_call_with_correct_path(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        test_path = tmp_path / "d_testdir"
        test_path.mkdir(exist_ok=True)
        test_file = test_path / "specific_file.txt"
        test_file.touch()

        received_path = None
        called = False

        async def callback(changed_path: Path, change_type: ChangeType):
            nonlocal received_path
            nonlocal called
            called = True
            received_path = changed_path

        uuid_str = await watcher.register_callback(callback, "test_callback", watch_path=[test_file])
        await asyncio.sleep(0.1)  # 确保监视器启动
        test_file.write_text("modification to check path")
        await asyncio.sleep(0.2)  # 等待回调执行
        await watcher.unregister_callback(uuid_str)
        assert called, "Callback was not called"
        assert received_path == test_file, f"Callback received incorrect path: {received_path}"

    asyncio.run(run_test())


def test_raise_exception_on_non_exist_path_watch(tmp_path: Path):
    async def run_test():
        watcher = FileWatcher()

        non_exist_path = tmp_path / "non_exist_dir" / "file.txt"

        async def callback(changed_path: Path, change_type: ChangeType):
            pass

        with pytest.raises(FileNotFoundError) as exc_info:
            await watcher.register_callback(callback, "test_callback", watch_path=[non_exist_path])
        assert exc_info.type is FileNotFoundError
        assert "尝试监视不存在的路径" in str(exc_info.value)

    asyncio.run(run_test())
