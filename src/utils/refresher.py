
from src.main import Main
from src.features.databases import FirebaseClient
from typing import Optional
from copy import deepcopy

class Refresher:
    def __init__(self, pipeline: Optional[Main] = None) -> None:
        self.pipeline = pipeline or Main()
        self.db = FirebaseClient.get_instance()
        self._all_data = {}

    def run(self, link:str, hard:bool=False) -> None:
        """
        Get all links from the database
        Rerun with certain preconditions for each

        Soft run:\n
        L> Only certain sections are reset\n
            L> Overview -> Subjects & Tags\n
            L> Eligibility\n
            L> Dates\n
            L> Locations\n
            L> Costs\n
            L> Metadata\n

        Hard run:\n
        L> All sections are reset
        """
        pass

    @staticmethod
    def _refresh_condition() -> bool:
        return False

    def __get_all_data(self, collection_path:str) -> None:
        self._all_data[collection_path] = self.db.get_all_data(collection_path)

    def _get_latest_entry(self, collection_path:str, link:str) -> dict[str, dict]:
        # If the database hasn't been read yet, do so
        if not self._all_data:
            self.__get_all_data(collection_path)

        # Documents end with a "-" followed by a number representing the version of the doc
        # Find all data with the same link as the link provided
        docs_with_link: dict[int, dict] = {}
        for doc in self._all_data[collection_path]:
            id = '-'.join(doc.split('-')[:-1])
            ver = doc.split('-')[-1]
            if link == id:
                # {version: {id: data}}
                docs_with_link[ver] = {id: self._all_data[collection_path][doc]}

        max_ver: int = max(docs_with_link.keys())
        return docs_with_link[max_ver]

    def _soft_run(self, link:str) -> None:
        
        self.pipeline.schema.overview
        pass

    def _hard_run(self, link:str) -> None:
        pass

if __name__ == "__main__":
    r = Refresher()
    print(r._get_latest_entry("programs-display", "https:\\\\precollegesummer.rutgers.edu\\scholars"))
    print(r._get_latest_entry("programs-display", "https:\\\\opportunitynetwork.org\\apply\\"))
    print(r._get_latest_entry("programs-display", "https:\\\\sumac.spcs.stanford.edu\\sumac-online-program"))