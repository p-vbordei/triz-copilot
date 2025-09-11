# TRIZ Engineering Co-Pilot - Quickstart Guide

## Prerequisites

Before running the TRIZ Co-Pilot, ensure you have:

1. **Gemini CLI installed** with valid API configuration
2. **Local Qdrant instance running** (Docker container)
3. **Ollama installed** with embedding models
4. **Python dependencies** for TRIZ tools

## Quick Setup

### 1. Start Local Infrastructure
```bash
# Start Qdrant vector database
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Start Ollama service (if not running)
ollama serve

# Pull required embedding model
ollama pull nomic-embed-text
```

### 2. Verify Gemini CLI
```bash
# Test Gemini CLI basic functionality
gemini "Hello, can you help me solve engineering problems?"

# Check for TRIZ commands (after installation)
gemini --help | grep triz
```

## Basic Usage Examples

### Example 1: Guided Workflow Mode (Learning)
**Scenario**: New user wants to learn TRIZ methodology step-by-step

```bash
# Start guided workflow
gemini /triz:workflow "I need to design a bicycle that's lightweight but strong"

# Follow prompts through 6 TRIZ stages:
# 1. Problem Definition
# 2. Function & Contradiction Analysis  
# 3. Parameter Mapping
# 4. Principle Identification
# 5. Solution Generation
# 6. Evaluation
```

**Expected Flow**:
1. System asks for detailed problem description and Ideal Final Result
2. Guides identification of useful/harmful functions
3. Helps formulate technical contradictions
4. Maps contradictions to 39 engineering parameters
5. Identifies relevant TRIZ principles from contradiction matrix
6. Brainstorms solutions using selected principles
7. Evaluates solutions against constraints and IFR

### Example 2: Autonomous Solve Mode (Experienced Users)
**Scenario**: Expert user wants quick TRIZ analysis and solutions

```bash
# Autonomous problem solving
gemini /triz:solve "Reduce aircraft wing weight while maintaining structural strength. Current aluminum design is 20% too heavy for fuel efficiency targets. Must meet FAA certification requirements."
```

**Expected Output**:
```
TRIZ Analysis Report
===================

Problem Summary:
- Technical contradiction between weight reduction and structural strength
- Material optimization challenge in aerospace application
- Regulatory compliance constraint (FAA certification)

Contradictions Identified:
1. Technical: Weight of moving object (#1) vs Strength (#14)
2. Physical: Aluminum properties limit weight/strength optimization

Top Inventive Principles:
- Principle 1 (Segmentation): Divide wing structure into optimized sections
- Principle 15 (Dynamics): Adaptive structural elements
- Principle 40 (Composite materials): Multi-material layered construction

Solution Concepts:
1. Composite Sandwich Structure
   - Description: CFRP skins with honeycomb aluminum core
   - Applied principles: 1, 40
   - Pros: 30% weight reduction, maintained stiffness
   - Cons: Higher manufacturing complexity, cost increase

2. Topology-Optimized Structure  
   - Description: AI-optimized internal structure with selective material removal
   - Applied principles: 1, 15
   - Pros: 25% weight reduction, maintains strength
   - Cons: Complex manufacturing, requires specialized tooling

[Additional solutions...]

Materials Recommendations:
- Carbon Fiber Reinforced Polymer (CFRP): High strength-to-weight ratio
- Aluminum-Lithium Alloy: Lighter than standard aluminum, aerospace certified
- Titanium-Aluminum Intermetallics: Superior strength, expensive

Confidence Score: 0.87
```

### Example 3: Direct Tool Access (Expert Users)
**Scenario**: Expert wants specific TRIZ tool functionality

```bash
# Get specific principle details
gemini /triz:tool get-principle 15

# Query contradiction matrix
gemini /triz:tool contradiction-matrix --improving 1 --worsening 14

# Contextual brainstorming
gemini /triz:tool brainstorm --principle 40 --context "Solar panel efficiency improvement"
```

**Expected Outputs**:

