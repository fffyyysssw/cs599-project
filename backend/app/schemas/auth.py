from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username", "password")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    role: str
    department: str
    email: str | None = None


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
