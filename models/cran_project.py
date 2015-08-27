from app import db
from sqlalchemy.dialects.postgresql import JSONB




class CranProject(db.Model):
    project_name = db.Column(db.Text, primary_key=True)
    owner_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)

    api_raw = db.Column(JSONB)
    reverse_deps = db.Column(JSONB)
    deps = db.Column(JSONB)

    zip_download_elapsed = db.Column(db.Float)
    zip_download_size = db.Column(db.Integer)
    zip_download_error = db.Column(db.Text)
























def test_cran_project():
    print "testing cran project!"