import re
import math

class RevDepNode():
    def __init__(self, parent, name, pagerank, stars=None, root_pagerank=None):
        self.parent = parent
        self.name = name
        self.pagerank = pagerank
        self.stars = stars
        self.root_pagerank = root_pagerank
        self.is_root = False

        self.children = []


    def __repr__(self):
        return "RevDepNode {} with {} children".format(
            self.name,
            len(self.children)
        )

    @property
    def display_pagerank(self):
        return self._make_display_pagerank(self.pagerank)

    @property
    def root_goodness(self):
        return self._make_display_pagerank(self.root_pagerank)

    @property
    def is_rollup(self):
        return self.name.startswith("+")

    @property
    def is_package(self):
        return not self.name.startswith("github:")

    @property
    def percent_root_goodness(self):
        return self.sort_score / float(self.root_goodness)

    @property
    def display_name(self):
        if self.is_rollup:
            return re.compile(r'\+(\d+)').findall(self.name)[0] + " others"
        elif not self.is_package:
            return self.name.replace("github:", "")
        else:
            return self.name

    @property
    def scale_factor(self):
        return math.log(math.ceil(self.percent_root_goodness * 100) + 1)

    @property
    def sort_score(self):
        if self.is_rollup:
            return 0  # always sort to bottom
        elif self.is_package:
            return self.display_pagerank
        elif self.stars is not None:
            return self.stars / 5
        else:
            return self.display_pagerank

    def _make_display_pagerank(self, pagerank):
        return round(pagerank * 1000000, 0)


    def set_children(self, rev_deps_lookup):
        my_children = rev_deps_lookup[self.name]
        for child in my_children:
            new_child_node = RevDepNode(
                parent=self.name,
                name=child[0],
                pagerank=child[1],
                stars=child[2],
                root_pagerank=self.root_pagerank
            )
            if new_child_node.percent_root_goodness > 0.003:
                self.children.append(new_child_node)

        for child in self.children:
            child.set_children(rev_deps_lookup)


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
            "sort_score": self.sort_score,
            "percent_root_goodness": self.percent_root_goodness,
            "stars": self.stars,
            "is_root": self.is_root,
            "scale_factor": self.scale_factor

        }


