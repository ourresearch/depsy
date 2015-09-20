create table dep_nodes_ncol_cran as
(
select jsonb_array_elements_text(named_deps) as package, 'github:'||id as used_by
    from github_repo 
    where named_deps is not NULL 
    and language = 'r'
    and login != 'cran'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='cran' and github_owner is not null)
union    
select project_name as package, jsonb_array_elements_text(host_reverse_deps) as used_by 
    from package where host_reverse_deps is not NULL 
    and host='cran' 
) 

create table dep_nodes_ncol_cran_reverse as
(
select 'github:'||id as used_by, jsonb_array_elements_text(named_deps) as package
    from github_repo 
    where named_deps is not NULL 
    and language = 'r'
    and login != 'cran'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='cran' and github_owner is not null)
union    
select jsonb_array_elements_text(host_reverse_deps) as used_by , project_name as package
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
select jsonb_array_elements_text(host_deps) as package, project_name as used_by 
    from package where host_deps is not NULL 
    and host='pypi' 
) 



create table dep_nodes_ncol_pypi_reverse as
(
select 'github:'||id as used_by, jsonb_array_elements_text(named_deps) as package
    from github_repo 
    where named_deps is not NULL 
    and language='python'
    and api_raw->>'fork' = 'false'
    and id not in
        (select github_owner||':'||github_repo_name from package where host='pypi' and github_owner is not null)
union    
select project_name as used_by, jsonb_array_elements_text(host_deps) as package
    from package where host_deps is not NULL 
    and host='pypi' 
) 



select * from dep_nodes_ncol_pypi limit 1000
