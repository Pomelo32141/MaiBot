from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.absolute().resolve()
CONFIG_DIR: Path = PROJECT_ROOT / "configs"
BOT_CONFIG_PATH: Path = (CONFIG_DIR / "bot_config.toml").resolve().absolute()
MODEL_CONFIG_PATH: Path = (CONFIG_DIR / "model_config.toml").resolve().absolute()
PLUGINS_DIR: Path = (PROJECT_ROOT / "plugins").resolve().absolute()
INTERNAL_PLUGINS_DIR: Path = (PROJECT_ROOT / "src" / "plugins").resolve().absolute()