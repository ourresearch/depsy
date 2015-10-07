-- from http://stackoverflow.com/a/22106818  

create table package_tags as (
    select
        id as package_id,
        jsonb_array_elements_text(tags) as tag,
        jsonb_array_length(tags) as num_tags_in_package
    from package) 


create table cooccurring_tags_one_way as (
    select 
        a.tag as tag1, 
        b.tag as tag2, 
        count(*) as c
    from package_tags a, package_tags b 
    where a.tag < b.tag 
    and a.package_id = b.package_id
    group by a.tag, b.tag
)

create view cooccurring_tags as (
    select 
        tag1, 
        tag2, 
        c 
        from cooccurring_tags_one_way
    union
    select 
        tag2 as tag1, 
        tag1 as tag2, 
        c 
        from cooccurring_tags_one_way
)

