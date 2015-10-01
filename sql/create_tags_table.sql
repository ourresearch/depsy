drop table tags;

create table tags as
select jsonb_array_elements_text(tags)::text as unique_tag, 
	count(jsonb_array_elements_text(tags)::text) as count,
	host as namespace
 	from package 
 	group by unique_tag, host
 	order by count desc;
 	
alter table tags add column id text;
update tags set id=(namespace||':'||unique_tag);

CREATE INDEX tags_unique_tag_idx 
	ON tags (unique_tag);

select * from tags order by count desc;
