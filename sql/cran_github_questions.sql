-- how many cran projects have any url at all?
select api_raw::jsonb->>'URL' from cran_project where api_raw::jsonb ? 'URL'


-- how many have a github-lookin' url?
select api_raw::jsonb->>'URL' from cran_project where api_raw::jsonb->>'URL' like '%github%';

