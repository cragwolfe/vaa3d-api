# content of test_sample.py
def func(x):
    return x + 1

def test_answer_correct():
	assert func(3) == 4

def test_answer():
    assert func(3) == 5