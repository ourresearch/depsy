import re
import ast



def reqs_from_file(contents, file_type=None):
    if file_type is None:
        # we can auto-detect the file type prolly, but don't need to yet.
        pass

    if contents is None:
        return []

    if file_type == "requirements.txt":
        return parse_requirements_txt(contents)

    elif file_type == "setup.py":
        try:
            return parse_setup_py(contents)
        except SyntaxError:
            # we couldn't read the file.
            print "\n******  setup.py parse error!  ******\n"
            return []


def parse_requirements_txt(contents):
    # see here for spec used in parsing the file:
    # https://pip.readthedocs.org/en/1.1/requirements.html#the-requirements-file-format
    # it doesn't mention the '#' comment but found it often in examples.
    # not using this test str in  the function, just a handy place to keep it.
    test_str = """# my comment
file://blahblah
foo==10.2
baz>=3.6
foo.bar>=3.33
foo-bar==2.2
foo_bar==1.1
foo == 5.5
.for some reason there is a dot sometimes
--index-url blahblah
-e http://blah
  foo_with_space_in_front = 1.1"""

    reqs = re.findall(
        r'^(?!#|file|-|\.)\s*([\w\.-]+)',
        contents,
        re.MULTILINE | re.IGNORECASE
    )
    return sorted(reqs)


def _clean_setup_req(req):
    """
    get rid of cruft in setup.py req format params.

    there's some spec stuff here: https://pythonhosted.org/setuptools/setuptools.html#declaring-dependencies
    but also lots of trial-and-error.

    "Markdown==5.5",
    "Markdown>=5",
    "Foo.bar==5"
    "Foo_bar==5"
    "Foo-bar==5"
    "Foo[PDF]==5"
    "simplejson (>=3.3.1)"
    """
    try:
        return re.compile(r"^[\w\.-]+").findall(req)[0]
    except IndexError:
        return None



def regex_parse_setup_py(contents):
    # not using this yet, but it will get more stuff than ast approach.
    requirement_lists_regex = r'(install_requires|requires|tests_require)\s*=\s*(\[[^\]]+\])'
    requirement_dicts_regex = r'(extras_require)\s*=\s*(\[[^\]]+\])'


def parse_setup_py(contents):
    parsed = ast.parse(contents)
    ret = []
    # see ast docs: https://greentreesnakes.readthedocs.org/en/latest/index.html
    for node in ast.walk(parsed):
        try:
            if node.func.id == "setup":
                for keyword in node.keywords:
                    if keyword.arg=="install_requires":
                        print "found requirements in setup.py 'install_requires' arg"
                        for elt in keyword.value.elts:
                            ret.append(_clean_setup_req(elt.s))

                    if keyword.arg=="requires":
                        print "found requirements in setup.py 'requires' arg"
                        for elt in keyword.value.elts:
                            ret.append(_clean_setup_req(elt.s))

                    if keyword.arg == "extras_require":
                        print "found requirements in setup.py 'extras_require' arg"
                        for my_list in keyword.value.values:
                            for elt in my_list.elts:
                                ret.append(_clean_setup_req(elt.s))

        except AttributeError:
            continue

    return sorted(ret)


