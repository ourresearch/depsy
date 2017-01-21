python update.py Package.set_github_contributors  --id=pypi:scikit-learn
python update.py Package.save_all_people  --id=pypi:scikit-learn
python update.py Package.dedup_people  --id=pypi:scikit-learn
python update.py Package.set_credit  --id=pypi:scikit-learn

echo "**** Now run the sql in set_person_is_organization.sql"