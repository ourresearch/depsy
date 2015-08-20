from models.pypi_repo import save_pypi_repo

from app import db
from pathlib import Path
import json


data_dir = Path(__file__, "../data").resolve()
pypi_projects_path = Path(data_dir, "pypi_projects.json")



def main():
    """
    Moves all the pypi repo stuff from text file to the db

    For this to work, the pypi_repo table needs to be there. you
    can autocreate it by running the flask app, with the
    'from models.pypi_repo import PyPiRepo'
    import with the other ones in the middle of app.py
    """
    print "opening the data file..."
    with open(str(pypi_projects_path), "r") as f:
        projects = json.load(f)

    num_projects = len(projects)
    index = 0
    for project in projects:
        print "saving '{name}' ({index} of {num_projects})".format(
            name=project["info"]["name"],
            index=index,
            num_projects=num_projects
        )
        save_pypi_repo(project)
        index += 1

    print "there are {} projects".format(len(projects))

if __name__ == '__main__':
    main()
    print "i ran"

