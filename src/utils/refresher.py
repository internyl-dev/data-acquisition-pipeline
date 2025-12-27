
from typing import Optional
from copy import deepcopy
from pprint import pp

from src.main import Main
from src.models import RootSchema
from src.features.databases import FirebaseClient


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
    def _refresh_condition(max_days: int) -> bool:
        """
        Decides whether or not to refresh a program
        Currently does it based on the date added (if date added is greater than the time specified)
        Args:
            max_days (int): The amount of days since the date added until an internship can be refreshed
        """
        return False

    def __get_all_data(self, collection_path:str) -> None:
        "Reads the database and gets all data from the specified collection path and sets the non-static variable"
        self._all_data[collection_path] = self.db.get_all_data(collection_path)

    def _get_latest_entry(self, collection_path:str, link:str) -> dict[str, dict]:
        """
        Gets the latest data entry of the specified link
        Returns:
            {id (str): data (dict)}
        """
        # If the database hasn't been read yet, do so
        if not collection_path in self._all_data:
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

    def _soft_run(self, link:str, collection_path: str = "programs-display") -> None:
        doc: RootSchema = RootSchema.model_validate(self._get_latest_entry(collection_path, link)[link])
        cleared_schema = RootSchema()

        # Keep some sections
        doc.overview.subject = []
        doc.overview.tags = []
        cleared_schema.overview = doc.overview
        cleared_schema.contact = doc.contact

        self.pipeline.schema = cleared_schema
        pp(self.pipeline.schema)

        self.pipeline.run(link)

        schema = self.pipeline.schema.model_dump()
        self.db.save(collection_path, schema, set_index=True)

    def _hard_run(self, link:str) -> None:
        pass

if __name__ == "__main__":
    r = Refresher()
    """
    print(r._get_latest_entry("programs-display", "https:\\\\precollegesummer.rutgers.edu\\scholars"))
    print(r._get_latest_entry("programs-display", "https:\\\\opportunitynetwork.org\\apply\\"))
    print(r._get_latest_entry("programs-display", "https:\\\\sumac.spcs.stanford.edu\\sumac-online-program"))
    """
    r._soft_run("https:\\\\aimi.stanford.edu\\education\\summer-research-internship")