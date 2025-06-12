"""Tests for story create command."""

import pytest
from unittest.mock import Mock, MagicMock
from click.testing import CliRunner
from sc.commands.story import story
from useshortcut.models import StoryInput, UpdateStoryInput


def test_story_create_success(mocker):
    """Test successful story creation flow."""
    # Mock the client
    mock_client = Mock()
    mock_get_client = mocker.patch('sc.commands.story.get_client')
    mock_get_client.return_value = mock_client
    
    # Mock API responses
    mock_projects = [
        Mock(id=1, name="API Backend", archived=False),
        Mock(id=2, name="Frontend", archived=False),
    ]
    mock_workflows = [Mock(states=[
        Mock(id=100, name="Todo"),
        Mock(id=101, name="In Progress"),
        Mock(id=102, name="Done"),
    ])]
    mock_members = [
        Mock(id="mem-1", disabled=False, profile=Mock(name="Sarah Chen", email_address="sarah@example.com")),
        Mock(id="mem-2", disabled=False, profile=Mock(name="Alex Johnson", email_address="alex@example.com")),
    ]
    mock_epics = [
        Mock(id=10, name="Auth Epic", archived=False, project_ids=[1]),
        Mock(id=11, name="API Epic", archived=False, project_ids=[1]),
    ]
    mock_iterations = [
        Mock(id=20, name="Sprint 24", status="started"),
        Mock(id=21, name="Sprint 25", status="unstarted"),
    ]
    mock_groups = [
        Mock(id="grp-1", name="Backend", archived=False),
        Mock(id="grp-2", name="Frontend", archived=False),
    ]
    
    mock_client.list_projects.return_value = mock_projects
    mock_client.list_workflows.return_value = mock_workflows
    mock_client.list_members.return_value = mock_members
    mock_client.list_epics.return_value = mock_epics
    mock_client.list_iterations.return_value = mock_iterations
    mock_client.list_groups.return_value = mock_groups
    
    # Mock the created story
    mock_story = Mock(id=12345, app_url="https://app.shortcut.com/story/12345")
    mock_client.create_story.return_value = mock_story
    mock_client.update_story.return_value = mock_story
    
    # Mock questionary prompts
    mock_questionary = mocker.patch('sc.commands.story.questionary')
    
    # Configure mock responses for each prompt
    mock_questionary.text.return_value.ask.side_effect = [
        "Implement user authentication",  # title
        "Add login and logout endpoints",  # description
        "5",  # estimate
    ]
    
    mock_questionary.select.return_value.ask.side_effect = [
        "feature",  # story type
        1,  # project_id
        "mem-1",  # owner_id
        10,  # epic_id
        20,  # iteration_id
        "grp-1",  # group_id
    ]
    
    # Run the command
    runner = CliRunner()
    result = runner.invoke(story, ['create'])
    
    # Verify success
    assert result.exit_code == 0
    assert "✓ Created story #12345" in result.output
    assert "View in browser: https://app.shortcut.com/story/12345" in result.output
    
    # Verify the story was created with correct data
    mock_client.create_story.assert_called_once()
    created_story = mock_client.create_story.call_args[0][0]
    assert created_story.name == "Implement user authentication"
    assert created_story.story_type == "feature"
    assert created_story.project_id == 1
    assert created_story.description == "Add login and logout endpoints"
    assert created_story.workflow_state_id == 100  # First state ID
    assert created_story.epic_id == 10
    
    # Verify update was called with additional fields
    mock_client.update_story.assert_called_once_with(12345, mocker.ANY)
    update_data = mock_client.update_story.call_args[0][1]
    assert update_data.estimate == 5
    assert update_data.owner_ids == ["mem-1"]
    assert update_data.iteration_id == 20
    assert update_data.group_id == "grp-1"


def test_story_create_cancelled(mocker):
    """Test story creation cancelled by user."""
    # Mock the client
    mock_client = Mock()
    mock_get_client = mocker.patch('sc.commands.story.get_client')
    mock_get_client.return_value = mock_client
    
    # Mock empty lists for simplicity
    mock_client.list_projects.return_value = []
    mock_client.list_workflows.return_value = []
    mock_client.list_members.return_value = []
    mock_client.list_epics.return_value = []
    mock_client.list_iterations.return_value = []
    mock_client.list_groups.return_value = []
    
    # Mock questionary to return None (user cancelled)
    mock_questionary = mocker.patch('sc.commands.story.questionary')
    mock_questionary.text.return_value.ask.return_value = None
    
    # Run the command
    runner = CliRunner()
    result = runner.invoke(story, ['create'])
    
    # Verify cancellation
    assert result.exit_code == 0
    assert "Story creation cancelled" in result.output
    
    # Verify no story was created
    mock_client.create_story.assert_not_called()


