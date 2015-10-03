
update person set is_organization=false;

update person set is_organization=true 
	where false	 -- just to comment out other things easily
	or name ilike '%organiz%'
	or name ilike '%foundat%'
	or name ilike '%technolo%'
	or name ilike '% labor%'
	or name ilike '% lab'
	or name ilike '% labs'
	or name ilike '%center%'
	or name ilike '%centre%'
	or name ilike '%consulting%'
	or name ilike '%institu%'
	or name ilike '%project%'
	or name ilike '%group%'
	or name ilike '%alliance%'
	or name ilike '%contributor%'
	or name ilike '%university%'
	or name ilike '%department%'
	or name ilike '% inc.'
	or name ilike '% inc'
	or name ilike '% llc'
	or name ilike '% incorp%'
	or name ilike '% limited%'
	or name like '% AG'
	or name ilike '% GmbH'
	or github_about->>'type' = 'Organization'
	or name in ('Tryton', 'OpenERP SA')