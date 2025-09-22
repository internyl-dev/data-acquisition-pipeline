
class History:
    """
    A container object that represents the history of the 
    running program. The purpose of this object is to store 
    items and check whether or not the item has been stored. 
    """
    def __init__(self) -> None:
        self.items = {}

    def add(self, item) -> None:
        """
        Adds the item into storage for the purpose of checking
        later.

        Args:
            item (any): The item to add into storage.
        """
        self.items.add(item)
    
    def add_all(self, *args) -> None:
        """
        Like the `add` method but adds multiple items into
        storage at once.

        Args:
            *items (any): The items to add into storage.
        """
        self.items.update(args)

    def is_in(self, item) -> bool:
        """
        Checks whether or not an item is in storage. The
        item has to be an object reference and will check
        whether or not it is in storage based on the __eq__
        method.
        \n
        **TLDR**; If an equivalent item is in storage, it'll
        return `True`.

        Args:
            item (any): The item to check.
        """
        return (item in self.items)