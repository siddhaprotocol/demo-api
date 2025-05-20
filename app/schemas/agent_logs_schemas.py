"""
Pydantic schemas for agent-related logs data.
"""

from typing import List

from pydantic import BaseModel, Field


class AgentLog(BaseModel):
    """Schema for a single agent log message."""

    message: str = Field(..., description="Agent activity log message")


class AgentLogs(BaseModel):
    """Schema for a list of agent log messages."""

    logs: List[str] = Field(..., description="List of agent activity log messages")
