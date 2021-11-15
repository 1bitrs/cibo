import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from cibo import BaseApiBody, Handler, SimpleContext
from demo.handlers import api


@api.post("/user")
class UserHandler(Handler):
    class Body(BaseApiBody):
        class User(BaseModel):
            name: str = Field(description="姓名")
            emails: Optional[List[str]] = Field(description="邮箱")

            @classmethod
            def validate(cls, value: Dict):
                obj = cls(**value)
                if obj.emails:
                    if not all(
                        [
                            re.match(
                                r"^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$", email
                            )
                            for email in obj.emails
                        ]
                    ):
                        raise ValueError("email is not valid")
                return obj

        user: User
        inviter: str
        invitees: List[str]

    def handle(self, context: SimpleContext, body: Body):
        return context.success(user=body.user, inviter=body.inviter, invitees=body.invitees)