**Principle 15 Details**:
```
TRIZ Principle 15: Dynamics
===========================

Description: Make objects or systems adaptive, allowing them to change their characteristics to be optimal at each stage of operation.

Sub-principles:
a) Adaptive systems that change with operating conditions
b) Divide object into parts that can move relative to each other
c) Increase degree of freedom if object is static

Examples:
- Variable geometry aircraft wings
- Adjustable steering wheels
- Flexible manufacturing systems
- Adaptive suspension systems

Applications: Aerospace, automotive, manufacturing, robotics
Usage Frequency: High
Innovation Level: 3/5
```

**Contradiction Matrix Query**:
```
Contradiction: Improving Weight (#1) vs Worsening Strength (#14)

Recommended Principles:
- Principle 1 (Segmentation): 85% success rate
- Principle 8 (Anti-weight): 78% success rate  
- Principle 15 (Dynamics): 72% success rate
- Principle 40 (Composite materials): 89% success rate

Most Successful Approach: Composite materials + Segmentation
Historical Applications: 247 documented cases
Average Innovation Level: 3.2/5
```

## Validation Tests

### Test 1: Tool Response Time
```bash
# Test tool query performance (should be <2s)
time gemini /triz:tool get-principle 1

# Test autonomous solve performance (should be <10s)  
time gemini /triz:solve "Simple contradiction test problem"
```

### Test 2: Session Continuity
```bash
# Start workflow
gemini /triz:workflow "Test problem for session continuity"

# Continue session (should remember previous context)
gemini /triz:workflow continue

# Reset and verify clean state
gemini /triz:workflow reset
```

### Test 3: Knowledge Base Accuracy
```bash
# Verify principle lookup accuracy
gemini /triz:tool get-principle 1 | grep -i "segmentation"

# Verify contradiction matrix accuracy
gemini /triz:tool contradiction-matrix --improving 1 --worsening 14 | grep -E "Principle [0-9]+"
```

## Troubleshooting

### Common Issues

**Issue**: "No TRIZ commands found"
```bash
# Solution: Verify TOML files exist
ls ~/.gemini/commands/triz/
# Should show: workflow.toml, solve.toml, tool.toml
```

**Issue**: "Qdrant connection failed"
```bash
# Solution: Check Qdrant service
curl http://localhost:6333/health
# Should return: {"status":"ok"}
```

**Issue**: "Embedding model not found"
```bash
# Solution: Check Ollama models
ollama list | grep nomic-embed-text
# If missing: ollama pull nomic-embed-text
```

**Issue**: "Session state corrupted"
```bash
# Solution: Reset session storage
rm -rf ~/.triz_sessions/*
# Or reset specific session
gemini /triz:workflow reset
```

### Performance Optimization

**Slow embedding generation**:
```bash
# Check Ollama optimization settings
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_FLASH_ATTENTION=1
ollama serve
```

**High memory usage**:
```bash
# Use smaller embedding dimensions
# Edit configuration to use 256D vectors instead of 768D
# Expected 1% accuracy loss, 66% memory savings
```

## Success Criteria

The TRIZ Co-Pilot is working correctly if:

1. ✅ **Response Times**: Tool queries <2s, autonomous solve <10s
2. ✅ **Accuracy**: Contradiction matrix returns valid principles (1-40)
3. ✅ **Completeness**: Autonomous solve returns 3-5 solution concepts
4. ✅ **Persistence**: Workflow sessions maintain state across invocations
5. ✅ **Knowledge**: Principle lookup returns detailed, accurate information
6. ✅ **Integration**: Commands work seamlessly within Gemini CLI interface

## Next Steps

After successful quickstart:

1. **Explore Advanced Features**: Function analysis, materials database integration
2. **Customize Knowledge Base**: Add domain-specific TRIZ examples
3. **Performance Tuning**: Optimize vector dimensions for your use cases
4. **Integration**: Connect to CAD tools or engineering databases
5. **Collaboration**: Share TRIZ sessions and results with team members

## Support Resources

- **TRIZ Knowledge Base**: Built-in 40 principles with examples
- **Contradiction Matrix**: Complete 39x39 parameter mapping
- **Materials Database**: 1000+ engineering materials with properties
- **Case Studies**: Historical TRIZ applications and success stories

For additional support, see the full documentation in the `specs/` directory.