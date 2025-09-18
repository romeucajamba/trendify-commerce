from dataclasses import dataclass 
from typing import Optional
from datetime import datetime

@dataclass
class UserEntity:
    id: str
    name: str
    last_name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    confirmation_code: Optional[str] = None
    confirmation_expires_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        return "@" in self.email
