-- counts unique libs listed in the pypi_dependencies column
select jsonb_array_elements(pypi_dependencies), count(jsonb_array_elements(pypi_dependencies)) 
	from github_repo where pypi_dependencies is not NULL 
	group by jsonb_array_elements(pypi_dependencies);



