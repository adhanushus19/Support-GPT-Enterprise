import time
import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from src.models.db_models import ResponseApproval, Ticket
from src.models.schemas import ResponseApprovalRequest

logger = logging.getLogger("supportgpt.approval.workflows")

class HumanInTheLoopService:
    """
    Manages AI response validation, edits, approvals, and latency tracking.
    """
    async def create_pending_approval(
        self, 
        db: AsyncSession, 
        ticket_id: int, 
        drafted_response: str
    ) -> ResponseApproval:
        """Create a pending response approval ticket."""
        approval = ResponseApproval(
            ticket_id=ticket_id,
            drafted_response=drafted_response,
            status="pending",
            created_at=datetime.datetime.utcnow()
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        logger.info(f"Created pending approval ID {approval.id} for ticket ID {ticket_id}")
        return approval

    async def get_pending_approvals(self, db: AsyncSession) -> list[ResponseApproval]:
        """Fetch all response approvals currently pending review."""
        result = await db.execute(select(ResponseApproval).filter(ResponseApproval.status == "pending"))
        return list(result.scalars().all())

    async def process_agent_approval(
        self, 
        db: AsyncSession, 
        approval_id: int, 
        agent_id: int,
        req: ResponseApprovalRequest
    ) -> ResponseApproval:
        """
        Approve, reject, or edit an AI draft.
        Tracks response latency between AI generation and human review.
        """
        result = await db.execute(select(ResponseApproval).filter(ResponseApproval.id == approval_id))
        approval = result.scalars().first()
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Approval record {approval_id} not found."
            )
            
        if approval.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Approval record {approval_id} has already been processed (status: {approval.status})."
            )

        # Calculate latency in seconds
        now = datetime.datetime.utcnow()
        delta = now - approval.created_at
        latency = delta.total_seconds()

        # Update record
        approval.status = req.status
        approval.agent_id = agent_id
        approval.latency_seconds = latency
        
        if req.modified_response:
            approval.modified_response = req.modified_response
        else:
            approval.modified_response = approval.drafted_response

        # If approved or modified, update ticket status to completed / resolved
        if req.status in ["approved", "modified"]:
            ticket_result = await db.execute(select(Ticket).filter(Ticket.id == approval.ticket_id))
            ticket = ticket_result.scalars().first()
            if ticket:
                ticket.status = "resolved"

        await db.commit()
        await db.refresh(approval)
        logger.info(f"Processed approval ID {approval_id} with status {req.status} by agent {agent_id}.")
        return approval

human_it_loop_service = HumanInTheLoopService()
