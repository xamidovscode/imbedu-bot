from pydantic import BaseModel

class BotTokenSchema(BaseModel):
    token: str
