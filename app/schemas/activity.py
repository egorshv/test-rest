from pydantic import BaseModel, ConfigDict


class ActivityBase(BaseModel):
    name: str
    parent_id: int | None = None


class ActivityRead(ActivityBase):
    id: int
    level: int
    children: list["ActivityRead"] | None = None

    model_config = ConfigDict(from_attributes=True)


ActivityRead.model_rebuild()
