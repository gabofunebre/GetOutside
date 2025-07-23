from sqlalchemy.orm import Session, joinedload
from app.models import ActionLog


def log_action(db: Session, user_id: int, action: str, *, entity_type: str | None = None, entity_id: int | None = None, detail: str = "") -> ActionLog:
    log = ActionLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_actions(db: Session) -> list[ActionLog]:
    return (
        db.query(ActionLog)
        .options(joinedload(ActionLog.user))
        .order_by(ActionLog.timestamp.desc())
        .all()
    )

