import re
import math
from collections import defaultdict

class RevDepNode():
    def __init__(self, parent, name, pagerank, generation, stars=None, root_pagerank=None):
        self.parent = parent
        self.name = name
        self.pagerank = pagerank
        self.stars = stars
        self.root_pagerank = root_pagerank
        self.generation = generation

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
    def is_root(self):
        return self.generation == 0

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

        score = self.display_pagerank
        return score

        if self.stars is not None:
            if self.is_package:
                score += math.log10(self.stars + 1)
            else:  # github repo
                score += math.log10(self.stars + 1) * 100

        return score


    def _make_display_pagerank(self, pagerank):
        return round((math.log10(pagerank) + 5) * 20, 2)


    def set_children(self, rev_deps_lookup):
        my_children = rev_deps_lookup[self.name]
        for child in my_children:
            new_child_node = RevDepNode(
                parent=self.name,
                name=child[0],
                pagerank=child[1],
                generation=self.generation + 1,
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

    def to_generation_dict(self):
        ret = defaultdict(list)
        ret[self.generation].append(self.sort_score)
        if len(self.children) > 0:
            for child in self.children:
                print "i am child", self
                child_generation_dict = child.to_generation_dict()
                for generation_index, sort_scores in child_generation_dict.iteritems():
                    print "i am child dict item", generation_index, sort_scores
                    ret[generation_index] += sort_scores


        sorted_ret = {k: sorted(v, reverse=True) for k, v in ret.iteritems()}

        return sorted_ret


    def to_dict(self):
        ret = {
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
            "scale_factor": self.scale_factor,
            "generation": self.generation
        }

        if self.is_root:



            # needed for json serialization...
            ret["generation_dict"] = {}
            for generation_index, names in self.to_generation_dict().iteritems():
                ret["generation_dict"][generation_index] = list(names)

        return ret


