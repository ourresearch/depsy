heroku run --size=performance-l python update.py CranPackage.set_impact --no-rq --limit=100000
heroku run --size=performance-l python update.py PypiPackage.set_impact --no-rq --limit=100000

heroku run --size=performance-l python update.py Person.set_impact --no-rq --limit=1000000 --chunk=100

heroku run python update.py CranPackage.set_impact_rank --no-rq --limit=100000 
heroku run python update.py PypiPackage.set_impact_rank --no-rq --limit=100000 
