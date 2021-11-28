Building
--------
`pipenv install --dev --skip-lock
nb package`
Some dependencies are expected to be pipx installed globally on the machine, e.g. pylint


Testing
-------
Testing requires live modules.

Scenarios
- Pipx installed. Target in file system, installed packages or system.
- Pipenv installed
  - Target in file system
    - In vs not in /src/ folder
    - On some entirely different path
  - Target in virtual environment or system python
  - Target is system python
  - Target is self (pydoc_fork)
    - Mentioning because pydoc itself has code to handle documenting pydoc.


