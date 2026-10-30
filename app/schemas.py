from pydantic import BaseModel, EmailStr, Field
class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=12, max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class RefreshIn(BaseModel): refresh_token: str
class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)
class OptimizationIn(BaseModel): building_id: int
class ReportIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    report_type: str = Field(default="SUMMARY", max_length=50)
class ExplainIn(BaseModel):
    subject: str = Field(pattern="^(energy|forecast|optimization|impact|anomaly)$")
    building_id: int | None = None
