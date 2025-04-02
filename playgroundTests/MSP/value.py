import time

class TimedValue:
    NEW_VALUE = 0
    ALREADY_READ = 1
    REQUESTED = 2
    NEVER_UPDATED = 3

    def __init__(self, initial_value=None):
        self._value = initial_value
        self._state = self.NEVER_UPDATED

        self.lastSetTime = None
        self.lastGetTime = None

    @property
    def value(self):
        self.lastGetTime = time.time()
        self._state = self.ALREADY_READ
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self._state = self.NEW_VALUE
        self.lastSetTime = time.time()

    def __repr__(self):
        return str(self._value)