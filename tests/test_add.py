def test_add():
    from simulator.add import add

    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-1, -1) == -2
    assert add(1000000, 2000000) == 3000000
    assert add(1.5, 2.5) == 4.0
    assert add(-1.5, -2.5) == -4.0
    assert add(1.5, -2.5) == -1.0
