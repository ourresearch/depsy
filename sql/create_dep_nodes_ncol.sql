create table dep_nodes_ncol_cran as
(
select jsonb_array_elements_text(named_deps) as package, 'github:'||id as used_by
    from github_repo 
    where named_deps is not NULL 
    and language='r'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='cran' and github_owner is not null)
union    
select jsonb_array_elements_text(host_reverse_deps) as package, project_name as used_by
    from package where host_reverse_deps is not NULL 
    and host='cran' 
) 


create table dep_nodes_ncol_pypi as
(
select jsonb_array_elements_text(named_deps) as package, 'github:'||id as used_by
    from github_repo 
    where named_deps is not NULL 
    and language='python'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='pypi' and github_owner is not null)
union    
select jsonb_array_elements_text(host_reverse_deps) as package, project_name as used_by
    from package where host_reverse_deps is not NULL 
    and host='pypi' 
) 


select * from dep_nodes_ncol_pypi limit 1000

{"reverse_depends": [], 
"reverse_imports": [], 
"all_reverse_deps": ["htmlTable"], 
"reverse_enhances": [], 
"reverse_suggests": ["htmlTable"]}