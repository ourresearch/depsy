create table tags as
select jsonb_array_elements_text(tags)::text as unique_tag, 
	count(jsonb_array_elements_text(tags)::text) as count
 	from package 
 	group by unique_tag
 	order by count desc
 	
alter table tags add column namespace text
update tags set namespace='pypi'

update tags set id=(namespace||':'||unique_tag)
select * from tags
