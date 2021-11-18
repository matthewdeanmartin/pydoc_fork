
### TODO:
- Separate "document source code at this path" from "document this imported type/module"
- Link built ins to main doc site (or give option to generate)
- Option to walk the module tree (to some specified depth)
  - https://stackoverflow.com/questions/48000761/list-submodules-of-a-python-module

### DONE
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

### MAYBE
Not sure I can pull in the tests
https://github.com/python/cpython/blob/3.10/Lib/test/test_pydoc.py
