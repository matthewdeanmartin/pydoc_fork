echo sphinx-quickstart
echo "Now go edit conf.py, move files to correct folder, etc."
# sphinx-apidoc -f -o docs pydoc_fork
sphinx-apidoc -o . ../pydoc_fork
sphinx-build -M html . _build
