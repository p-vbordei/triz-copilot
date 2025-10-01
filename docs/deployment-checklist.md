# Deployment Checklist - Claude CLI Integration

## Pre-Deployment

### Code Review
- [ ] All 44 tasks completed in specs/002-add-claude-cli/tasks.md
- [ ] Code follows existing TRIZ project patterns
- [ ] No hardcoded paths or credentials
- [ ] All TODOs resolved
- [ ] Logging properly configured

### Testing
- [ ] Unit tests passing: `pytest tests/unit/test_claude_*.py -v`
- [ ] Integration tests passing: `pytest tests/integration/ -v`
- [ ] Contract tests passing
- [ ] Performance tests meet targets (<10s analysis, <500ms lookups)
- [ ] Cross-platform session tests passing
- [ ] No regression in Gemini CLI functionality

### Documentation
- [ ] README.md updated with Claude CLI information
- [ ] docs/claude-cli-guide.md complete
- [ ] API documentation updated
- [ ] Code comments and docstrings complete
- [ ] CLAUDE.md file reviewed

### Dependencies
- [ ] pyproject.toml includes `mcp>=1.15.0` in claude optional group
- [ ] uv.lock updated
- [ ] No version conflicts with existing packages
- [ ] All imports working correctly

## Deployment Steps

### 1. Version Control
```bash
# Ensure on correct branch
git status  # Should show: On branch 002-add-claude-cli

# Check all changes staged
git add -A
git status

# Verify no unintended changes
git diff --cached

# Final commit
git commit -m "feat(claude): Complete Claude CLI integration - All 44 tasks"
```

### 2. Run Full Test Suite
```bash
# Run all tests
pytest tests/ -v --cov=src/claude_tools --cov=src/claude_mcp_server

# Performance benchmarks
pytest tests/performance/ -v

# Verify contract compliance
pytest specs/002-add-claude-cli/contracts/ -v
```

### 3. Build and Install
```bash
# Clean build
rm -rf dist/ build/ *.egg-info

# Install with Claude support
uv sync --extra claude

# Verify installation
python -c "import mcp; print(mcp.__version__)"
python -c "from claude_tools import ClaudeResponseFormatter"
```

### 4. Setup Script Validation
```bash
# Run setup script
./scripts/setup-claude.sh

# Verify configuration created
ls -la ~/.config/claude/mcp/triz-copilot.json

# Verify sessions directory
ls -la ~/.triz/sessions/

# Test MCP server
./test_claude_integration.sh
```

### 5. System Integration Test
```bash
# Check Qdrant (optional)
docker ps | grep qdrant

# Check Ollama (optional)
curl http://localhost:11434/api/tags

# Run health check
python -c "from triz_tools.health_checks import check_system_health; print(check_system_health())"
```

### 6. Manual Testing with Claude

#### Test 1: Workflow Start
```
Open Claude CLI
> Use triz_workflow_start tool

Expected: Session created with ID, Step 1 prompt displayed
```

#### Test 2: Autonomous Solve
```
> Use triz_solve tool with problem: "reduce weight while maintaining strength"

Expected: Complete analysis with contradictions, principles, solutions in <10 seconds
```

#### Test 3: Get Principle
```
> Use triz_get_principle tool with principle_number: 15

Expected: Full principle details with examples and sub-principles
```

#### Test 4: Contradiction Matrix
```
> Use triz_contradiction_matrix tool with improving_parameter: 2, worsening_parameter: 14

Expected: List of recommended principles from matrix
```

#### Test 5: Cross-Platform Session
```
# In Claude
> Use triz_workflow_start
Note the session_id

# In terminal (Gemini CLI or standalone)
python -c "from triz_tools.workflow_tools import triz_workflow_continue; print(triz_workflow_continue('<session_id>', 'my problem'))"

Expected: Session continues seamlessly
```

## Post-Deployment

### Monitoring
- [ ] Monitor logs: `tail -f ~/.triz/logs/claude_mcp_server.log`
- [ ] Check session creation rate
- [ ] Monitor response times
- [ ] Check error rates

### Performance Validation
```bash
# Run performance benchmarks
pytest tests/performance/test_claude_performance.py -v --benchmark-only

# Expected results:
# - Tool registration: <100ms
# - Principle lookup: <500ms
# - Full analysis: <10s
# - Session load/save: <200ms
```

### User Acceptance
- [ ] Test with 3-5 real users
- [ ] Collect feedback on tool usability
- [ ] Verify documentation clarity
- [ ] Test on different platforms (macOS, Linux, Windows)

### Rollback Plan
If issues found:
```bash
# Revert code changes
git revert HEAD

# Stop MCP server
pkill -f claude_mcp_server

# Remove configuration
rm ~/.config/claude/mcp/triz-copilot.json

# Clean sessions
rm -rf ~/.triz/sessions/*

# Reinstall without Claude
uv sync
```

## Post-Deployment Validation

### Week 1
- [ ] No critical bugs reported
- [ ] Performance targets met
- [ ] User feedback positive
- [ ] Documentation sufficient

### Week 2
- [ ] Cross-platform sessions working
- [ ] No data corruption
- [ ] Logging providing useful info
- [ ] Error handling graceful

### Week 4
- [ ] Feature usage metrics collected
- [ ] Performance stable
- [ ] No memory leaks
- [ ] Session management working

## Success Criteria

All must be TRUE to consider deployment successful:

- [ ] All 44 implementation tasks complete
- [ ] All tests passing (100% of critical paths)
- [ ] Response times within targets
  - Principle lookup: <500ms
  - Full analysis: <10s
  - Session operations: <200ms
- [ ] Zero regression in Gemini functionality
- [ ] Documentation complete and accurate
- [ ] User acceptance criteria met
- [ ] Cross-platform sessions validated
- [ ] Health checks passing
- [ ] No critical bugs in first week
- [ ] Positive user feedback (>80% satisfaction)

## Sign-Off

- [ ] **Technical Lead**: Code reviewed and approved
- [ ] **QA**: All tests passing
- [ ] **Documentation**: Docs reviewed and complete
- [ ] **Product**: Features meet requirements
- [ ] **DevOps**: Deployment successful
- [ ] **Support**: Ready to handle user issues

---

## Rollout Strategy

### Phase 1: Internal Testing (Week 1)
- Deploy to dev team only
- Intensive testing and feedback
- Fix any critical issues

### Phase 2: Beta Testing (Week 2)
- Deploy to 10-20 beta users
- Monitor closely
- Gather feedback
- Performance tuning

### Phase 3: General Availability (Week 3)
- Full deployment to all users
- Announcement and documentation
- Support monitoring
- Continuous improvement

## Support Resources

### For Users
- Documentation: docs/claude-cli-guide.md
- Troubleshooting: Section in guide
- Examples: Usage examples in docs
- Health check: `triz_health_check` tool

### For Developers
- Code: src/claude_mcp_server.py, src/claude_tools/
- Tests: tests/unit/test_claude_*, tests/integration/
- Logs: ~/.triz/logs/claude_mcp_server.log
- Configuration: src/config/claude_config.json

### Escalation Path
1. Check logs and health status
2. Review troubleshooting guide
3. Check GitHub issues
4. Contact technical support
5. Escalate to development team

## Maintenance

### Weekly
- Review logs for errors
- Check performance metrics
- Monitor session sizes
- Clean old sessions

### Monthly
- Update dependencies
- Review and optimize performance
- Analyze usage patterns
- Update documentation

### Quarterly
- Major version updates
- Feature enhancements
- Security audits
- User satisfaction surveys
