# %%
from langchain_core.documents import Document
from load.base_load import BaseLoad
from load.synthetic_data_loaders import ForumSyntheticDataLoader
from util.util_main import to_serialized_parquet
import pandas as pd


class MongoLoad(BaseLoad, ForumSyntheticDataLoader):
    folder_name = "mongo"

    def __init__(self):
        super().__init__()

    def create_merged_df(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """Merge all datasets into a single dataframe and perform operations."""
        df = pd.concat(dfs)
        df = self.normalize_columns(df)
        df = self.ner(df)
        return df

    def load_docs(self, documents: list[Document]) -> list[Document]:
        """
        Process documents using ForumSyntheticDataLoader.

        Args:
            documents: List of documents to process

        Returns:
            Processed documents with additional metadata
        """
        # Remove unwanted metadata fields
        for doc in documents:
            doc.metadata.pop("post_tags", None)
            doc.metadata.pop("post_category_id", None)

        self.create_capped_batchfiles(documents)
        return documents

    def drop_rows_with_longest_page_content(self, n: int = 15) -> None:
        """
        For Pinecone. A few rows have page_content that is too long for Pinecone.
        This fixes that.  May need to increase n by a few more rows.
        """
        df = self.get_artifact()
        df = df.drop(df["page_content"].str.len().nlargest(n).index)
        to_serialized_parquet(df, self.staging_folder / "staging.parquet")
        print(df.info())
