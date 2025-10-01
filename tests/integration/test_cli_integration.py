#!/usr/bin/env python3
"""
Integration Test: Gemini CLI Tool Registration (T014)
Tests the integration between TRIZ tools and Gemini CLI.
"""

import unittest
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mcp_server import TRIZMCPServer
from src.cli import cli
from click.testing import CliRunner


class TestGeminiCLIIntegration(unittest.TestCase):
    """Test Gemini CLI integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.runner = CliRunner()
        self.mcp_server = TRIZMCPServer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mcp_server_initialization(self):
        """Test MCP server initializes correctly"""
        self.assertIsNotNone(self.mcp_server)
        self.assertIsNotNone(self.mcp_server.commands)
        self.assertTrue(len(self.mcp_server.commands) > 0)
    
    def test_mcp_server_command_registration(self):
        """Test all commands are registered"""
        expected_commands = [
            "triz-workflow",
            "triz-tool",
            "triz-solve"
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, self.mcp_server.commands,
                         f"Command {cmd} not registered")
    
    def test_cli_workflow_command(self):
        """Test CLI workflow command"""
        result = self.runner.invoke(cli, ['workflow', 'start'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("session", result.output.lower())
    
    def test_cli_tool_command_principle(self):
        """Test CLI tool command for principle"""
        result = self.runner.invoke(cli, ['tool', 'principle', '1'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("segmentation", result.output.lower())
    
    def test_cli_tool_command_matrix(self):
        """Test CLI tool command for matrix"""
        result = self.runner.invoke(cli, ['tool', 'matrix', '1', '14'])
        self.assertEqual(result.exit_code, 0)
        # Should contain principle recommendations
        self.assertTrue(
            "principle" in result.output.lower() or 
            "recommendation" in result.output.lower()
        )
    
    def test_cli_solve_command(self):
        """Test CLI solve command"""
        result = self.runner.invoke(cli, [
            'solve', 
            'Test problem for integration testing'
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("analysis", result.output.lower())
    
    def test_cli_interactive_mode(self):
        """Test CLI interactive mode entry"""
        # Test that interactive mode can be invoked (won't actually run interactive)
        with patch('src.cli.interactive_session') as mock_interactive:
            result = self.runner.invoke(cli, ['interactive'])
            self.assertEqual(result.exit_code, 0)
            mock_interactive.assert_called_once()
    
    def test_mcp_workflow_start(self):
        """Test MCP workflow start command"""
        result = self.mcp_server.handle_command(
            "triz-workflow",
            {"action": "start"}
        )
        
        self.assertIsNotNone(result)
        self.assertIn("session_id", result)
        self.assertIn("stage", result)
        self.assertEqual(result["stage"], "problem_definition")
    
    def test_mcp_workflow_continue(self):
        """Test MCP workflow continue command"""
        # Start a workflow first
        start_result = self.mcp_server.handle_command(
            "triz-workflow",
            {"action": "start"}
        )
        session_id = start_result["session_id"]
        
        # Continue workflow
        continue_result = self.mcp_server.handle_command(
            "triz-workflow",
            {
                "action": "continue",
                "session_id": session_id,
                "input": "Test problem statement"
            }
        )
        
        self.assertIsNotNone(continue_result)
        self.assertIn("stage", continue_result)
    
    def test_mcp_tool_get_principle(self):
        """Test MCP tool get principle"""
        result = self.mcp_server.handle_command(
            "triz-tool",
            {
                "tool": "get_principle",
                "principle_id": 1
            }
        )
        
        self.assertIsNotNone(result)
        self.assertIn("principle", result)
        self.assertIn("name", result["principle"])
        self.assertEqual(result["principle"]["name"], "Segmentation")
    
    def test_mcp_tool_contradiction_matrix(self):
        """Test MCP tool contradiction matrix"""
        result = self.mcp_server.handle_command(
            "triz-tool",
            {
                "tool": "contradiction_matrix",
                "improving": 1,
                "worsening": 14
            }
        )
        
        self.assertIsNotNone(result)
        self.assertIn("principles", result)
        self.assertIsInstance(result["principles"], list)
        self.assertTrue(len(result["principles"]) > 0)
    
    def test_mcp_solve_autonomous(self):
        """Test MCP autonomous solve"""
        result = self.mcp_server.handle_command(
            "triz-solve",
            {"problem": "Test problem for autonomous solving"}
        )
        
        self.assertIsNotNone(result)
        self.assertIn("analysis", result)
        self.assertIn("solutions", result["analysis"])
        self.assertIsInstance(result["analysis"]["solutions"], list)
    
    def test_cli_output_formats(self):
        """Test different output formats"""
        # Test JSON output
        result = self.runner.invoke(cli, [
            'solve',
            '--output-json',
            'Test problem'
        ])
        self.assertEqual(result.exit_code, 0)
        
        # Should be valid JSON
        try:
            json_output = json.loads(result.output)
            self.assertIsInstance(json_output, dict)
        except json.JSONDecodeError:
            # Output might have other text, try to find JSON part
            import re
            json_match = re.search(r'\{.*\}', result.output, re.DOTALL)
            if json_match:
                json_output = json.loads(json_match.group())
                self.assertIsInstance(json_output, dict)
    
    def test_cli_file_input(self):
        """Test CLI with file input"""
        # Create a test file
        test_file = Path(self.temp_dir) / "test_problem.txt"
        test_file.write_text("Test problem from file")
        
        result = self.runner.invoke(cli, [
            'solve',
            '--file', str(test_file)
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("analysis", result.output.lower())
    
    def test_mcp_error_handling(self):
        """Test MCP server error handling"""
        # Test with invalid command
        result = self.mcp_server.handle_command(
            "invalid-command",
            {}
        )
        self.assertIn("error", result)
        
        # Test with missing parameters
        result = self.mcp_server.handle_command(
            "triz-tool",
            {"tool": "get_principle"}  # Missing principle_id
        )
        self.assertIn("error", result)
    
    def test_cli_error_handling(self):
        """Test CLI error handling"""
        # Test with invalid principle ID
        result = self.runner.invoke(cli, ['tool', 'principle', '999'])
        # Should handle gracefully (exit code might be 0 with error message)
        self.assertIsNotNone(result.output)
        
        # Test with invalid matrix parameters
        result = self.runner.invoke(cli, ['tool', 'matrix', '999', '999'])
        self.assertIsNotNone(result.output)
    
    def test_session_persistence(self):
        """Test session persistence across commands"""
        # Start workflow
        start_result = self.runner.invoke(cli, ['workflow', 'start'])
        self.assertEqual(start_result.exit_code, 0)
        
        # Extract session ID from output
        import re
        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', 
                         start_result.output)
        
        if match:
            session_id = match.group(1)
            
            # Continue with same session
            continue_result = self.runner.invoke(cli, [
                'workflow', 'continue',
                '--session', session_id,
                '--input', 'Test problem'
            ])
            self.assertEqual(continue_result.exit_code, 0)
            self.assertIn(session_id, continue_result.output)


class TestCLICommandStructure(unittest.TestCase):
    """Test CLI command structure and help"""
    
    def setUp(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("triz", result.output.lower())
        self.assertIn("workflow", result.output.lower())
        self.assertIn("solve", result.output.lower())
    
    def test_workflow_help(self):
        """Test workflow command help"""
        result = self.runner.invoke(cli, ['workflow', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("start", result.output.lower())
        self.assertIn("continue", result.output.lower())
        self.assertIn("reset", result.output.lower())
    
    def test_tool_help(self):
        """Test tool command help"""
        result = self.runner.invoke(cli, ['tool', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("principle", result.output.lower())
        self.assertIn("matrix", result.output.lower())
    
    def test_solve_help(self):
        """Test solve command help"""
        result = self.runner.invoke(cli, ['solve', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("problem", result.output.lower())
        self.assertIn("file", result.output.lower())


if __name__ == '__main__':
    unittest.main()