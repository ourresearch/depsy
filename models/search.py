from sqlalchemy import sql


from app import db

def autocomplete(search_str):

    command = """(select project_name, sort_score, api_raw->'info'->>'summary' as summary, 'pypi_project' as type, 1 as first_sort
    from package
    where host='pypi'
    and project_name ilike '{str}%'
    order by sort_score desc
    limit 5)
    union
    (select project_name, sort_score, api_raw->>'Title' as summary, 'cran_project' as type, 2 as first_sort
    from package
    where host='cran'
    and project_name ilike '{str}%'
    order by sort_score desc
    limit 5)
    union
    (select name, sort_score, github_about->>'company' as summary, 'person' as type, 3 as first_sort
    from person
    where name ilike '%{str}%'
    order by sort_score desc
    limit 5)
    union
    (select name, "count" as sort_score, null as summary, 'tag' as type, 4 as first_sort
    from tags
    where name ilike '%{str}%'
    order by sort_score desc
    limit 5)
    order by first_sort, sort_score desc""".format(str=search_str)

    res = db.session.connection().execute(sql.text(command))
    rows = res.fetchall()
    ret = []
    prev_type = "there is no current type"
    for row in rows:
        ret.append({
            "name": row[0],
            "sort_score": row[1],
            "summary": row[2],
            "type": row[3],
            "is_first": prev_type != row[3]
        })
        prev_type = row[3]


    return ret

   










