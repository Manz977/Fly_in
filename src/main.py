class Student:
    def __init__(self, name, roll, branch) -> None:
        self._name = name
        self._roll = roll
        self._branch = branch

    def _displayRollAndBranch(self):
        print("Roll:", self._roll)
        print("Branch:", self._branch)

class Geek(Student):
    def displayDetails(self):
        print("Name:", self._name)
        self._displayRollAndBranch()


obj = Geek("R2J", 1706256, "IT")
obj.displayDetails()
