heroku run --size=performance-l python update.py CranPackage.set_pagerank_score  --limit=100000
heroku run --size=performance-l python update.py PypiPackage.set_pagerank_score  --limit=100000

heroku run --size=performance-l python update.py CranPackage.set_subscore_percentiles  --limit=100000
heroku run --size=performance-l python update.py PypiPackage.set_subscore_percentiles  --limit=100000

heroku run --size=performance-l python update.py CranPackage.set_impact  --limit=100000
heroku run --size=performance-l python update.py PypiPackage.set_impact  --limit=100000

heroku run --size=performance-l python update.py CranPackage.set_impact_percentiles  --limit=100000
heroku run --size=performance-l python update.py PypiPackage.set_impact_percentiles  --limit=100000


heroku run --size=performance-l python update.py Person.set_scores  --limit=1000000 --chunk=100
heroku run --size=performance-l python update.py Person.set_subscore_percentiles  --limit=1000000 --chunk=100
heroku run --size=performance-l python update.py Person.set_impact  --limit=1000000 --chunk=100
heroku run --size=performance-l python update.py Person.set_impact_percentiles  --limit=1000000 --chunk=100
