create table dep_nodes_ncol as
(
select jsonb_array_elements_text(named_deps) as package, 'github:'||id as used_by,  1.0 + ((api_raw->>'stargazers_count')::float / 10.0) as weight
    from github_repo 
    where named_deps is not NULL 
    and language='python'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='pypi' and github_owner is not null)
union    
select jsonb_array_elements_text(host_reverse_deps) as package, project_name as used_by,  1.0 as weight
    from package where host_reverse_deps is not NULL 
    and host='pypi' 
) 

select * from dep_nodes_ncol limit 1000