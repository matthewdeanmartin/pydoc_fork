# pydoc_fork
A fork of pydoc to fix some problems with it.

## Motivation
Pydoc appears to have been pulled in five directions without the input of a product manager.
It is a mishmash of intentions:

- a customized web server/web application
- a plaintext in-console manpage-like documentation browser
- a documentation search
- html templating
- inspection/reflection code

I think it should be a html documentation generator alone. There is another tool, pdoc that
appears to be written from scratch. This will keep the intention of the html generator.

## Pydoc Bugs

- Can't specify module plus submodules (limitations to `.//` option)
- Can't do relative paths (404s if you move folders)
- Can't specify host url for builtins (404s)
- Can't specify output folder (paths break if you copy files)

## TODO:
 - rip out web server and browser. DONE
 - rip out the plain text (console) generator. DONE
 - rip out interactive text (console) code. DONE
 - rip out most arg parser logic. DONE
 - Make path relative for file links
 - Allow specifiying output folders
 - Add more documentaion scenarios
 - Pull in some unit tests


## Source
Forked from python 3.10. 
https://github.com/python/cpython/blob/3.10/Lib/pydoc.py

That code is governed by this license
https://github.com/python/cpython/blob/main/LICENSE

Not sure I can pull in the tests
https://github.com/python/cpython/blob/3.10/Lib/test/test_pydoc.py
