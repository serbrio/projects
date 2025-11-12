from __future__ import annotations
#from typing import Self  # available from Python 3.11



class Levels:
    """
    Levels() -> new Levels object with one level.
    Levels(amount=N) -> new Levels object with N levels.

    Level in levels is presented as dictionary with descriptive keys and values.
    Levels object is iterable.
    """
    def __init__(self, amount: int=1) -> None:
        if amount >= 1:
            self.amount = amount
        else:
            self.amount = 1
        self.generate_levels()
    
    def generate_levels(self) -> None:
        self.levels = [{"level": n, "monsters": n, "rams": n+1, "coins": n*10} for n in range(1, self.amount+1)]

    def __iter__(self) -> Levels:
        self.n = 0
        return self
    
    def __next__(self) -> dict:
        if self.n < self.amount:
            level = self.levels[self.n]
            self.n += 1
            return level
        else:
            raise StopIteration