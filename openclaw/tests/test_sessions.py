"""Tests for session management."""

import pytest
from openclaw.config import Config
from openclaw.sessions import SessionManager, Session


def test_session_creation():
    """Test creating a new session."""
    session = Session(channel="test", chat_id="user1")
    assert session.channel == "test"
    assert session.chat_id == "user1"
    assert len(session.messages) == 0


def test_session_add_message():
    """Test adding messages to session."""
    session = Session(channel="test", chat_id="user1")

    msg1 = session.add_message("user", "Hello")
    msg2 = session.add_message("assistant", "Hi there!")

    assert len(session.messages) == 2
    assert msg1.role == "user"
    assert msg2.role == "assistant"


def test_session_manager():
    """Test session manager operations."""
    config = Config()
    manager = SessionManager(config)

    # Get or create session
    session = manager.get_or_create_session("console", "user1")
    assert session is not None
    assert manager.get_active_session_count() == 1

    # Add message
    manager.add_message("console", "user1", "user", "Hello")
    assert len(session.messages) == 1

    # Get messages
    messages = manager.get_session_messages("console", "user1")
    assert len(messages) == 1


def test_session_to_llm_format():
    """Test converting session to LLM message format."""
    session = Session(channel="test", chat_id="user1")
    session.add_message("system", "You are helpful")
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi!")

    llm_messages = session.to_llm_messages()
    assert len(llm_messages) == 3
    assert llm_messages[0]["role"] == "system"
    assert llm_messages[1]["role"] == "user"
    assert llm_messages[2]["role"] == "assistant"
