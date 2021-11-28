# Documentation workflows

Docs first
----------
Write a collection of markup files, refer to code as appropriate.

Code First
----------
Write documentation in comments, write stand-alone documents as appropriate.

Code First build
----------------
Before: 
```python
shit = None
"""String representation of hits"""
```
After, fix names, annotate, docstrings: 
```python
hits:Optional[str] = None
"""Player hit points"""
```

Fix identifier names. Good names should make documentation less important.

Add annotations. Tools can automatically add type annotations. Mypy checks if types are correct.


Build Script
------------
Steps:
- Annotate
- Validate annotations (mypy)
- Auto-comment (tools?)
- Lint comments
- Generate
- Publish/Host
  - If Markdown and Github, source repo is the host
  - If html, use Github pages or the like
  - If read-the-docs, then ....




