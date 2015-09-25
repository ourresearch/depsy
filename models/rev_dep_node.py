class RevDepNode():
    def __init__(self, parent, name, pagerank):
        self.parent = parent
        self.name = name
        self.pagerank = pagerank
        self.children = []


    @property
    def display_pagerank(self):
        return self.pagerank * 100000

    @property
    def is_rollup(self):
        return True

    @property
    def is_package(self):
        return True


    def get_child(self, child_name):
        for child in self.children:
            if child.name == child_name:
                return child

        return None

    def to_dict(self):
        return {
            "parent": self.parent,
            "name": self.name,
            "pagerank": self.pagerank,
            "display_pagerank": self.display_pagerank,
            "is_rollup": self.is_rollup,
            "is_package": self.is_package
        }
