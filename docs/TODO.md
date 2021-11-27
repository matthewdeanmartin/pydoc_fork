## What pydoc does well
Pydoc excels at:
- giving you consistent documentation for everything
  - your code
  - standard lib code (except when it links to external)
  - 3rd package code

Real world documentation comes wildly different formats, missing, all over the place.


### TODO:
- Detect MD or RST &amp; format as such
- Separate "document source code at this path" from "document this imported type/module" eg:
  - pydoc_fork foo.bar
  - pydoc_fork c:/src/foo/bar.py
- copy source to target folder...using pycco!
- index page
- Surface all settings in cmd switchs or yaml config or pyproject.toml config

### DONE
- font tags in JINJA. DONE.Now HTML 4.5
- Option to walk the module tree (to some specified depth) DONE...?
  - https://stackoverflow.com/questions/48000761/list-submodules-of-a-python-module

- suppress typing/annotation cruft- DONE!
- font tags in .py code - DONE
- Just enough jinja to fix the HTML- DONE
  - heading, page, section are templates
- rip out web server and browser. DONE
- rip out the plain text (console) generator. DONE
- rip out interactive text (console) code. DONE
- rip out most arg parser logic. DONE
- Make path relative for source file links. DONE
- Allow specifiying output folders. DONE
- Allow just doing one folder module and subs. DONE
- Allow documenting more than `__all__`. DONE. "document internals" flag
- Add more documentaion scenarios
- Pull in some unit tests. DONE. Could hardly salvage any.
- Link built ins to main doc site (or give option to generate). DONE
- Double encoding (in unit tests flag HTML escape codes for "greater than"?). Fixed 1.
- Links to stdlib documentation work again
- Now attempts to doc `import foo` modules
- Now shows `from foo import bar` functions

### MAYBE
Not sure I can pull in the tests
https://github.com/python/cpython/blob/3.10/Lib/test/test_pydoc.py
