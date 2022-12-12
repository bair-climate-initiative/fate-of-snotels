# Fate of Snotels
This library provides a set of utilities and analysis code for the Fate Of Snotels™ project.


## Installation and Quickstart

```bash
# Clone the repo -- request from colorado.j.reed _at_ gmail.com if you do not have permission
git clone https://github.com/bair-climate-initiative/fate-of-snotels
cd fate-of-snotels

# Create and activate a virtual environment (or use an existing one)
conda create -n "fos"
conda activate fos

# Install fos (in editable mode, so that you can update the code and have the updates propagated)
pip install -e .

TODO add commands
```

## Development
The following section provides startup instructions for further developing MR Analyzer.

### Structure

```
TODO describe data and code structure
```

### Development Setup

```
# enable pre-commit hooks
pre-commit install

# Note that to keep the code tidy and avoid oh-so-common python mistakes, we use precommit hooks. The pre-commit hooks will be installed using the above pip development install command. To run the pre-commit hooks, run the following command (they will also be run automatically when you commit code):
```bash
pre-commit run  --all-files
```

### Testing
All tests can be run through:
```bash
# run pytest after installing the dev libraries (see above)
pytest

# run pytest with html coverage output
pytest --cov=fos --cov-report=html
# open the html coverage report at `htmlcov/index.html`
```

### FAQ

* Do I have to follow the structure of this project or can I just make a ipynb / script for my analysis?
> Do whatever makes your life easiest! You can easily import the utils from the fos package as 
```python
from fos import utils
```

* How do I add a new dependency?
> Add it to [setup.cfg](setup.cfg) under `install_requires`. Use `pip freeze` or `conda list` to figure out the version.

