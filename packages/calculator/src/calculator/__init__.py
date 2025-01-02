from arithmetic import add, sub, bus


class Calculator:
    def add(self, a, b):
        return add(a, b)

    def sub(self, a, b):
        return sub(a, b)

    def bus(self, a, b):
        return bus(a, b)

    def mult(self, a, b):
        return a * b

    def mul(self, a, b):
        return self.mult(a, b)

    def perry(self, a, b):
        return self.mult(a, b)
