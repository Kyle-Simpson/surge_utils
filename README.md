# Surge Utils
Python and R utility functions to make life a little simpler ;)

## Codebase Outline
```
surge_utils/
  +-- py_utils
  |   +-- tests
  |       +-- test_data_man_calc.py
  |       +-- test_gbd_cause_helpers.py
  |       +-- test_gbd_loc_helpers.py
  |       +-- test_qsub_helpers.py
  |       +-- test_root_path.py
  |   +-- utils.py
  +-- r_utils
  |   +-- tests
  |       +-- run_all_tests.R
  |       +-- test_data_man_calc.R
  |       +-- test_gbd_cause_helpers.R
  |       +-- test_gbd_loc_helpers.R
  |       +-- test_qsub_helpers.R
  |       +-- test_root_path.R
  |   +-- utils.R
  +-- README.md
  +-- refs.yaml
```

---  

## Sourcing Scripts
### Python
To source utils.py, import `surge_utils.py_utils.utils` at the top of your file with the rest of your import statements. And be sure to have added the `surge_utils` repo to the `PATH` variable in your .bash_profile or .bash_rc.  

### R
To source utils.R, use the `source()` function and specify the path to the `surge_utils` repo.

---

## Running Tests
### Python Tests
1. Open an SSH terminal, qlogin, and source a conda env
2. Navigate to the root of `surge_utils`
3. Type `python -m unittest discover py_utils/tests/ -v`

### R Tests
1. Open an SSH terminal, qlogin, and source a conda env
2. Navigate to the root of `surge_utils`
3. Type `Rscript r_utils/tests/run_all_tests.R`