def test_story_create_no_estimate(mocker):
    """Test story creation with no estimate provided."""
    # Mock the client
    mock_client = Mock()
    mock_get_client = mocker.patch('sc.commands.story.get_client')
    mock_get_client.return_value = mock_client
    
    # Mock API responses (minimal for this test)
    mock_client.list_projects.return_value = [Mock(id=1, name="Project", archived=False)]
    mock_client.list_workflows.return_value = [Mock(states=[Mock(id=100, name="Todo")])]
    mock_client.list_members.return_value = []
    mock_client.list_epics.return_value = []
    mock_client.list_iterations.return_value = []
    mock_client.list_groups.return_value = []
    
    # Mock the created story
    mock_story = Mock(id=12346, app_url="https://app.shortcut.com/story/12346")
    mock_client.create_story.return_value = mock_story
    
    # Mock questionary prompts
    mock_questionary = mocker.patch('sc.commands.story.questionary')
    
    mock_questionary.text.return_value.ask.side_effect = [
        "Fix bug in auth",  # title
        "",  # description (empty)
        "",  # estimate (empty)
    ]
    
    mock_questionary.select.return_value.ask.side_effect = [
        "bug",  # story type
        1,  # project_id
        None,  # owner_id (unassigned)
        None,  # epic_id (no epic)
        None,  # iteration_id (no iteration)
        None,  # group_id (no team)
    ]
    
    # Run the command
    runner = CliRunner()
    result = runner.invoke(story, ['create'])
    
    # Verify success
    assert result.exit_code == 0
    assert "✓ Created story #12346" in result.output
    
    # Verify the story was created with correct data
    created_story = mock_client.create_story.call_args[0][0]
    assert created_story.name == "Fix bug in auth"
    assert created_story.story_type == "bug"
    assert created_story.workflow_state_id == 100
    assert created_story.description is None
    assert created_story.epic_id is None
    
    # Verify no update was called (all optional fields were None/empty)
    mock_client.update_story.assert_not_called()


def test_story_create_no_projects(mocker):
    """Test story creation when no projects are available."""
    # Mock the client
    mock_client = Mock()
    mock_get_client = mocker.patch('sc.commands.story.get_client')
    mock_get_client.return_value = mock_client
    
    # Mock API responses with no projects
    mock_client.list_projects.return_value = []  # No projects
    mock_client.list_workflows.return_value = []
    mock_client.list_members.return_value = []
    mock_client.list_epics.return_value = []
    mock_client.list_iterations.return_value = []
    mock_client.list_groups.return_value = []
    
    # Mock questionary prompts
    mock_questionary = mocker.patch('sc.commands.story.questionary')
    
    mock_questionary.text.return_value.ask.side_effect = [
        "Test Story",  # title
    ]
    
    mock_questionary.select.return_value.ask.side_effect = [
        "feature",  # story type
    ]
    
    # Run the command
    runner = CliRunner()
    result = runner.invoke(story, ['create'])
    
    # Verify it failed gracefully
    assert result.exit_code == 0
    assert "No projects available. Please create a project first." in result.output
    
    # Verify no story was created
    mock_client.create_story.assert_not_called()


def test_story_create_all_projects_archived(mocker):
    """Test story creation when all projects are archived."""
    # Mock the client
    mock_client = Mock()
    mock_get_client = mocker.patch('sc.commands.story.get_client')
    mock_get_client.return_value = mock_client
    
    # Mock API responses with only archived projects
    mock_client.list_projects.return_value = [
        Mock(id=1, name="Old Project", archived=True),
        Mock(id=2, name="Archived Project", archived=True),
    ]
    mock_client.list_workflows.return_value = []
    mock_client.list_members.return_value = []
    mock_client.list_epics.return_value = []
    mock_client.list_iterations.return_value = []
    mock_client.list_groups.return_value = []
    
    # Mock questionary prompts
    mock_questionary = mocker.patch('sc.commands.story.questionary')
    
    mock_questionary.text.return_value.ask.side_effect = [
        "Test Story",  # title
    ]
    
    mock_questionary.select.return_value.ask.side_effect = [
        "feature",  # story type
    ]
    
    # Run the command
    runner = CliRunner()
    result = runner.invoke(story, ['create'])
    
    # Verify it failed gracefully
    assert result.exit_code == 0
    assert "No active projects available. All projects are archived." in result.output
    
    # Verify no story was created
    mock_client.create_story.assert_not_called()