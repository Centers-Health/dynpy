from calculator import Calculator


def test_should_add_two_numbers():
    c = Calculator()
    assert c.add(1, 1) == 2
