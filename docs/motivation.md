## Motivation
Pydoc appears to have been pulled in five directions without the input of a product manager.
It is a mishmash of intentions:

- the help() function that spits out the doc string for a type
- a plaintext in-console manpage-like documentation browser
- basic documentation search
- html templating with no separation between logic and UI code
- a customized web server/web application
- inspection/reflection code to support it all

I think it should be a html documentation generator alone. There is another tool, pdoc that
appears to be written from scratch. This will keep the intention of the html generator.

## Pydoc Bugs

- Can't specify module plus submodules (limitations to `.//` option)
- Can't do relative paths (404s if you move folders)
- Can't specify host url for builtins (404s)
- Can't specify output folder (paths break if you copy files)
