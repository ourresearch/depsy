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
            "fractional_sort_score": 282.1837,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "4ch",
                "summary": "Python wrapper for the 4chan JSON API.",
                "use": 0.0,
                "use_percentile": 20.0
            },
            "percent": 70.37,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 19,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 146.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "chrw",
                "summary": "Python wrapper for the chr url shortener API",
                "use": 0.0,
                "use_percentile": 22.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 3,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 239.0,
            "package": {
                "citations_count": 9,
                "language": "python",
                "name": "chr",
                "summary": "Python based URL shortening service",
                "use": 1.0,
                "use_percentile": 64.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 73,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 220.0,
            "package": {
                "citations_count": 145,
                "language": "python",
                "name": "corrections",
                "summary": "A nifty project.",
                "use": 0.0,
                "use_percentile": 38.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 13,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 40100.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "4ch",
                "summary": "Python wrapper for the 4chan JSON API.",
                "use": 0.0,
                "use_percentile": 20.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 1.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "ebooks",
                "summary": "A nifty project.",
                "use": 0.0,
                "use_percentile": 11.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 13,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 100.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "fah",
                "summary": "Flask Against Humanity (copyright infringement pending).",
                "use": 1.0,
                "use_percentile": 70.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "github_owner"
        },
        {
            "fractional_sort_score": 0.92105,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "fah",
                "summary": "Flask Against Humanity (copyright infringement pending).",
                "use": 1.0,
                "use_percentile": 70.0
            },
            "percent": 92.105,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 35,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 376.47360000000003,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "Flask-Themes2",
                "summary": "Provides infrastructure for theming Flask applications                     (and supports Flask>=0.6!...",
                "use": 83.5,
                "use_percentile": 95.0
            },
            "percent": 36.765,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 25,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 102400.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "Flask-Themes2",
                "summary": "Provides infrastructure for theming Flask applications                     (and supports Flask>=0.6!...",
                "use": 83.5,
                "use_percentile": 95.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "github_owner"
        },
        {
            "fractional_sort_score": 210.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "mattdaemon",
                "summary": "Easily daemonize your python projects",
                "use": 3.0,
                "use_percentile": 78.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 11,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 417.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "pysqlw",
                "summary": "Python wrapper to make interacting with SQL databases easy",
                "use": 1.0,
                "use_percentile": 67.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 33,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 136.66523999999998,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "Quokka-Themes",
                "summary": "Provides infrastructure for theming Quokka applications",
                "use": 111.8,
                "use_percentile": 96.0
            },
            "percent": 22.892,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 19,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 191.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "rcmd",
                "summary": "Like Python's cmd module, but uses regex based handlers instead!",
                "use": 0.0,
                "use_percentile": 62.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 9,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 165.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "spiffing",
                "summary": "The gentleman's CSS pre-processor, to convert correct English CSS to American English CSS (and the r...",
                "use": 0.0,
                "use_percentile": 23.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 4,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 1.0,
            "package": {
                "citations_count": 1,
                "language": "python",
                "name": "strawberries",
                "summary": "Strawberries is an IRC bot, and also the plural of the word 'strawberry'.",
                "use": 0.0,
                "use_percentile": 1.0
            },
            "percent": 100.0,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": 5,
            "role": "github_contributor"
        },
        {
            "fractional_sort_score": 23900.0,
            "package": {
                "citations_count": 9,
                "language": "python",
                "name": "chr",
                "summary": "Python based URL shortening service",
                "use": 1.0,
                "use_percentile": 64.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 14600.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "chrw",
                "summary": "Python wrapper for the chr url shortener API",
                "use": 0.0,
                "use_percentile": 22.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 22000.0,
            "package": {
                "citations_count": 145,
                "language": "python",
                "name": "corrections",
                "summary": "A nifty project.",
                "use": 0.0,
                "use_percentile": 38.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 100.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "ebooks",
                "summary": "A nifty project.",
                "use": 0.0,
                "use_percentile": 11.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 100.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "fah",
                "summary": "Flask Against Humanity (copyright infringement pending).",
                "use": 1.0,
                "use_percentile": 70.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 102400.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "Flask-Themes2",
                "summary": "Provides infrastructure for theming Flask applications                     (and supports Flask>=0.6!...",
                "use": 83.5,
                "use_percentile": 95.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 21000.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "mattdaemon",
                "summary": "Easily daemonize your python projects",
                "use": 3.0,
                "use_percentile": 78.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 41700.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "pysqlw",
                "summary": "Python wrapper to make interacting with SQL databases easy",
                "use": 1.0,
                "use_percentile": 67.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        },
        {
            "fractional_sort_score": 19100.0,
            "package": {
                "citations_count": 0,
                "language": "python",
                "name": "rcmd",
                "summary": "Like Python's cmd module, but uses regex based handlers instead!",
                "use": 0.0,
                "use_percentile": 62.0
            },
            "percent": null,
            "person": {
                "bucket": {},
                "email": "chris@gibsonsec.org",
                "github_login": "sysr-q",
                "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
                "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
                "id": 37806,
                "is_academic": false,
                "name": "Chris Carter",
                "other_names": null,
                "parsed_name": {
                    "first": "Chris",
                    "last": "Carter",
                    "middle": "",
                    "nickname": "",
                    "suffix": "",
                    "title": ""
                },
                "sort_score": 389886.24359,
                "type": null
            },
            "quantity": null,
            "role": "author"
        }
    ],
    "email": "chris@gibsonsec.org",
    "github_login": "sysr-q",
    "icon": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=160&d=mm",
    "icon_small": "http://www.gravatar.com/avatar/670f175fdda8341082c9a7d9f8ef3a4c.jpg?s=30&d=mm",
    "id": 37806,
    "is_academic": false,
    "name": "Chris Carter",
    "other_names": null,
    "parsed_name": {
        "first": "Chris",
        "last": "Carter",
        "middle": "",
        "nickname": "",
        "suffix": "",
        "title": ""
    },
    "sort_score": 389886.24359,
    "type": null
}

"""