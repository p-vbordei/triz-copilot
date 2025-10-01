#!/usr/bin/env python3
"""
Unit Tests: Session Management (T056)
Tests for session state management and persistence.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
from datetime import datetime, timedelta
from uuid import uuid4
import time

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.session_manager import (
    SessionManager,
    get_session_manager,
    create_session,
    get_session,
    update_session,
    delete_session,
    list_sessions
)


class TestSessionManager(unittest.TestCase):
    """Test SessionManager core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SessionManager(storage_dir=Path(self.temp_dir))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_session(self):
        """Test creating a new session"""
        session_id = self.manager.create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)
        
        # Verify session file created
        session_file = Path(self.temp_dir) / f"{session_id}.json"
        self.assertTrue(session_file.exists())
    
    def test_get_session_data(self):
        """Test retrieving session data"""
        session_id = self.manager.create_session()
        
        data = self.manager.get_session_data(session_id)
        
        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['session_id'], session_id)
        self.assertEqual(data['stage'], 'problem_definition')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_update_session(self):
        """Test updating session data"""
        session_id = self.manager.create_session()
        
        # Update with new data
        success = self.manager.update_session(
            session_id,
            stage='contradiction_analysis',
            data={'test_key': 'test_value'}
        )
        
        self.assertTrue(success)
        
        # Verify update
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['stage'], 'contradiction_analysis')
        self.assertEqual(data['test_key'], 'test_value')
    
    def test_delete_session(self):
        """Test deleting a session"""
        session_id = self.manager.create_session()
        
        # Delete session
        success = self.manager.delete_session(session_id)
        self.assertTrue(success)
        
        # Verify deletion
        data = self.manager.get_session_data(session_id)
        self.assertIsNone(data)
        
        # Verify file deleted
        session_file = Path(self.temp_dir) / f"{session_id}.json"
        self.assertFalse(session_file.exists())
    
    def test_list_sessions(self):
        """Test listing all sessions"""
        # Create multiple sessions
        ids = []
        for i in range(3):
            session_id = self.manager.create_session()
            self.manager.save_problem_statement(session_id, f"Problem {i}")
            ids.append(session_id)
        
        # List sessions
        sessions = self.manager.list_sessions()
        
        self.assertEqual(len(sessions), 3)
        
        # Check session summaries
        for session in sessions:
            self.assertIn('session_id', session)
            self.assertIn('stage', session)
            self.assertIn('created_at', session)
            self.assertIn('has_problem', session)
            self.assertTrue(session['has_problem'])
    
    def test_save_problem_statement(self):
        """Test saving problem statement"""
        session_id = self.manager.create_session()
        problem = "Design a lightweight strong component"
        
        success = self.manager.save_problem_statement(session_id, problem)
        
        self.assertTrue(success)
        
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['problem_statement'], problem)
    
    def test_save_ideal_final_result(self):
        """Test saving ideal final result"""
        session_id = self.manager.create_session()
        ifr = "Component has zero weight but infinite strength"
        
        success = self.manager.save_ideal_final_result(session_id, ifr)
        
        self.assertTrue(success)
        
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['ideal_final_result'], ifr)
    
    def test_save_contradictions(self):
        """Test saving contradictions"""
        session_id = self.manager.create_session()
        contradictions = [
            {"improving": 1, "worsening": 14},
            {"improving": 2, "worsening": 11}
        ]
        
        success = self.manager.save_contradictions(session_id, contradictions)
        
        self.assertTrue(success)
        
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['contradictions'], contradictions)
    
    def test_save_selected_principles(self):
        """Test saving selected principles"""
        session_id = self.manager.create_session()
        principles = [1, 8, 15, 40]
        
        success = self.manager.save_selected_principles(session_id, principles)
        
        self.assertTrue(success)
        
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['selected_principles'], principles)
    
    def test_save_solution_concepts(self):
        """Test saving solution concepts"""
        session_id = self.manager.create_session()
        solutions = [
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
        
        success = self.manager.save_solution_concepts(session_id, solutions)
        
        self.assertTrue(success)
        
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['solution_concepts'], solutions)
    
    def test_get_current_stage(self):
        """Test getting current workflow stage"""
        session_id = self.manager.create_session()
        
        stage = self.manager.get_current_stage(session_id)
        self.assertEqual(stage, 'problem_definition')
        
        # Update stage
        self.manager.update_session(session_id, stage='evaluation')
        
        stage = self.manager.get_current_stage(session_id)
        self.assertEqual(stage, 'evaluation')
    
    def test_advance_stage(self):
        """Test advancing through workflow stages"""
        session_id = self.manager.create_session()
        
        stages = [
            'problem_definition',
            'ideal_final_result',
            'contradiction_analysis',
            'principle_selection',
            'solution_generation',
            'evaluation'
        ]
        
        for i, expected_stage in enumerate(stages):
            current = self.manager.get_current_stage(session_id)
            self.assertEqual(current, expected_stage)
            
            if i < len(stages) - 1:
                next_stage = self.manager.advance_stage(session_id)
                self.assertEqual(next_stage, stages[i + 1])
    
    def test_reset_session(self):
        """Test resetting session to initial state"""
        session_id = self.manager.create_session()
        
        # Add data
        self.manager.save_problem_statement(session_id, "Test problem")
        self.manager.save_ideal_final_result(session_id, "Test IFR")
        self.manager.advance_stage(session_id)
        self.manager.advance_stage(session_id)
        
        # Reset
        success = self.manager.reset_session(session_id)
        self.assertTrue(success)
        
        # Verify reset
        data = self.manager.get_session_data(session_id)
        self.assertIsNone(data.get('problem_statement'))
        self.assertIsNone(data.get('ideal_final_result'))
        self.assertEqual(data['stage'], 'problem_definition')
    
    def test_export_session(self):
        """Test exporting session to file"""
        session_id = self.manager.create_session()
        
        # Add data
        self.manager.save_problem_statement(session_id, "Export test")
        self.manager.save_solution_concepts(session_id, [{"concept": "Test"}])
        
        # Export
        export_file = Path(self.temp_dir) / "export.json"
        result = self.manager.export_session(session_id, export_file)
        
        self.assertIsNotNone(result)
        self.assertTrue(export_file.exists())
        
        # Verify export content
        with open(export_file, 'r') as f:
            exported = json.load(f)
        
        self.assertEqual(exported['problem_statement'], "Export test")
        self.assertEqual(len(exported['solution_concepts']), 1)
    
    def test_import_session(self):
        """Test importing session from file"""
        # Create export data
        export_data = {
            'session_id': 'old-id',
            'stage': 'evaluation',
            'problem_statement': 'Imported problem',
            'solution_concepts': [{'concept': 'Imported solution'}]
        }
        
        import_file = Path(self.temp_dir) / "import.json"
        with open(import_file, 'w') as f:
            json.dump(export_data, f)
        
        # Import
        new_id = self.manager.import_session(import_file)
        
        self.assertIsNotNone(new_id)
        self.assertNotEqual(new_id, 'old-id')  # Should get new ID
        
        # Verify import
        data = self.manager.get_session_data(new_id)
        self.assertEqual(data['problem_statement'], 'Imported problem')
        self.assertEqual(data['stage'], 'evaluation')
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions"""
        # Create sessions with different ages
        old_id = self.manager.create_session()
        recent_id = self.manager.create_session()
        
        # Manually set old session timestamp
        old_data = self.manager.get_session_data(old_id)
        old_data['updated_at'] = (datetime.now() - timedelta(days=35)).isoformat()
        
        old_file = Path(self.temp_dir) / f"{old_id}.json"
        with open(old_file, 'w') as f:
            json.dump(old_data, f)
        
        # Run cleanup
        deleted = self.manager.cleanup_old_sessions(days=30)
        
        self.assertEqual(deleted, 1)
        
        # Verify old deleted, recent kept
        self.assertIsNone(self.manager.get_session_data(old_id))
        self.assertIsNotNone(self.manager.get_session_data(recent_id))
    
    def test_session_not_found(self):
        """Test handling non-existent sessions"""
        fake_id = str(uuid4())
        
        # All operations should handle gracefully
        data = self.manager.get_session_data(fake_id)
        self.assertIsNone(data)
        
        success = self.manager.save_problem_statement(fake_id, "Test")
        self.assertFalse(success)
        
        stage = self.manager.get_current_stage(fake_id)
        self.assertIsNone(stage)
        
        success = self.manager.delete_session(fake_id)
        self.assertFalse(success)
    
    def test_concurrent_session_updates(self):
        """Test concurrent updates to same session"""
        session_id = self.manager.create_session()
        
        # Simulate concurrent updates
        self.manager.save_problem_statement(session_id, "Problem 1")
        self.manager.save_ideal_final_result(session_id, "IFR 1")
        
        # Both should succeed
        data = self.manager.get_session_data(session_id)
        self.assertEqual(data['problem_statement'], "Problem 1")
        self.assertEqual(data['ideal_final_result'], "IFR 1")
    
    def test_session_metadata(self):
        """Test session metadata handling"""
        session_id = self.manager.create_session()
        
        # Add metadata
        self.manager.update_session(
            session_id,
            data={
                'metadata': {
                    'user': 'test_user',
                    'project': 'test_project',
                    'tags': ['engineering', 'optimization']
                }
            }
        )
        
        data = self.manager.get_session_data(session_id)
        self.assertIn('metadata', data)
        self.assertEqual(data['metadata']['user'], 'test_user')
        self.assertIn('optimization', data['metadata']['tags'])


class TestSessionManagerSingleton(unittest.TestCase):
    """Test singleton pattern for session manager"""
    
    def test_singleton_instance(self):
        """Test that get_session_manager returns singleton"""
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        
        self.assertIs(manager1, manager2)
    
    def test_singleton_reset(self):
        """Test resetting singleton instance"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager1 = get_session_manager(storage_dir=Path(temp_dir))
            session_id = manager1.create_session()
            
            # Reset and get new instance
            manager2 = get_session_manager(
                storage_dir=Path(temp_dir),
                reset=True
            )
            
            self.assertIsNot(manager1, manager2)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestModuleFunctions(unittest.TestCase):
    """Test module-level convenience functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        get_session_manager(storage_dir=Path(self.temp_dir), reset=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_session_function(self):
        """Test create_session convenience function"""
        session_id = create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
    
    def test_get_session_function(self):
        """Test get_session convenience function"""
        session_id = create_session()
        
        data = get_session(session_id)
        
        self.assertIsNotNone(data)
        self.assertEqual(data['session_id'], session_id)
    
    def test_update_session_function(self):
        """Test update_session convenience function"""
        session_id = create_session()
        
        success = update_session(
            session_id,
            stage='evaluation',
            data={'test': 'value'}
        )
        
        self.assertTrue(success)
        
        data = get_session(session_id)
        self.assertEqual(data['stage'], 'evaluation')
        self.assertEqual(data['test'], 'value')
    
    def test_delete_session_function(self):
        """Test delete_session convenience function"""
        session_id = create_session()
        
        success = delete_session(session_id)
        self.assertTrue(success)
        
        data = get_session(session_id)
        self.assertIsNone(data)
    
    def test_list_sessions_function(self):
        """Test list_sessions convenience function"""
        # Create sessions
        for i in range(3):
            create_session()
        
        sessions = list_sessions()
        
        self.assertEqual(len(sessions), 3)


class TestSessionPersistence(unittest.TestCase):
    """Test session persistence across manager instances"""
    
    def test_persistence_across_instances(self):
        """Test that sessions persist across manager instances"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # First manager
            manager1 = SessionManager(storage_dir=Path(temp_dir))
            session_id = manager1.create_session()
            manager1.save_problem_statement(session_id, "Persistent problem")
            
            # Second manager
            manager2 = SessionManager(storage_dir=Path(temp_dir))
            data = manager2.get_session_data(session_id)
            
            self.assertIsNotNone(data)
            self.assertEqual(data['problem_statement'], "Persistent problem")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_file_corruption_handling(self):
        """Test handling of corrupted session files"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager = SessionManager(storage_dir=Path(temp_dir))
            
            # Create corrupted file
            bad_file = Path(temp_dir) / "bad-session.json"
            bad_file.write_text("not valid json {]}")
            
            # Should handle gracefully
            data = manager.get_session_data("bad-session")
            self.assertIsNone(data)
            
            # Should still work for valid sessions
            good_id = manager.create_session()
            data = manager.get_session_data(good_id)
            self.assertIsNotNone(data)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()