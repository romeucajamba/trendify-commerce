from dataclasses import dataclass 
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

    def is_valid(self) -> bool:
        return "@" in self.email
