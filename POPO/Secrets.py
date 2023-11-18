from pydantic import BaseModel


class Secrets(BaseModel):
    client_id: str
    client_secret: str
    firebase_secret: dict[str, str]
    owner: str

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, by_alias=True)
