"""
配置管理
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """配置类"""

    def __init__(self, config_dict: Dict[str, Any]):
        """
        初始化配置

        Args:
            config_dict: 配置字典
        """
        self._config = config_dict

    @classmethod
    def load(cls, config_path: str = None) -> 'Config':
        """
        加载配置

        Args:
            config_path: 配置文件路径（可选）

        Returns:
            配置对象
        """
        # 加载环境变量
        load_dotenv()

        # 确定配置文件路径
        if config_path is None:
            # 使用默认路径
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / 'config' / 'config.yaml'

        # 加载 YAML 配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        # 替换环境变量
        config_dict = cls._replace_env_vars(config_dict)

        return cls(config_dict)

    @classmethod
    def _replace_env_vars(cls, config: Any) -> Any:
        """
        递归替换配置中的环境变量

        Args:
            config: 配置值

        Returns:
            替换后的配置值
        """
        if isinstance(config, dict):
            return {k: cls._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [cls._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            # 提取环境变量名
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        else:
            return config

    def __getitem__(self, key: str) -> Any:
        """字典式访问"""
        return self._config[key]

    def __getattr__(self, key: str) -> Any:
        """属性式访问"""
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self._config.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        """安全获取配置值"""
        return self._config.get(key, default)
