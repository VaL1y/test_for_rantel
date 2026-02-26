import enum


class OperatorStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    busy = "busy"


class TicketStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    waiting = "waiting"
    resolved = "resolved"
    closed = "closed"
