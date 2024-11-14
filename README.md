Invariant testing library

To run the sample tests, do `python3 invariant_runner/runner.py -s -vv --push sample_tests/` if you want to run with the Invariant runner. 

Else, do `pytest sample_tests -s -vv `. This will not use the Invariant runner but will still allow usage of the context manager.