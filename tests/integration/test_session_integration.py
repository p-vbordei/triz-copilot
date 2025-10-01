#!/usr/bin/env python3
"""
Integration Test: Session State Persistence (T017)
Tests session management and state persistence across operations.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.session_manager import (
    SessionManager,
    get_session_manager,
    create_session,
    get_session,
    update_session
)
from src.triz_tools.services.session_service import (
    SessionService,
    SessionData,
    SessionStage,
    get_session_service
)


class TestSessionIntegration(unittest.TestCase):
    """Test session state persistence"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=Path(self.temp_dir))
        self.session_service = get_session_service(storage_dir=Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_session_creation(self):
        """Test creating a new session"""
        session_id = self.session_manager.create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
        
        # Verify UUID format
        try:
            uuid_obj = uuid4().hex
            self.assertEqual(len(session_id.replace('-', '')), len(uuid_obj))
        except:
            self.fail(f"Invalid session ID format: {session_id}")
    
    def test_session_retrieval(self):
        """Test retrieving session data"""
        # Create session
        session_id = self.session_manager.create_session()
        
        # Retrieve session
        session_data = self.session_manager.get_session_data(session_id)
        
        self.assertIsNotNone(session_data)
        self.assertIsInstance(session_data, dict)
        self.assertEqual(session_data['session_id'], session_id)
        self.assertEqual(session_data['stage'], 'problem_definition')
    
    def test_session_update(self):
        """Test updating session data"""
        session_id = self.session_manager.create_session()
        
        # Update with problem statement
        success = self.session_manager.save_problem_statement(
            session_id,
            "Test problem for session integration"
        )
        self.assertTrue(success)
        
        # Verify update
        session_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(
            session_data['problem_statement'],
            "Test problem for session integration"
        )
    
    def test_session_stage_progression(self):
        """Test advancing through workflow stages"""
        session_id = self.session_manager.create_session()
        
        # Check initial stage
        stage = self.session_manager.get_current_stage(session_id)
        self.assertEqual(stage, 'problem_definition')
        
        # Advance stage
        new_stage = self.session_manager.advance_stage(session_id)
        self.assertEqual(new_stage, 'ideal_final_result')
        
        # Advance again
        new_stage = self.session_manager.advance_stage(session_id)
        self.assertEqual(new_stage, 'contradiction_analysis')
    
    def test_session_data_persistence(self):
        """Test data persistence across manager instances"""
        session_id = self.session_manager.create_session()
        
        # Save various data
        self.session_manager.save_problem_statement(
            session_id,
            "Persistent problem"
        )
        self.session_manager.save_ideal_final_result(
            session_id,
            "Persistent IFR"
        )
        self.session_manager.save_contradictions(
            session_id,
            [{"improving": 1, "worsening": 14}]
        )
        
        # Create new manager instance
        new_manager = SessionManager(storage_dir=Path(self.temp_dir))
        
        # Retrieve session
        session_data = new_manager.get_session_data(session_id)
        
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['problem_statement'], "Persistent problem")
        self.assertEqual(session_data['ideal_final_result'], "Persistent IFR")
        self.assertEqual(len(session_data['contradictions']), 1)
    
    def test_session_reset(self):
        """Test resetting session to initial state"""
        session_id = self.session_manager.create_session()
        
        # Add data
        self.session_manager.save_problem_statement(session_id, "Problem")
        self.session_manager.advance_stage(session_id)
        
        # Reset
        success = self.session_manager.reset_session(session_id)
        self.assertTrue(success)
        
        # Verify reset
        session_data = self.session_manager.get_session_data(session_id)
        self.assertIsNone(session_data['problem_statement'])
        self.assertEqual(session_data['stage'], 'problem_definition')
    
    def test_session_deletion(self):
        """Test deleting a session"""
        session_id = self.session_manager.create_session()
        
        # Delete
        success = self.session_manager.delete_session(session_id)
        self.assertTrue(success)
        
        # Try to retrieve
        session_data = self.session_manager.get_session_data(session_id)
        self.assertIsNone(session_data)
    
    def test_list_sessions(self):
        """Test listing multiple sessions"""
        # Create multiple sessions
        session_ids = []
        for i in range(5):
            session_id = self.session_manager.create_session()
            self.session_manager.save_problem_statement(
                session_id,
                f"Problem {i}"
            )
            session_ids.append(session_id)
        
        # List sessions
        sessions = self.session_manager.list_sessions(limit=10)
        
        self.assertEqual(len(sessions), 5)
        
        # Verify session summaries
        for session in sessions:
            self.assertIn('session_id', session)
            self.assertIn('stage', session)
            self.assertIn('has_problem', session)
            self.assertTrue(session['has_problem'])
    
    def test_session_export_import(self):
        """Test exporting and importing sessions"""
        # Create and populate session
        session_id = self.session_manager.create_session()
        self.session_manager.save_problem_statement(
            session_id,
            "Exportable problem"
        )
        self.session_manager.save_solution_concepts(
            session_id,
            [{"concept": "Solution 1", "feasibility": 0.8}]
        )
        
        # Export
        export_file = Path(self.temp_dir) / "export.json"
        result = self.session_manager.export_session(session_id, export_file)
        self.assertIsNotNone(result)
        self.assertTrue(export_file.exists())
        
        # Import to new manager
        new_manager = SessionManager(storage_dir=Path(self.temp_dir) / "new")
        imported_id = new_manager.import_session(export_file)
        
        self.assertIsNotNone(imported_id)
        self.assertNotEqual(imported_id, session_id)  # Should get new ID
        
        # Verify imported data
        imported_data = new_manager.get_session_data(imported_id)
        self.assertEqual(imported_data['problem_statement'], "Exportable problem")
        self.assertEqual(len(imported_data['solution_concepts']), 1)
    
    def test_session_cleanup(self):
        """Test cleaning up old sessions"""
        # Create old session (mock old timestamp)
        old_session = self.session_service.create_session()
        old_session.updated_at = datetime.now() - timedelta(days=40)
        self.session_service._save_session(old_session)
        
        # Create recent session
        recent_id = self.session_manager.create_session()
        
        # Run cleanup
        deleted_count = self.session_manager.cleanup_old_sessions(days=30)
        
        self.assertEqual(deleted_count, 1)
        
        # Verify recent session still exists
        recent_data = self.session_manager.get_session_data(recent_id)
        self.assertIsNotNone(recent_data)
    
    def test_concurrent_session_access(self):
        """Test concurrent access to same session"""
        session_id = self.session_manager.create_session()
        
        # Simulate concurrent updates
        manager1 = SessionManager(storage_dir=Path(self.temp_dir))
        manager2 = SessionManager(storage_dir=Path(self.temp_dir))
        
        # Both update same session
        manager1.save_problem_statement(session_id, "Problem from manager1")
        manager2.save_ideal_final_result(session_id, "IFR from manager2")
        
        # Verify both updates persisted
        final_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(final_data['problem_statement'], "Problem from manager1")
        self.assertEqual(final_data['ideal_final_result'], "IFR from manager2")
    
    def test_session_with_complete_workflow(self):
        """Test session with complete TRIZ workflow"""
        session_id = self.session_manager.create_session()
        
        # Problem definition
        self.session_manager.save_problem_statement(
            session_id,
            "Design lightweight strong component"
        )
        self.session_manager.advance_stage(session_id)
        
        # IFR
        self.session_manager.save_ideal_final_result(
            session_id,
            "Component has zero weight but infinite strength"
        )
        self.session_manager.advance_stage(session_id)
        
        # Contradictions
        self.session_manager.save_contradictions(
            session_id,
            [
                {"improving": 1, "worsening": 14},
                {"improving": 2, "worsening": 11}
            ]
        )
        self.session_manager.advance_stage(session_id)
        
        # Principles
        self.session_manager.save_selected_principles(
            session_id,
            [1, 8, 15, 40]
        )
        self.session_manager.advance_stage(session_id)
        
        # Solutions
        self.session_manager.save_solution_concepts(
            session_id,
            [
                {
                    "concept": "Honeycomb structure",
                    "principle": 1,
                    "feasibility": 0.9
                },
                {
                    "concept": "Composite materials",
                    "principle": 40,
                    "feasibility": 0.85
                }
            ]
        )
        self.session_manager.advance_stage(session_id)
        
        # Verify complete session
        final_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(final_data['stage'], 'evaluation')
        self.assertIsNotNone(final_data['problem_statement'])
        self.assertIsNotNone(final_data['ideal_final_result'])
        self.assertEqual(len(final_data['contradictions']), 2)
        self.assertEqual(len(final_data['selected_principles']), 4)
        self.assertEqual(len(final_data['solution_concepts']), 2)


