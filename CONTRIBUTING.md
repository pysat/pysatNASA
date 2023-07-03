Contributing
============

Bug reports, feature suggestions, and other contributions are greatly
appreciated!  pysat is a community-driven project and welcomes both feedback and
contributions.

Come join us on Slack! An invitation to the pysat workspace is available
in the 'About' section of the
[pysat GitHub Repository.](https://github.com/pysat/pysat) Development meetings
are generally held fortnightly.

Short version
-------------

* Submit bug reports and feature requests at [GitHub](https://github.com/pysat/pysatNASA/issues)

* Make pull requests to the ``develop`` branch

Bug reports
-----------

When [reporting a bug](https://github.com/pysat/pysatNASA/issues) please
include:

* Your operating system name and version

* Any details about your local setup that might be helpful in troubleshooting

* Detailed steps to reproduce the bug

Feature requests and feedback
-----------------------------

The best way to send feedback is to file an issue at
[GitHub](https://github.com/pysat/pysatNASA/issues).

If you are proposing a feature:

* Explain in detail how it would work.

* Keep the scope as narrow as possible, to make it easier to implement.

* Remember that this is a volunteer-driven project, and that code contributions
  are welcome :)

Development
-----------

To set up `pysatNASA` for local development:

1. [Fork pysatNASA on GitHub](https://github.com/pysat/pysatNASA/fork).

2. Clone your fork locally:

  ```
    git clone git@github.com:your_name_here/pysatNASA.git
  ```

3. Create a branch for local development:

  ```
    git checkout -b name-of-your-bugfix-or-feature
  ```

   Now you can make your changes locally.

   Tests for new instruments are performed automatically.  See discussion
   [here](https://pysat.readthedocs.io/en/main/new_instrument.html#testing-support)
   for more information on triggering these standard tests.

   Tests for custom functions should be added to the appropriately named file
   in ``pysatNASA/tests``.  For example, custom functions for the OMNI HRO data
   are tested in ``pysatNASA/tests/test_omni_hro.py``.  If no test file exists,
   then you should create one.  This testing uses pytest, which will run tests
   on any python file in the test directory that starts with ``test``.  Classes
   must begin with ``Test``, and methods must begin with ``test`` as well.


4. When you're done making changes, run all the checks to ensure that nothing
  is broken on your local system:

  ```
  pytest pysatNASA
  ```

5. You should also check for flake8 style compliance:

  ```
  flake8 . --count --select=D,E,F,H,W --show-source --statistics
  ```

  Note that pysat uses the `flake-docstrings` and `hacking` packages to ensure
  standards in docstring formatting.


6. Update/add documentation (in ``docs``), if relevant

7. Add your name to the .zenodo.json file as an author

8. Commit your changes:
  ```
  git add .
  git commit -m "AAA: Brief description of your changes"
  ```
  Where AAA is a standard shorthand for the type of change (eg, BUG or DOC).
  `pysat` follows the [numpy development workflow](https://numpy.org/doc/stable/dev/development_workflow.html),
  see the discussion there for a full list of this shorthand notation.  

9. Once you are happy with the local changes, push to Github:
  ```
  git push origin name-of-your-bugfix-or-feature
  ```
  Note that each push will trigger the Continuous Integration workflow.

10. Submit a pull request through the GitHub website. Pull requests should be
   made to the ``develop`` branch.  Note that automated tests will be run on
   github actions, but these must be initialized by a member of the pysat team.

Pull Request Guidelines
-----------------------

If you need some code review or feedback while you're developing the code, just
make a pull request. Pull requests should be made to the ``develop`` branch.

For merging, you should:

1. Include an example for use
2. Add a note to ``CHANGELOG.md`` about the changes
3. Update the author list in ``zenodo.json`` if applicable
4. Ensure that all checks passed (current checks include Github Actions and Coveralls)

If you don't have all the necessary Python versions available locally or
have trouble building all the testing environments, you can rely on
GitHub Actions to run the tests for each change you add in the pull
request. Because testing here will delay tests by other developers,
please ensure that the code passes all tests on your local system first.


Project Style Guidelines
------------------------

In general, pysat follows PEP8 and numpydoc guidelines.  Pytest runs the unit
and integration tests, flake8 checks for style, and sphinx-build performs
documentation tests.  However, there are certain additional style elements that
have been adopted to ensure the project maintains a consistent coding style.
These include:

* Line breaks should occur before a binary operator (ignoring flake8 W503)
* Combine long strings using `join`
* Preferably break long lines on open parentheses rather than using `\`
* Use no more than 80 characters per line
* Avoid using Instrument class key attribute names as unrelated variable names:
  `platform`, `name`, `tag`, and `inst_id`
* The pysat logger is imported into each sub-module and provides status updates
  at the info and warning levels (as appropriate)
* Several dependent packages have common nicknames, including:
  * `import datetime as dt`
  * `import numpy as np`
  * `import pandas as pds`
  * `import xarray as xr`
* When incrementing a timestamp, use `dt.timedelta` instead of `pds.DateOffset`
  when possible to reduce program runtime
* All classes should have `__repr__` and `__str__` functions
* Docstrings use `Note` instead of `Notes`
* Try to avoid creating a try/except statement where except passes
* Use setup and teardown in test classes
* Use pytest parametrize in test classes when appropriate
* Provide testing class methods with informative failure statements and
  descriptive, one-line docstrings
* Block and inline comments should use proper English grammar and punctuation
  with the exception of single sentences in a block, which may then omit the
  final period
* When casting is necessary, use `np.int64` and `np.float64` to ensure operating
  system agnosticism
