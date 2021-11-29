set -e

do_lint()
{
  # pick ones that match target generator & syntax
 dargslint
 interrogate
}

do_docs()
{
  # pick one or two!
  pdoc
  portray
  pycco
  pydoctor
  mkdocs build

  cd sphinx_docs
  ./start.sh
  cd ..
}

#fill in boiler plate
# HUGE, 1/4 GB!!!
# pip install docly
docly-gen pydoc_fork

interrogate pydoc_fork
rst_support.py:1

# spell checks variable names, can't target docstrings?
# scspell build.py --report-only

# copy `__init__` docstring to README.md
#https://github.com/datagazing/gleandoc/tree/main/gleandoc

# google style checker... seems to not be picky?
python -m check_docstring pydoc_fork

# run those tests
pytest pydoc_fork --doctest-modules

# this will remove docstrings! Maybe if they are so bad a reset is needed?
# strip-docs .

# can't figure out how to enable just doc related
pylint pydoc_fork --disable=all --enable=basic,spelling
# not sure these are high value rules, so I disabled them
pydocstyle pydoc_fork --ignore=D400,D404,D415,D212,D200,D205,D403,D401,D203,D213,D202,D407,D413,D209,D406
rm  -rf docs/docs_pdoc3
pdoc pydoc_fork --html -o docs/docs_pdoc3