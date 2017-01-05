# run this with 
# heroku run --size=performance-l sh scripts/run_igraph.sh

echo "exporting CRAN dep nodes from db"
psql $DATABASE_URL --command="drop table dep_nodes_ncol_cran_reverse;
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
);"
psql $DATABASE_URL --command="\copy dep_nodes_ncol_cran_reverse to 'dep_nodes_ncol.txt' DELIMITER ' ';"
echo "running CRAN igraph data through igraph and storing stats in db"
python update.py CranPackage.set_igraph_data --limit=100000 --chunk=100 --no-rq

# echo "exporting PYPI dep nodes from db"
# psql $DATABASE_URL --command="\copy dep_nodes_ncol_pypi_reverse to 'dep_nodes_ncol.txt' DELIMITER ' ';"
# echo "running PYPI igraph data through igraph and storing stats in db"
# python update.py PypiPackage.set_igraph_data --limit=100000 --chunk=100 --no-rq

echo "done!  :)"