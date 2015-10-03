
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