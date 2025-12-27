
from src.main import Main
from src.features.databases import FirebaseClient

class Refresher:
    def __init__(self) -> None:
        self.pipeline = Main()
        self.db = FirebaseClient.get_instance()
        self.all_data = {}

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
        self.all_data[collection_path] = self.db.get_all_data(collection_path)

    def _get_latest_entry(self, collection_path:str, link:str) -> dict:
        # If the database hasn't been read yet, do so
        if not self.all_data:
            self.__get_all_data(collection_path)

        # Documents end with a "-" followed by a number representing the version of the doc
        # Find all data with the same link as the link provided and add it to a list
        documents_with_link: list[dict] = []
        for doc in self.all_data[collection_path]:
            if link == '-'.join(doc.split('-')[:-1]):
                documents_with_link.append({doc: self.all_data[collection_path][doc]})

        docs: dict[int, dict] = {}
        for doc in documents_with_link:
            id: str = list(doc.keys())[0]
            ver: int = int(id.split("-")[-1])
            docs[ver] = doc
        max_ver: int = max(docs.keys())
        return docs[max_ver]

    def _soft_run(self, link:str) -> None:
        pass

    def _hard_run(self, link:str) -> None:
        pass

if __name__ == "__main__":
    r = Refresher()
    print(r._get_latest_entry("programs-display", "https:\\\\precollegesummer.rutgers.edu\\scholars"))
    print(r._get_latest_entry("programs-display", "https:\\\\opportunitynetwork.org\\apply\\"))
    print(r._get_latest_entry("programs-display", "https:\\\\sumac.spcs.stanford.edu\\sumac-online-program"))