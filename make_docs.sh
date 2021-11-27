do_lint()
{
 dargslint
}

do_docs()
{
  pdoc
  portray
  pycco
  pydoctor
  mkdocs build

  cd sphinx_docs
  ./start.sh
  cd ..
}

