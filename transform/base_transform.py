from abc import abstractmethod
import logging
from typing import Any, Dict
from config import global_config, ConfigType
import pandas as pd
import pyarrow
import pyarrow.parquet as pq
from pathlib import Path


logger = logging.getLogger('transformer')


class BaseTransform:
    """Base class for all data transformers."""

    def __init__(self, folder_name: str):
        self.folder_name = folder_name

    @property
    def config(self) -> ConfigType:
        """Get the global config singleton."""
        return global_config

    @abstractmethod
    def transform_file(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Transform the data according to implementation-specific rules.

        Args:
            data: Dictionary containing the raw data

        Returns:
            DataFrame containing the transformed data
        """
        pass

    def transform(self) -> None:
        """Process all files in raw directory and save to staging."""
        raw_dir = Path("data") / self.folder_name / "raw"
        staging_dir = self._ensure_dir()

        if not raw_dir.exists():
            raise FileNotFoundError(f"Raw directory does not exist: {raw_dir}")

        for file_path in raw_dir.glob("*"):
            try:
                df = self.transform_file(file_path)
                output_path = staging_dir / f"{file_path.stem}.parquet"
                pq.write_table(pyarrow.Table.from_pandas(df), output_path)

            except Exception as e:
                logger.error(f"Error processing {file_path}")
                raise e

    def _ensure_dir(self) -> Path:
        """Create and return path to staging directory."""
        dir_path = Path("data") / self.folder_name / "staging"
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
