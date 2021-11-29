set -e

do_tests()
{
  # run those tests
  pytest pydoc_fork --doctest-modules
}

do_lint()
{
  # pick ones that match target generator & syntax
  # dargslint
  interrogate pydoc_fork
  # can't figure out how to enable just doc related
  pylint pydoc_fork --disable=all --enable=basic,spelling
  # not sure these are high value rules, so I disabled them
  pydocstyle pydoc_fork --ignore=D400,D404,D415,D212,D200,D205,D403,D401,D203,D213,D202,D407,D413,D209,D406
}

do_docs()
{
  # pick one or two!
  rm  -rf docs/docs_pdoc3
  pdoc pydoc_fork --html -o docs/docs_pdoc3

  # broken here!
  # pycco

  # pydoctor, validates on indentation
  rm  -rf docs/docs_pydoctor
  pydoctor pydoc_fork/**/*.py --make-html --html-output docs/docs_pydoctor

  # driven by yaml config
  mkdocs build

  rm  -rf docs/docs_sphinx
  cd sphinx_docs
  ./start.sh
  cd ..

  rm  -rf docs/docs_pydoc_fork
  python -m pydoc_fork pydoc_fork --output docs/docs_pydoc_fork

  rm  -rf docs/docs_portray
  portray as_html --directory . --output_dir docs/docs_portray --modules pydoc_fork

}

#fill in boiler plate
# HUGE, 1/4 GB!!!
# pip install docly
# and doesn't work on windows and abandoned project
# docly-gen pydoc_fork



# spell checks variable names, can't target docstrings?
# scspell build.py --report-only

# copy `__init__` docstring to README.md
#https://github.com/datagazing/gleandoc/tree/main/gleandoc

# google style checker... seems to not be picky?
# python -m check_docstring pydoc_fork




# this will remove docstrings! Maybe if they are so bad a reset is needed?
# strip-docs .


do_tests
do_lint
do_docs