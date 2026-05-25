from pydantic import BaseModel


class FieldAttribute(BaseModel):
    field_id: str
    field_value: str


class CreateCardInput(BaseModel):
    pipe_id: str
    title: str
    fields_attributes: list[FieldAttribute]


class UpdateCardFieldInput(BaseModel):
    card_id: str
    field_id: str
    new_value: str