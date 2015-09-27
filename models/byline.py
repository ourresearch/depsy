import re
from collections import defaultdict

from nameparser import HumanName
from validate_email import validate_email


class Byline:
    def __init__(self, raw_byline):
        self.raw_byline = raw_byline

    def _clean_byline(self):
        clean_byline = self.raw_byline

        halt_patterns = [" port", " adapted ", " comply "]
        for pattern in halt_patterns:
            if pattern in clean_byline:
                # print "has a halt pattern, so skipping this byline"
                return None

        # do these before the remove_pattern matching
        clean_byline = clean_byline.replace("<U+000a>", " ")
        clean_byline = clean_byline.replace("\n", " ")

        remove_patterns = [
            "\(.*?\)",   # here so can get before comma split
            "with.*$",
            "based on.*$",
            "assistance.*$",
            "derived from.*$",
            "uses.*$",
            "as represented by.*$",
            "contributions.*$",
            "under.*$",
            "and others.*$",
            "and many others.*$",
            "and authors.*$",
            "assisted.*$"
        ]
        for pattern in remove_patterns:
            clean_byline = re.sub(pattern, "", clean_byline, re.IGNORECASE)

        clean_byline = clean_byline.replace(" & ", ",")
        clean_byline = re.sub(" and ", ",", clean_byline, re.IGNORECASE)
        self.clean_byline = clean_byline
        return clean_byline  



    def author_email_pairs(self):
        clean_byline = self._clean_byline()
        if not clean_byline:
            return None

        responses = []
        for author_clause in clean_byline.split(","):
            author_name = None
            author_email = None

            clause_replace_patterns = [
                "\(.*?\)",   # here so can get before comma split            
                "\[.*?\]",
                "\[.*?$"
                ]
            for pattern in clause_replace_patterns:
                author_clause = re.sub(pattern, "", author_clause, re.IGNORECASE)

            if not author_clause or (len(author_clause) < 6):
                return None

            if "<" in author_clause:
                (author_name, author_email) = author_clause.split("<", 1)
                author_email = re.sub("(>.*)", "", author_email)
                if not validate_email(author_email):
                    author_email = None
            else:
                author_name = author_clause

            if author_name:
                author_name = author_name.strip("\t .'(")
                author_name = author_name.strip('"')

            if author_name or author_email:
                responses.append({"name":author_name, "email":author_email})

        return responses
        
