import json
def get_dummy_data(name):
    string = globals()[name]
    dict = json.loads(string)
    return dict


person = """
{
    "bucket": {},
    "contributions": [
        {
            "fractional_sort_score": 0.639,
            "package": {
                "as_search_result": {
                    "name": "miniupnpc",
                    "namespace": "pypi",
                    "sort_score": 355.0,
                    "summary": "miniupnp client",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chenhouwu",
                "github_repo_name": "miniupnpc",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [],
                "id": "pypi:miniupnpc",
                "pmc_mentions": [],
                "project_name": "miniupnpc",
                "setup_py_hash": "fbc5568dc7bd0aa079e3a9128b9bf5eb",
                "sort_score": 355.0,
                "source_url": "https://pypi.python.org/packages/source/m/miniupnpc/miniupnpc-1.9.tar.gz",
                "tags": []
            },
            "percent": 0.18,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": 1,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 615.0,
            "package": {
                "as_search_result": {
                    "name": "Warcat",
                    "namespace": "pypi",
                    "sort_score": 615.0,
                    "summary": "Tool and library for handling Web ARChive (WARC) files.",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "warcat",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [],
                "id": "pypi:Warcat",
                "pmc_mentions": [],
                "project_name": "Warcat",
                "setup_py_hash": "c54b6e4378679018b8e3e89e6e8b54bb",
                "sort_score": 615.0,
                "source_url": "https://pypi.python.org/packages/source/W/Warcat/Warcat-2.2.3.tar.gz",
                "tags": [
                    "System",
                    "Archiving"
                ]
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": 60,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 61500.0,
            "package": {
                "as_search_result": {
                    "name": "Warcat",
                    "namespace": "pypi",
                    "sort_score": 615.0,
                    "summary": "Tool and library for handling Web ARChive (WARC) files.",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "warcat",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [],
                "id": "pypi:Warcat",
                "pmc_mentions": [],
                "project_name": "Warcat",
                "setup_py_hash": "c54b6e4378679018b8e3e89e6e8b54bb",
                "sort_score": 615.0,
                "source_url": "https://pypi.python.org/packages/source/W/Warcat/Warcat-2.2.3.tar.gz",
                "tags": [
                    "System",
                    "Archiving"
                ]
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": null,
            "role": "github_owner"
        },
        {
            "fractional_sort_score": 5100.170880000001,
            "package": {
                "as_search_result": {
                    "name": "wpull",
                    "namespace": "pypi",
                    "sort_score": 5152.0,
                    "summary": "Wget-compatible web downloader and crawler.",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "wpull",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [
                    "chardet",
                    "dnspython3",
                    "html5lib",
                    "namedlist",
                    "psutil",
                    "SQLAlchemy",
                    "tornado",
                    "trollius"
                ],
                "id": "pypi:wpull",
                "pmc_mentions": [],
                "project_name": "wpull",
                "setup_py_hash": "e5070e6f5d81b2c60de16682fbf048f5",
                "sort_score": 5152.0,
                "source_url": "https://pypi.python.org/packages/source/w/wpull/wpull-1.2.1.tar.gz",
                "tags": [
                    "Internet",
                    "Archiving",
                    "WWW/HTTP",
                    "System"
                ]
            },
            "percent": 98.994,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": 1772,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 515200.0,
            "package": {
                "as_search_result": {
                    "name": "wpull",
                    "namespace": "pypi",
                    "sort_score": 5152.0,
                    "summary": "Wget-compatible web downloader and crawler.",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "wpull",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [
                    "chardet",
                    "dnspython3",
                    "html5lib",
                    "namedlist",
                    "psutil",
                    "SQLAlchemy",
                    "tornado",
                    "trollius"
                ],
                "id": "pypi:wpull",
                "pmc_mentions": [],
                "project_name": "wpull",
                "setup_py_hash": "e5070e6f5d81b2c60de16682fbf048f5",
                "sort_score": 5152.0,
                "source_url": "https://pypi.python.org/packages/source/w/wpull/wpull-1.2.1.tar.gz",
                "tags": [
                    "Internet",
                    "Archiving",
                    "WWW/HTTP",
                    "System"
                ]
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": null,
            "role": "github_owner"
        },
        {
            "fractional_sort_score": 17500.0,
            "package": {
                "as_search_result": {
                    "name": "Bytestag",
                    "namespace": "pypi",
                    "sort_score": 175.0,
                    "summary": "Wide Availability Peer-to-Peer File Sharing",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "bytestag",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [],
                "id": "pypi:Bytestag",
                "pmc_mentions": [],
                "project_name": "Bytestag",
                "setup_py_hash": "ba08467229c0cf29eb02e16a3506c0c2",
                "sort_score": 175.0,
                "source_url": "https://pypi.python.org/packages/source/B/Bytestag/Bytestag-0.2b1.tar.gz",
                "tags": [
                    "Internet"
                ]
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 9700.0,
            "package": {
                "as_search_result": {
                    "name": "PyWheel",
                    "namespace": "pypi",
                    "sort_score": 97.0,
                    "summary": "Python Middleware and Utilities",
                    "type": "PypiPackage"
                },
                "dependencies": null,
                "github_owner": "chfoo",
                "github_repo_name": "pywheel",
                "github_reverse_deps": null,
                "host": "pypi",
                "host_reverse_deps": [],
                "id": "pypi:PyWheel",
                "pmc_mentions": [],
                "project_name": "PyWheel",
                "setup_py_hash": "18d8df3aaea278718884cacdc0edda5c",
                "sort_score": 97.0,
                "source_url": "https://pypi.python.org/packages/source/P/PyWheel/PyWheel-0.1.tar.gz",
                "tags": [
                    "Internet",
                    "Utilities"
                ]
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris.foo@gmail.com",
                "github_login": "chfoo",
                "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
                "id": 65414,
                "is_academic": false,
                "name": "Christopher Foo",
                "other_names": null,
                "sort_score": 609615.80988,
                "type": null
            },
            "quantity": null,
            "role": "author"
        }
    ],
    "email": "chris.foo@gmail.com",
    "github_login": "chfoo",
    "icon": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=160&d=mm",
    "icon_small": "http://www.gravatar.com/avatar/122db15a75bb22a42a63dff77fca526f.jpg?s=30&d=mm",
    "id": 65414,
    "is_academic": false,
    "name": "Christopher Foo",
    "other_names": null,
    "sort_score": 609615.80988,
    "type": null
}



"""