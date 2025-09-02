
class History:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
    
    def add_all(self, *args):
        self.items.extend(args)

    def is_in(self, item):
        return (item in self.items)