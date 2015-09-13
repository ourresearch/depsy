create table dep_nodes_ncol as
(
select 'github:'||id as source, jsonb_array_elements_text(named_deps) as depends_on, 1.0 + ((api_raw->>'stargazers_count')::float / 10.0) as weight
    from github_repo 
    where named_deps is not NULL 
    and language='python'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='pypi' and github_owner is not null)
union    
select 'pypi:'||project_name as source, jsonb_array_elements_text(host_reverse_deps) as depends_on, 1 as weight
    from package where host_reverse_deps is not NULL 
    and host='pypi' 
) 
