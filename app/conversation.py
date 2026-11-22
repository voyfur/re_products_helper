from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr


MAX_PRIOR_MESSAGES = 9


class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: StrictStr = Field(min_length=1)


def format_untrusted_history(messages: Sequence[ConversationMessage]) -> str:
    return json.dumps(
        [message.model_dump() for message in messages],
        ensure_ascii=False,
        separators=(",", ":"),
    )
