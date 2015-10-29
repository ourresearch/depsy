[![Research software impact](http://depsy.org/api/package/cran/rfUtilities/badge.svg)](http://depsy.org/package/r/rfUtilities)
*This documentation is embedded from Depsy's GitHub Readme, and is still in progress. Feel free to submit a pull request with updates and changes*








##Depsy is a better way to learn the impact of research software.##
It's being built at [Impactstory](https://impactstory.org/about) by Jason Priem and Heather Piwowar, and is funded by an [EAGER grant](http://blog.impactstory.org/impactstory-awarded-300k-nsf-grant/) from the National Science Foundation.

## What does Depsy include?

Depsy finds the impact of research software **packages** written in Python and R, and also impact of the **people** who write it.

[PyPI](http://pypi.python.org) for Python, and [CRAN](https://cran.r-project.org/web/packages/) for R.

R is a language for doing statistics.  As such, almost all of its packages are written by academics, for academics, to do reasearch--so we consider all R software on Depsy to be research software. We cover the *7057* R software packages available on [CRAN](https://cran.r-project.org/web/packages/), the main library repository for R.


Python is a more general purpose programming language.  We try to establish whether a given Python package is research software by searching its metadata (package name, description, tags) for researchy-words (see [code on GitHub](https://github.com/Impactstory/depsy/blob/870c85ee4598643f496bca76e5a7dff994e53837/models/academic.py)). We cover all *57,243* active Python packages on [PyPI](http://pypi.python.org), Python's main package repository; of those, we count *4166* as research software.

## Package impact

We currently calculate impact along three dimensions (and a fourth, coming later, that will capture social signals like GitHub watchers and Stack Overflow discussions). The overall impact score of a package is calculated as the average of these three: **downloads**, **software reuse**, and **literature mentions**. 

More information coming soon!  In the mean time, see our [full documentation page](https://github.com/Impactstory/depsy-research/blob/master/introducing_depsy.md) for details.


