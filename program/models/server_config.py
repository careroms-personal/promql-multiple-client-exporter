from pydantic import BaseModel
from typing import Literal, Optional

class AuthConfig(BaseModel):
  type: Literal["none", "bearer", "basic"] = "none"

class ServerEntry(BaseModel):
  id: str
  url: str
  api: str = "api/v1"
  timeout: str
  auth: Optional[AuthConfig] = None

class ServerConfig(BaseModel):
  servers: list[ServerEntry]
