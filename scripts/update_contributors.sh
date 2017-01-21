
heroku run --size=performance-l python update.py Package.save_all_people  --limit=1000000
heroku run --size=performance-l python update.py Package.set_credit  --limit=1000000

echo "**** Now run the sql in set_person_is_organization.sql"