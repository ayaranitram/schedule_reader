"""
A simple counter class that can be used to count the number of iterations in a loop. It can be initialized with a starting value and a step size, and it has methods to increment, decrement, and get the current value of the counter. It also has a __call__ method that can be used to get the next value of the counter or the current value without incrementing it. The class also has __add__, __sub__, and __mult__ methods to perform arithmetic operations on the counter. The start_counter function is a helper function to create a new Counter instance with a given starting value.

developed by: Martin Araya
email: martinaraya@gmail.com
"""
__version__ = '0.7.0'
__release__ = 20260228

class Counter(object):
    """A simple counter that can be used to count the number of iterations in a loop."""
    def __init__(self, start: int = 0, step: int = 1):
        """Initialize the counter with a starting value and a step size."""
        if step == 0:
            raise ValueError(f"The `step` can't be zero!")
        self.start = start
        self.step = step
        self.current = start - step

    def next(self):
        """Increment the counter by the step size and return the current value."""
        self.current += self.step
        return self.current

    def curr(self):
        """Return the current value of the counter without incrementing it."""
        return self.current if self.current >= self.start else self.start

    def prev(self):
        """Decrement the counter by the step size and return the current value."""
        self.current -= self.step

    def __call__(self, count=True):
        """Return the next value of the counter if `count` is True, otherwise return the current value."""
        if count is None:
            return None
        elif count:
            return self.next()
        elif not count:
            return self.curr()
        else:
            return None

    def __add__(self, other: int):
        """Add a value to the current count and return the new count."""
        self.current = self.curr + other
        return self.curr()

    def __sub__(self, other: int):
        """Subtract a value from the current count and return the new count."""
        self.current = self.curr - other
        return self.curr()

    def __mult__(self, other: int):
        """Multiply the current count by a value and return the new count."""
        self.current = self.curr * other
        return self.curr()

    def __repr__(self):
        """Return a string representation of the counter."""
        return f"{self.curr()} counted"


def start_counter(start: int):
    """Start a counter with a given starting value."""
    return Counter(start)