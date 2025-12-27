from typing import Self

from pydantic import BaseModel


class ClonableBaseModel(BaseModel):

    def copy_with(self, **kwargs) -> Self:
        data = self.model_dump()
        data.update(kwargs)
        return type(self)(**data)

    def just_copy(self):
        return self.copy_with()
