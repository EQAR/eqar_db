"""
helper classes
"""

class Esg:
    """
    A single ESG standard
    """

    AcceptedValues = {
        1: range(1,11),
        2: range(1,8),
        3: range(1,8),
    }

    def __init__(self, part, number):
        self.part = int(part)
        self.number = int(number)
        if self.part not in self.AcceptedValues.keys():
            raise ValueError(f'The ESG have no part {self.part}.')
        if self.number not in self.AcceptedValues[self.part]:
            raise ValueError(f'The ESG have no standard {self.part}.{self.number}.')

    def __str__(self):
        return f'ESG {self.part}.{self.number}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.part}, {self.number})'

    @property
    def _dbname(self):
        return f'{self.part}_{self.number}'

    @property
    def rc(self):
        return f'rc_{self._dbname}'

    @property
    def rapp(self):
        return f'rapp_{self._dbname}'

    @property
    def panel(self):
        return f'panel_{self._dbname}'


class EsgList(list):
    """
    A list of ESG standards relevant for registration
    """

    def __init__(self):
        super().__init__()
        for s in range(1,8):
            self.append(Esg(2, s))
        for s in range(1,7):
            self.append(Esg(3, s))

