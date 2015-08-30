import rq_worker
from models.pypi_project import PypiPackageNames
from models.pypi_project import PythonStandardLibs


if __name__ == '__main__':

    PypiPackageNames.load_cache()
    PythonStandardLibs.load_cache()
    rq_worker.start_worker("github_zip")
