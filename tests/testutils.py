from _pytest.outcomes import Failed


def should_fail_with(num_assertion: int | None = None):
    def decorator(fct):
        def wrapper(*args, **kwargs):
            try:
                fct(*args, **kwargs)
                if num_assertion != 0:
                    assert False, f"Expected test {fct.__name__} to fail, but it unexpectedly passed"
            except Failed as e:
                first_line = str(e).split("\n")[0]
                assert (
                    str(num_assertion) in first_line
                ), f"Expected test case to fail with {num_assertion} Invariant assertion(s), but got {first_line}"

        return wrapper

    return decorator
