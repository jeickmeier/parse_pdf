"""Configuration management for document parsers."""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional, cast
import json
import yaml
from .exceptions import ConfigurationError


@dataclass
class ParserConfig:
    """Configuration for parsers."""

    # Directory settings
    cache_dir: Path = Path("cache")
    output_dir: Path = Path("outputs")

    # Processing settings
    max_workers: int = 15
    timeout: int = 60
    retry_count: int = 3
    batch_size: int = 1
    use_cache: bool = True

    # Model settings
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: Optional[str] = None

    # Output settings
    output_format: str = "markdown"

    # Parser-specific settings
    parser_settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure paths are Path objects."""
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_file(cls, config_path: Path) -> "ParserConfig":
        """
        Load configuration from YAML or JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            ParserConfig instance

        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                if config_path.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif config_path.suffix == ".json":
                    data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported config format: {config_path.suffix}"
                    )

            return cls(**data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        data = asdict(self)
        # Convert Path objects to strings
        data["cache_dir"] = str(self.cache_dir)
        data["output_dir"] = str(self.output_dir)
        return data

    def save(self, config_path: Path) -> None:
        """
        Save configuration to file.

        Args:
            config_path: Path to save configuration to
        """
        data = self.to_dict()

        with open(config_path, "w") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)

    def get_parser_config(self, parser_name: str) -> Dict[str, Any]:
        """
        Get configuration for specific parser.

        Args:
            parser_name: Name of the parser

        Returns:
            Parser-specific configuration dictionary
        """
        return cast(Dict[str, Any], self.parser_settings.get(parser_name, {}))