class TestSessionServiceIntegration(unittest.TestCase):
    """Test low-level session service"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = SessionService(storage_dir=Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_session_data_model(self):
        """Test SessionData model"""
        session = self.service.create_session()
        
        self.assertIsInstance(session, SessionData)
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.stage, SessionStage.PROBLEM_DEFINITION)
        self.assertIsInstance(session.metadata, dict)
    
    def test_session_stage_enum(self):
        """Test SessionStage enum"""
        stages = list(SessionStage)
        
        expected_stages = [
            SessionStage.PROBLEM_DEFINITION,
            SessionStage.IDEAL_FINAL_RESULT,
            SessionStage.CONTRADICTION_ANALYSIS,
            SessionStage.PRINCIPLE_SELECTION,
            SessionStage.SOLUTION_GENERATION,
            SessionStage.EVALUATION
        ]
        
        self.assertEqual(stages, expected_stages)
    
    def test_session_to_dict(self):
        """Test session serialization"""
        session = self.service.create_session()
        session.problem_statement = "Test problem"
        session.contradictions = [{"test": "data"}]
        
        data = session.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['problem_statement'], "Test problem")
        self.assertEqual(data['contradictions'], [{"test": "data"}])
        self.assertEqual(data['stage'], 'problem_definition')
    
    def test_session_from_dict(self):
        """Test session deserialization"""
        data = {
            'session_id': str(uuid4()),
            'stage': 'contradiction_analysis',
            'problem_statement': 'Test problem',
            'contradictions': [{'improving': 1, 'worsening': 14}],
            'metadata': {'source': 'test'}
        }
        
        session = SessionData.from_dict(data)
        
        self.assertEqual(session.session_id, data['session_id'])
        self.assertEqual(session.stage, SessionStage.CONTRADICTION_ANALYSIS)
        self.assertEqual(session.problem_statement, 'Test problem')
        self.assertEqual(len(session.contradictions), 1)


if __name__ == '__main__':
    unittest.main()