# Fate of Snotels
This library provides a set of utilities and analysis code for the Fate Of Snotels™ project.

## TODOs
- [x] Create fos package
- [x] Add getting install instructions
- [x] Add end-to-end tests
- [x] Add getting started instructions for a new team member
- [x] Add caching for slow loading operations (with command line / api override)
- [x] Add example notebooks (see [nbs/cjr-dev.ipynb][nbs/cjr-dev.ipynb] for example)


## Installation and Quickstart

```bash
# If on a NERSC system
module load python

# Clone the repo -- request from colorado.j.reed _at_ gmail.com if you do not have permission
git clone https://github.com/bair-climate-initiative/fate-of-snotels
cd fate-of-snotels

# Create and activate a virtual environment (or use an existing one)
conda create -n "fos" python=3.9 ipython
conda activate fos

# Install fos (in editable mode, so that you can update the code and have the updates propagated)
pip install -e .
```

## Analysis

See the analysis notebooks at [nbs/cjr-dev.ipynb][nbs/cjr-dev.ipynb].

## Development
The following section provides startup instructions for further developing MR Analyzer.

### Code Structure

```
- README.md : this file ;-)
- setup.cfg : add new dependencies here
- pyproject.toml : can probably ignore this (sets up the build system)
nbs/ : notebooks, development and exploratory code
scripts/ : scripts for running and launching reproducbile analysis
fos/: the main package directory
    - dir.py: relevant directory locations -- avoid hardcoding directories in the code and put all values here.
    - util.py: common utilities, data loading, etc.
```

### Data Structure

On UCAR, this directory contains the "raw" data from the WRF simulations. 
```
- /glade/campaign/uwyo/wyom0112/postprocess/: Downscaled WRF simulations
|
|- {model}_{variant}_{experiment-id}_{bias correction flag}
|
|-- e.g. ukesm1-0-ll_r2i1p1f2_ssp370/postprocess/{domains} [e.g. d01: 45km domain, d02: 9km domain, d03: CA 3km, d04: WY 3km]
|---- e.g. d02/wspd10mean.daily.ukesm1-0-ll_ssp370_r2i1p1f2_d02_2090.nc: {variable}.{sampling}.{model}
```



### Development Setup

```
# enable pre-commit hooks
pre-commit install

# Note that to keep the code tidy and avoid oh-so-common python mistakes, we use precommit hooks. The pre-commit hooks will be installed using the above pip development install command. To run the pre-commit hooks, run the following command (they will also be run automatically when you commit code):
```bash
pre-commit run  --all-files
```
### Caching
Have an expensive function that you want to cache? Use the `cache` decorator from `fos.util`:
```python
from fos.util import memory

@memory.cache
def expensive_function():
    # do something expensive
    return result
```

Control the cache location with the `FOS_CACHE_DIR` environment variable. The default is `~/.fos_cachedir`.

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
> Do whatever makes your life easiest! For using version control with your notebooks, you can add them to the `nbs/` directory. You can easily import the utils from the fos package as 
```python
from fos import util
```

* How do I add a new dependency?
> Add it to [setup.cfg](setup.cfg) under `install_requires`. Use `pip freeze` or `conda list` to figure out the version.


### NERSC Tips
```
module load python
module load hdf
export HDF5_USE_FILE_LOCKING=FALSE
```
* On cori, you may need to set `export HDF5_USE_FILE_LOCKING=FALSE` if you recieve an hdf5 error.
