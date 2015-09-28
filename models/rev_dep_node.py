import re

class RevDepNode():
    def __init__(self, parent, name, pagerank):
        self.parent = parent
        self.name = name
        self.pagerank = pagerank
        self.children = []


    def __repr__(self):
        return "RevDepNode {} with {} children".format(
            self.name,
            len(self.children)
        )

    @property
    def display_pagerank(self):
        return round(self.pagerank * 1000000, 0)

    @property
    def is_rollup(self):
        return self.name.startswith("+")

    @property
    def is_package(self):
        return not self.name.startswith("github:")

    @property
    def display_name(self):
        if self.is_rollup:
            return re.compile(r'\+(\d+)').findall(self.name)[0] + " others"
        elif not self.is_package:
            return self.name.replace("github:", "")
        else:
            return self.name

    @property
    def sort_score(self):
        if self.is_rollup:
            return 0  # always sort to bottom
        else:
            return self.display_pagerank


    def add_children(self, edges):
        for edge in edges:
            if edge[1] == self.name:
                new_child_node = RevDepNode(
                    self.name,
                    edge[2],
                    edge[3]
                )
                self.children.append(new_child_node)


        for child in self.children:
            child.add_children(edges)

    def get_child(self, child_name):
        for child in self.children:
            if child.name == child_name:
                return child

        return None

    def to_dict(self):
        return {
            "parent": self.parent,
            "name": self.display_name,
            "pagerank": self.pagerank,
            "display_pagerank": self.display_pagerank,
            "is_rollup": self.is_rollup,
            "is_package": self.is_package,
            "children": [c.to_dict() for c in self.children],
            "sort_score": self.sort_score

        }


