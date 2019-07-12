import pytest
def func(x):
    return x + 1


def test_answer():
    assert func(4) == 5


def test_check():
    assert (2 ** 2) == 4


class TestClass(object):
    def test_one(self):
        x = "this"
        assert 'h' in x


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0


def test_recursion_depth():
    with pytest.raises(RuntimeError) as excinfo:
        def f():
            f()
        f()
    assert "maximum recursion" in str(excinfo.value)


def myfunc():
    raise ValueError("Exception 123 raised")


def test_match():
    with pytest.raises(ValueError, match=r".* 123 .*"):
        myfunc()


@pytest.mark.xfail(raises=NameError)
def test_f():
    f()
