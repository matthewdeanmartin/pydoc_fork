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

