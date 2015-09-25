import re
from collections import defaultdict

from nameparser import HumanName
from validate_email import validate_email


class Byline:
    def __init__(self, raw_byline):
        self.raw_byline = raw_byline

    def _clean_byline(self):
        clean_byline = self.raw_byline

        halt_patterns = [" port ", " adapted ", " comply "]
        for pattern in halt_patterns:
            if pattern in clean_byline:
                print "has a halt pattern, so skipping this byline"
                return None

        remove_patterns = [
            "\(.*?\)",
            "\[.*?\]",
            "with.*$",
            "assistance.*$",
            "contributions.*$",
            "under.*$",
            "and others.*$",
            "and many others.*$",
            "and authors.*$",
            "assisted.*$"
        ]
        for pattern in remove_patterns:
            clean_byline = re.sub(pattern, "", clean_byline)
            # print pattern, all_authors

        clean_byline = clean_byline.replace("<U+000a>", " ")
        clean_byline = clean_byline.replace("\n", " ")
        clean_byline = clean_byline.replace(" & ", ",")
        clean_byline = clean_byline.replace(" and ", ",")
        clean_byline.strip(" .")
        self.clean_byline = clean_byline
        return clean_byline  



    def author_email_pairs(self):
        clean_byline = self._clean_byline()
        if not clean_byline:
            return None

        responses = []
        for one_author in clean_byline.split(","):
            author_email = None
            if "<" in one_author:
                (author_name, author_email) = one_author.split("<", 1)
                author_email = re.sub("(>.*)", "", author_email)
                if not validate_email(author_email):
                    author_email = None
            else:
                author_name = one_author

            if author_name:
                author_name = author_name.strip()

            responses.append({"name":author_name, "email":author_email})

        return responses
        
