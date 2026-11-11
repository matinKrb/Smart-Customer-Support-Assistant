import logging
from .models import Conversation , AuditLog

logger = logging.getLogger('state_machine')

ALLOWED_TRANSITIONS = {
    Conversation.Status.ACTIVE: [
        Conversation.Status.WAITING_FOR_HUMAN,
        Conversation.Status.RESOLVED,
        Conversation.Status.CLOSED,
    ],
    Conversation.Status.WAITING_FOR_HUMAN: [
        Conversation.Status.HUMAN_HANDLING,
        Conversation.Status.ACTIVE,
    ],
    Conversation.Status.HUMAN_HANDLING: [
        Conversation.Status.RESOLVED,
        Conversation.Status.ACTIVE,
    ],
    Conversation.Status.RESOLVED: [
        Conversation.Status.CLOSED,
        Conversation.Status.ACTIVE,
    ],
    Conversation.Status.CLOSED: [],
}


def can_transition(current_status: str, new_status: str) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def transition_to(conversation, new_status: str , reason : str = None) -> bool:
    current_status = conversation.status

    if not can_transition(current_status, new_status):
        logger.warning(
            f"Invalid transition attempted: conversation_id={conversation.uuid} "
            f"from={current_status} to={new_status}"
        )
        return False

    conversation.status = new_status
    conversation.save()
    logger.info(f"conversation_id={conversation.uuid} transitioned {current_status} -> {new_status}")

    AuditLog.objects.create(
        conversation=conversation,
        event_type=AuditLog.EventType.STATUS_CHANGED,
        details={"from": current_status, "to": new_status, "reason": reason},
    )

    logger.info(f"conversation_id={conversation.uuid} transitioned {current_status} -> {new_status}")
    return True