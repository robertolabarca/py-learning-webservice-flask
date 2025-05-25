from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Student:
    id:int
    name:str
    age:str
    can_vote:bool=field(init=False)

    def __post_init__(self):
        """
        docstring
        """
        if self.age < 15:
            raise ValueError("Age mayor de 18")
        self.can_vote = self.age >= 18

    def __repr__(self):
        return f"Student(id={self.id}, name='{self.name}', age={self.age})"