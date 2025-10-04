"""
Deep Research Agent for TRIZ Co-Pilot
Performs multi-stage, multi-source research to generate genius-level solutions.
Enhanced with CLI subprocess for 10x research capacity.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import re
import numpy as np

from .services.vector_service import get_vector_service, SearchResult
from .services.embedding_service import get_embedding_service
from .services.cli_executor import get_cli_executor, CLIExecutor
from .services.research_persistence import get_research_persistence, ResearchPersistence
from .knowledge_base import load_principles_from_file, load_contradiction_matrix
from .models import TRIZToolResponse

logger = logging.getLogger(__name__)

# Research configuration - dramatically increased limits when using subprocess
RESEARCH_CONFIG = {
    "with_subprocess": {
        "max_findings": 500,  # 10x increase
        "chunk_size": 16000,  # Full chunks
        "search_limit_per_query": 50,  # 10x increase
        "max_queries": 15,
        "materials_search_limit": 50,  # Increased for comprehensive materials analysis
    },
    "without_subprocess": {
        "max_findings": 50,
        "chunk_size": 2000,
        "search_limit_per_query": 5,
        "max_queries": 10,
        "materials_search_limit": 10,
    },
}


@dataclass
class ResearchQuery:
    """A research query with metadata"""

    query_text: str
    query_type: str  # 'principle', 'material', 'book', 'analogy', 'contradiction'
    priority: float = 1.0
    target_collections: List[str] = field(default_factory=list)


@dataclass
class ResearchFinding:
    """A finding from research"""

    source: str  # Which collection/book
    content: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)


@dataclass
class ResearchReport:
    """Complete research report"""

    problem_statement: str
    research_queries: List[ResearchQuery]
    findings: List[ResearchFinding]
    contradictions: List[Dict[str, Any]]
    principles: List[Dict[str, Any]]
    cross_domain_analogies: List[Dict[str, Any]]
    solutions: List[Dict[str, Any]]
    confidence_score: float
    knowledge_gaps: List[str] = field(default_factory=list)


class DeepResearchAgent:
    """
    Genius-level research agent that performs multi-stage research
    across all knowledge sources to generate deeply informed solutions.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the research agent.

        Args:
            session_id: Session ID for research persistence (auto-generated if None)
        """
        self.vector_service = get_vector_service()
        self.embedding_service = get_embedding_service()
        self.principles = load_principles_from_file()
        self.matrix = load_contradiction_matrix()

        # CLI executor for subprocess-based analysis
        self.cli_executor = get_cli_executor()
        self.use_subprocess = self.cli_executor.is_available()

        # Research persistence - saves all findings to disk
        self.persistence = get_research_persistence(session_id=session_id, reset=True)

        # Select configuration based on subprocess availability
        config_key = "with_subprocess" if self.use_subprocess else "without_subprocess"
        self.config = RESEARCH_CONFIG[config_key]

        # Available collections for search
        self.collections = {
            "principles": "triz_principles",
            "books_general": "triz_documents",
            "materials": "materials_database",
            "materials_books": "materials_knowledge",  # Deep materials science from books
            "contradictions": "triz_contradictions",
        }

        logger.info(
            f"DeepResearchAgent initialized "
            f"(subprocess: {self.use_subprocess}, "
            f"max_findings: {self.config['max_findings']}, "
            f"session: {self.persistence.session_id})"
        )

    def research_problem(self, problem_description: str) -> ResearchReport:
        """
        Main research orchestrator - performs deep multi-stage research.
        NOW SAVES ALL FINDINGS TO DISK FOR CONTEXT RECOVERY.

        Args:
            problem_description: User's problem description

        Returns:
            Comprehensive research report
        """
        logger.info(f"Starting deep research for: {problem_description[:100]}...")

        # Save problem statement to persistence
        self.persistence.set_problem(problem_description)

        # Stage 1: Problem Understanding
        research_plan = self._generate_research_plan(problem_description)
        logger.info(f"Generated {len(research_plan)} research queries")

        # Save research queries to persistence
        for query in research_plan:
            self.persistence.save_research_query(
                {
                    "query_text": query.query_text,
                    "query_type": query.query_type,
                    "priority": query.priority,
                    "target_collections": query.target_collections,
                }
            )

        # Stage 2: Multi-Source Parallel Search
        findings = self._multi_source_search(research_plan, problem_description)
        logger.info(f"Collected {len(findings)} research findings")

        # SAVE FINDINGS TO DISK (batch save for performance)
        self.persistence.save_findings_batch(
            [
                {
                    "source": f.source,
                    "content": str(f.content)[:16000],  # Truncate at chunk size
                    "relevance_score": f.relevance_score,
                    "metadata": f.metadata,
                    "citations": f.citations,
                }
                for f in findings
            ]
        )

        # Stage 2.5: Deep Material Analysis (if materials problem detected)
        if self._is_materials_problem(problem_description):
            logger.info(
                "Materials problem detected - performing deep materials analysis..."
            )
            materials_analysis = self._deep_materials_analysis(
                problem_description, findings
            )
            # Add materials analysis as enriched findings
            for material_finding in materials_analysis:
                findings.append(material_finding)
            logger.info(f"Added {len(materials_analysis)} deep materials findings")

        # Stage 3: Contradiction Deep Dive
        contradictions = self._deep_contradiction_analysis(
            problem_description, findings
        )
        logger.info(f"Identified {len(contradictions)} contradictions")

        # Stage 4: Principle Discovery (semantic, not just matrix)
        principles = self._semantic_principle_discovery(
            problem_description, contradictions, findings
        )
        logger.info(f"Discovered {len(principles)} relevant principles")

        # Stage 5: Cross-Domain Analogy Search
        analogies = self._find_cross_domain_analogies(problem_description, findings)
        logger.info(f"Found {len(analogies)} cross-domain analogies")

        # Stage 6: Gap Detection
        gaps = self._detect_knowledge_gaps(findings, principles)

        # Stage 7: Recursive Deep Dive (if gaps found)
        if gaps and len(findings) < 20:
            logger.info(f"Detected {len(gaps)} knowledge gaps, performing deep dive...")
            additional_findings = self._recursive_deep_dive(gaps, problem_description)
            findings.extend(additional_findings)

        # Stage 8: Solution Synthesis
        solutions = self._synthesize_solutions(
            problem_description, findings, principles, contradictions, analogies
        )
        logger.info(f"Synthesized {len(solutions)} solutions")

        # Stage 9: Calculate Confidence
        confidence = self._calculate_confidence(findings, principles, solutions)

        # SAVE RESEARCH SUMMARY TO DISK
        self.persistence.save_research_summary(
            contradictions=contradictions,
            principles=principles,
            solutions=solutions,
            confidence_score=confidence,
            knowledge_gaps=gaps,
        )

        # Create comprehensive report
        report = ResearchReport(
            problem_statement=problem_description,
            research_queries=research_plan,
            findings=findings,
            contradictions=contradictions,
            principles=principles,
            cross_domain_analogies=analogies,
            solutions=solutions,
            confidence_score=confidence,
            knowledge_gaps=gaps,
        )

        # CREATE RECOVERY FILE for easy access
        recovery_file = self.persistence.create_recovery_file()
        logger.info(f"Research complete. Confidence: {confidence:.2f}")
        logger.info(f"📁 Research saved to: {self.persistence.get_session_path()}")
        logger.info(f"📄 Recovery file: {recovery_file}")

        # Print stats
        stats = self.persistence.get_research_stats()
        logger.info(
            f"📊 Stats: {stats['total_findings']} findings, "
            f"{stats['total_subprocess_calls']} subprocess calls, "
            f"{stats['unique_sources']} unique sources"
        )

        return report

    def _generate_research_plan(self, problem: str) -> List[ResearchQuery]:
        """
        Generate multiple research queries from the problem.
        Expands 1 problem into 10-15 targeted research queries.
        """
        queries = []

        # Extract key concepts using simple NLP
        problem_lower = problem.lower()

        # Query 0: HIGHEST PRIORITY - Search TRIZ principles directly (we have this data!)
        queries.append(
            ResearchQuery(
                query_text=problem,
                query_type="principle",
                priority=2.5,
                target_collections=["triz_principles"],
            )
        )

        # Query 1: Direct problem search in books (if available)
        queries.append(
            ResearchQuery(
                query_text=problem,
                query_type="book",
                priority=0.8,
                target_collections=["triz_documents"],
            )
        )

        # Query 2: Extract contradictions and search for them
        contradiction_patterns = [
            (r"(\w+(?:\s+\w+)*)\s+(?:while|but|versus|vs)\s+(\w+(?:\s+\w+)*)", 2),
            (r"increase\s+(\w+)", 1.5),
            (r"reduce\s+(\w+)", 1.5),
            (r"improve\s+(\w+)", 1.5),
        ]

        for pattern, priority in contradiction_patterns:
            matches = re.findall(pattern, problem_lower)
            for match in matches[:2]:  # Limit to 2 per pattern
                if isinstance(match, tuple):
                    query_text = f"{match[0]} contradiction resolution"
                else:
                    query_text = f"{match} optimization methods"

                queries.append(
                    ResearchQuery(
                        query_text=query_text,
                        query_type="contradiction",
                        priority=priority,
                        target_collections=["triz_principles", "triz_contradictions"],
                    )
                )

        # Query 3: Search for TRIZ principles semantically with specific keywords
        queries.append(
            ResearchQuery(
                query_text=f"inventive principles for solving {problem[:100]}",
                query_type="principle",
                priority=2.0,
                target_collections=["triz_principles"],
            )
        )

        # Query 4: Domain-specific search
        domains = self._extract_domains(problem)
        for domain in domains[:2]:
            queries.append(
                ResearchQuery(
                    query_text=f"{domain} {problem[:50]}",
                    query_type="book",
                    priority=1.5,
                    target_collections=["triz_documents"],
                )
            )

        # Query 5: Materials search if relevant (HIGH PRIORITY - we have real data!)
        if any(
            word in problem_lower
            for word in [
                "material",
                "weight",
                "strength",
                "property",
                "component",
                "part",
                "structure",
            ]
        ):
            # Search database for quick properties
            queries.append(
                ResearchQuery(
                    query_text=problem,
                    query_type="material",
                    priority=2.2,
                    target_collections=["materials_database"],
                )
            )

            # COMPREHENSIVE MATERIAL SEARCHES - Multiple specific queries to find examples

            # 5a. General material selection for the problem
            queries.append(
                ResearchQuery(
                    query_text=f"material selection criteria properties {problem[:100]}",
                    query_type="material",
                    priority=2.4,
                    target_collections=["materials_knowledge"],
                )
            )

            # 5b. Lightweight materials and weight reduction
            if any(
                word in problem_lower for word in ["light", "weight", "heavy", "mass"]
            ):
                queries.append(
                    ResearchQuery(
                        query_text="lightweight materials weight reduction aluminum magnesium titanium composite density comparison",
                        query_type="material",
                        priority=2.5,
                        target_collections=["materials_knowledge"],
                    )
                )
                queries.append(
                    ResearchQuery(
                        query_text="weight savings structural materials aerospace automotive applications",
                        query_type="material",
                        priority=2.3,
                        target_collections=["materials_knowledge"],
                    )
                )

            # 5c. Formability and bending
            if any(
                word in problem_lower
                for word in ["bend", "form", "shape", "flexible", "sheet"]
            ):
                queries.append(
                    ResearchQuery(
                        query_text="sheet metal forming bending formability ductility aluminum alloys",
                        query_type="material",
                        priority=2.5,
                        target_collections=["materials_knowledge"],
                    )
                )
                queries.append(
                    ResearchQuery(
                        query_text="thermoforming bendable materials plastic metal composite manufacturing",
                        query_type="material",
                        priority=2.3,
                        target_collections=["materials_knowledge"],
                    )
                )

            # 5d. Specific material comparisons
            if any(
                word in problem_lower
                for word in ["aluminum", "aluminium", "alternative"]
            ):
                queries.append(
                    ResearchQuery(
                        query_text="aluminum alloys magnesium titanium comparison properties strength weight",
                        query_type="material",
                        priority=2.6,
                        target_collections=["materials_knowledge"],
                    )
                )

            # 5e. Composite materials
            if any(
                word in problem_lower
                for word in ["composite", "cfrp", "carbon", "fiber", "fibre"]
            ):
                queries.append(
                    ResearchQuery(
                        query_text="composite materials carbon fiber CFRP properties applications manufacturing",
                        query_type="material",
                        priority=2.5,
                        target_collections=["materials_knowledge"],
                    )
                )
                queries.append(
                    ResearchQuery(
                        query_text="thermoplastic composites glass fiber reinforced polymer lightweight",
                        query_type="material",
                        priority=2.3,
                        target_collections=["materials_knowledge"],
                    )
                )

            # 5f. Application-specific searches
            if any(
                word in problem_lower
                for word in ["robot", "electronic", "enclosure", "housing"]
            ):
                queries.append(
                    ResearchQuery(
                        query_text="materials electronics enclosure robotics structural components shielding",
                        query_type="material",
                        priority=2.4,
                        target_collections=["materials_knowledge"],
                    )
                )

            # 5g. Case studies and examples
            queries.append(
                ResearchQuery(
                    query_text="material selection case study example application design criteria",
                    query_type="material",
                    priority=2.2,
                    target_collections=["materials_knowledge"],
                )
            )

        # Query 6: Cross-domain analogies
        queries.append(
            ResearchQuery(
                query_text=f"analogous problems {problem[:50]}",
                query_type="analogy",
                priority=1.3,
                target_collections=["triz_documents"],
            )
        )

        # Query 7: Solution examples
        queries.append(
            ResearchQuery(
                query_text=f"solutions examples {problem[:50]}",
                query_type="book",
                priority=1.4,
                target_collections=["triz_documents"],
            )
        )

        # Sort by priority
        queries.sort(key=lambda q: q.priority, reverse=True)

        return queries[: self.config["max_queries"]]

    def _multi_source_search(
        self, research_plan: List[ResearchQuery], problem: str
    ) -> List[ResearchFinding]:
        """
        Execute multiple searches across different collections in parallel.
        Enhanced with dynamic limits based on subprocess availability.
        """
        findings = []

        # Check if vector service is available
        if not self.vector_service.is_available():
            logger.warning("Vector service not available, using fallback")
            return self._fallback_research(problem)

        # Execute each query (increased limit when using subprocess)
        max_queries = self.config["max_queries"]
        for query in research_plan[:max_queries]:
            try:
                # Generate embedding for query
                query_embedding = self.embedding_service.generate_embedding(
                    query.query_text
                )

                if query_embedding is None:
                    continue

                # Search target collections
                for collection in query.target_collections:
                    if collection not in self.collections.values():
                        continue

                    # Use dynamic limits based on configuration
                    if collection == "materials_knowledge":
                        search_limit = self.config["materials_search_limit"]
                    else:
                        search_limit = self.config["search_limit_per_query"]

                    results = self.vector_service.search(
                        collection_name=collection,
                        query_vector=query_embedding,
                        limit=search_limit,
                        score_threshold=0.0,  # No threshold - return top results
                    )

                    # Convert results to findings
                    for result in results:
                        # Extract content - try different field names
                        # For triz_principles, keep the dict structure
                        if collection == "triz_principles":
                            content = result.payload
                        else:
                            content = (
                                result.payload.get("full_content")
                                or result.payload.get("content")
                                or result.payload.get("chunk_text")
                                or str(result.payload)
                            )

                        finding = ResearchFinding(
                            source=f"{collection} ({result.payload.get('document_name', 'N/A')})",
                            content=content,
                            relevance_score=result.score * query.priority,
                            metadata=result.payload,
                            citations=[f"{collection}:{result.id}"],
                        )
                        findings.append(finding)

            except Exception as e:
                logger.warning(
                    f"Search failed for query '{query.query_text}': {str(e)}"
                )
                continue

        # Sort by relevance
        findings.sort(key=lambda f: f.relevance_score, reverse=True)

        # Return findings based on configuration (50 or 500)
        max_findings = self.config["max_findings"]
        logger.info(f"Returning top {max_findings} findings from {len(findings)} total")
        return findings[:max_findings]

    def _deep_contradiction_analysis(
        self, problem: str, findings: List[ResearchFinding]
    ) -> List[Dict[str, Any]]:
        """
        Deep analysis of contradictions using both pattern matching
        and findings from books.
        """
        contradictions = []
        seen = set()

        # Pattern-based extraction (existing method)
        patterns = [
            r"(\w+(?:\s+\w+)*)\s+while\s+(\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*)\s+but\s+not\s+(\w+(?:\s+\w+)*)",
            r"increase\s+(\w+(?:\s+\w+)*)\s+(?:reduce|decrease)\s+(\w+(?:\s+\w+)*)",
        ]

        problem_lower = problem.lower()

        for pattern in patterns:
            matches = re.findall(pattern, problem_lower)
            for match in matches:
                if len(match) >= 2:
                    contradiction_key = f"{match[0]}_{match[1]}"
                    if contradiction_key not in seen:
                        seen.add(contradiction_key)
                        contradictions.append(
                            {
                                "type": "technical",
                                "improving": match[0],
                                "worsening": match[1],
                                "description": f"Need to improve {match[0]} while managing {match[1]}",
                                "source": "problem_statement",
                            }
                        )

        # Extract contradictions from findings
        for finding in findings[:10]:
            content_lower = str(finding.content).lower()
            for pattern in patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches:
                    if len(match) >= 2:
                        contradiction_key = f"{match[0]}_{match[1]}"
                        if contradiction_key not in seen:
                            seen.add(contradiction_key)
                            contradictions.append(
                                {
                                    "type": "discovered",
                                    "improving": match[0],
                                    "worsening": match[1],
                                    "description": f"Improve {match[0]} vs {match[1]}",
                                    "source": finding.source,
                                }
                            )

        return contradictions[:10]  # Top 10 contradictions

    def _semantic_principle_discovery(
        self,
        problem: str,
        contradictions: List[Dict[str, Any]],
        findings: List[ResearchFinding],
    ) -> List[Dict[str, Any]]:
        """
        Discover relevant TRIZ principles using semantic search,
        not just contradiction matrix lookup.
        """
        principles_map = {}

        # 1. Matrix-based principles (existing method)
        for contradiction in contradictions[:5]:
            # Try to map to parameters (simplified)
            imp_params = self._text_to_parameters(contradiction.get("improving", ""))
            wor_params = self._text_to_parameters(contradiction.get("worsening", ""))

            for imp in imp_params[:1]:
                for wor in wor_params[:1]:
                    result = self.matrix.lookup(imp, wor)
                    if result:
                        for p_id in result.recommended_principles:
                            if p_id not in principles_map:
                                principles_map[p_id] = {"score": 0, "sources": []}
                            principles_map[p_id]["score"] += 1.0
                            principles_map[p_id]["sources"].append(
                                "contradiction_matrix"
                            )

        # 2. Semantic search through principles
        if self.vector_service.is_available():
            try:
                query_embedding = self.embedding_service.generate_embedding(problem)
                if query_embedding is not None:
                    results = self.vector_service.search(
                        collection_name="triz_principles",
                        query_vector=query_embedding,
                        limit=10,
                        score_threshold=0.0,  # No threshold - return top results
                    )

                    for result in results:
                        p_id = result.payload.get(
                            "principle_id", result.payload.get("principle_number")
                        )
                        if p_id and p_id not in principles_map:
                            principles_map[p_id] = {"score": 0, "sources": []}
                        if p_id:
                            principles_map[p_id]["score"] += (
                                result.score * 1.5
                            )  # Weight semantic search higher
                            principles_map[p_id]["sources"].append("semantic_search")
            except Exception as e:
                logger.warning(f"Semantic principle search failed: {str(e)}")

        # 3. Extract principles mentioned in findings
        for finding in findings[:15]:
            # If content is a dict from triz_principles collection, extract principle_number directly
            if isinstance(finding.content, dict):
                p_id = finding.content.get("principle_number") or finding.content.get(
                    "principle_id"
                )
                if p_id and 1 <= p_id <= 40:
                    if p_id not in principles_map:
                        principles_map[p_id] = {"score": 0, "sources": []}
                    principles_map[p_id]["score"] += (
                        2.0  # High score for direct principle findings
                    )
                    principles_map[p_id]["sources"].append(
                        f"direct_from_{finding.source}"
                    )
            else:
                # Look for principle numbers mentioned in text
                content_str = str(finding.content).lower()
                principle_mentions = re.findall(r"principle\s+(\d+)", content_str)
                for p_id_str in principle_mentions:
                    try:
                        p_id = int(p_id_str)
                        if 1 <= p_id <= 40:
                            if p_id not in principles_map:
                                principles_map[p_id] = {"score": 0, "sources": []}
                            principles_map[p_id]["score"] += 0.8
                            principles_map[p_id]["sources"].append(
                                f"mentioned_in_{finding.source}"
                            )
                    except:
                        pass

        # Build final list with full details
        principles_list = []
        for p_id, data in principles_map.items():
            principle = self.principles.get_principle(p_id)
            if principle:
                principles_list.append(
                    {
                        "id": p_id,
                        "name": principle.principle_name,
                        "description": principle.description,
                        "score": data["score"],
                        "sources": data["sources"],
                        "sub_principles": principle.sub_principles,
                        "examples": principle.examples[:3],
                        "domains": principle.domains,
                        "usage_frequency": principle.usage_frequency,
                        "innovation_level": principle.innovation_level,
                    }
                )

        # Sort by score
        principles_list.sort(key=lambda p: p["score"], reverse=True)

        return principles_list[:10]  # Top 10 principles

    def _find_cross_domain_analogies(
        self, problem: str, findings: List[ResearchFinding]
    ) -> List[Dict[str, Any]]:
        """
        Find analogous solutions from other domains.
        """
        analogies = []

        # Extract domain from problem
        problem_domain = self._extract_domains(problem)

        # Search for similar patterns in other domains
        other_domains = [
            "nature",
            "automotive",
            "aerospace",
            "medical",
            "construction",
            "electronics",
        ]
        search_domains = [d for d in other_domains if d not in problem_domain]

        if self.vector_service.is_available():
            for domain in search_domains[:3]:
                try:
                    query_text = f"{domain} solutions for {problem[:50]}"
                    query_embedding = self.embedding_service.generate_embedding(
                        query_text
                    )

                    if query_embedding is not None:
                        results = self.vector_service.search(
                            collection_name="triz_documents",
                            query_vector=query_embedding,
                            limit=3,
                            score_threshold=0.0,  # No threshold - return top results
                        )

                        for result in results:
                            analogies.append(
                                {
                                    "source_domain": domain,
                                    "target_domain": problem_domain[0]
                                    if problem_domain
                                    else "general",
                                    "description": result.payload.get("chunk_text", "")[
                                        :200
                                    ],
                                    "relevance_score": result.score,
                                    "source_reference": result.payload.get(
                                        "document_name", "Unknown"
                                    ),
                                }
                            )
                except Exception as e:
                    logger.debug(f"Analogy search failed for {domain}: {str(e)}")
                    continue

        return analogies[:5]  # Top 5 analogies

    def _detect_knowledge_gaps(
        self, findings: List[ResearchFinding], principles: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detect what information is still missing.
        """
        gaps = []

        # Check if we have enough findings
        if len(findings) < 5:
            gaps.append("Insufficient background research - need more sources")

        # Check if we have principle coverage
        if len(principles) < 3:
            gaps.append("Limited principle coverage - need more TRIZ insights")

        # Check for specific types of information
        has_material_info = any(
            "material" in str(f.content).lower() for f in findings[:10]
        )
        has_implementation_info = any(
            "implement" in str(f.content).lower() for f in findings[:10]
        )
        has_case_studies = any(
            "case" in str(f.content).lower() or "example" in str(f.content).lower()
            for f in findings[:10]
        )

        if not has_material_info:
            gaps.append("Missing materials information")

        if not has_implementation_info:
            gaps.append("Missing implementation guidance")

        if not has_case_studies:
            gaps.append("Missing case studies and examples")

        return gaps

    def _recursive_deep_dive(
        self, gaps: List[str], original_problem: str
    ) -> List[ResearchFinding]:
        """
        Perform recursive search to fill knowledge gaps.
        """
        additional_findings = []

        # Generate queries to fill gaps
        gap_queries = []
        for gap in gaps[:3]:  # Limit to top 3 gaps
            if "material" in gap.lower():
                gap_queries.append(f"materials specifications {original_problem[:30]}")
            elif "implementation" in gap.lower():
                gap_queries.append(f"implementation steps {original_problem[:30]}")
            elif "case" in gap.lower():
                gap_queries.append(f"case studies examples {original_problem[:30]}")
            elif "principle" in gap.lower():
                gap_queries.append(f"TRIZ principles detailed {original_problem[:30]}")

        # Execute gap-filling searches
        for query_text in gap_queries:
            try:
                query_embedding = self.embedding_service.generate_embedding(query_text)
                if query_embedding is None:
                    continue

                results = self.vector_service.search(
                    collection_name="triz_documents",
                    query_vector=query_embedding,
                    limit=3,
                    score_threshold=0.0,  # No threshold - return top results
                )

                for result in results:
                    finding = ResearchFinding(
                        source=f"gap_filling_{result.payload.get('document_name', 'N/A')}",
                        content=result.payload.get("chunk_text", "")[:500],
                        relevance_score=result.score,
                        metadata=result.payload,
                        citations=[f"deep_dive:{result.id}"],
                    )
                    additional_findings.append(finding)
            except Exception as e:
                logger.debug(f"Gap-filling search failed for '{query_text}': {str(e)}")
                continue

        return additional_findings

    def _synthesize_solutions(
        self,
        problem: str,
        findings: List[ResearchFinding],
        principles: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]],
        analogies: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Synthesize solutions from all research findings.
        NOT template-based - creates deeply researched solutions.
        """
        solutions = []

        # Solution 1-3: Based on top principles with research support
        for i, principle in enumerate(principles[:3]):
            # Find relevant findings for this principle
            principle_findings = [
                f
                for f in findings
                if str(principle["id"]) in str(f.content)
                or principle["name"].lower() in str(f.content).lower()
            ]

            # Find relevant analogies
            principle_analogies = [
                a
                for a in analogies
                if principle["name"].lower() in a["description"].lower()
            ][:2]

            solution = {
                "title": f"{principle['name']}-Based Solution",
                "description": self._generate_research_based_description(
                    principle, principle_findings[:3], problem
                ),
                "applied_principles": [principle["id"]],
                "principle_names": [principle["name"]],
                "research_support": [
                    {
                        "source": f.source,
                        "excerpt": str(f.content)[:5000],
                        "relevance": f.relevance_score,
                    }
                    for f in principle_findings[:3]
                ],
                "cross_domain_insights": [
                    {"domain": a["source_domain"], "insight": a["description"][:100]}
                    for a in principle_analogies
                ],
                "pros": self._extract_pros_from_research(principle_findings),
                "cons": self._extract_cons_from_research(principle_findings),
                "feasibility_score": 0.7 + (0.05 * (3 - i)),
                "confidence": min(
                    1.0, principle["score"] / 3.0 + len(principle_findings) * 0.1
                ),
                "implementation_hints": self._extract_implementation_hints(
                    principle_findings
                ),
                "citations": [f.source for f in principle_findings[:5]],
            }

            solutions.append(solution)

        # Solution 4: Hybrid solution combining top 2 principles
        if len(principles) >= 2:
            hybrid_findings = findings[:5]  # Use top general findings

            solution = {
                "title": f"Hybrid: {principles[0]['name']} + {principles[1]['name']}",
                "description": f"Synthesized approach combining {principles[0]['name']} and {principles[1]['name']}. "
                f"{principles[0]['description'][:100]}... integrated with {principles[1]['description'][:100]}...",
                "applied_principles": [principles[0]["id"], principles[1]["id"]],
                "principle_names": [principles[0]["name"], principles[1]["name"]],
                "research_support": [
                    {
                        "source": f.source,
                        "excerpt": str(f.content)[:5000],
                        "relevance": f.relevance_score,
                    }
                    for f in hybrid_findings
                ],
                "cross_domain_insights": [a for a in analogies[:2]],
                "pros": [
                    "Addresses multiple contradictions simultaneously",
                    "Synergistic effects from principle combination",
                    "Supported by multiple research sources",
                ],
                "cons": [
                    "Higher implementation complexity",
                    "Requires careful integration",
                    "May need more resources",
                ],
                "feasibility_score": 0.65,
                "confidence": min(
                    1.0, (principles[0]["score"] + principles[1]["score"]) / 6.0
                ),
                "implementation_hints": self._extract_implementation_hints(
                    hybrid_findings
                ),
                "citations": [f.source for f in hybrid_findings],
            }

            solutions.append(solution)

        # Solution 5: Analogy-based solution (if we have good analogies)
        if analogies:
            best_analogy = analogies[0]

            solution = {
                "title": f"Cross-Domain Solution from {best_analogy['source_domain'].title()}",
                "description": f"Adapted from successful approaches in {best_analogy['source_domain']}: "
                f"{best_analogy['description']}",
                "applied_principles": [p["id"] for p in principles[:2]],
                "principle_names": [p["name"] for p in principles[:2]],
                "research_support": [
                    {
                        "source": best_analogy["source_reference"],
                        "excerpt": best_analogy["description"][:150],
                        "relevance": best_analogy["relevance_score"],
                    }
                ],
                "cross_domain_insights": analogies[:3],
                "pros": [
                    "Proven in another domain",
                    "Novel cross-domain transfer",
                    "Lower risk due to existing validation",
                ],
                "cons": [
                    "May need adaptation to current domain",
                    "Domain differences could introduce challenges",
                ],
                "feasibility_score": 0.7,
                "confidence": best_analogy["relevance_score"],
                "implementation_hints": [
                    f"Study {best_analogy['source_domain']} implementations"
                ],
                "citations": [best_analogy["source_reference"]],
            }

            solutions.append(solution)

        return solutions

    def _generate_research_based_description(
        self, principle: Dict[str, Any], findings: List[ResearchFinding], problem: str
    ) -> str:
        """Generate solution description based on research findings"""
        desc = f"Apply {principle['name']} principle to {problem[:80]}. "

        # Add principle description
        desc += f"{principle['description']} "

        # Add insights from research
        if findings:
            desc += f"\n\nResearch insights: "
            for finding in findings[:2]:
                content_str = str(finding.content)
                excerpt = content_str[:5000].strip()
                desc += f"\n- From {finding.source}: {excerpt}... "

        # Add sub-principle details
        if principle.get("sub_principles"):
            desc += f"\n\nSpecific approaches: {principle['sub_principles'][0]}"

        return desc

    def _extract_pros_from_research(self, findings: List[ResearchFinding]) -> List[str]:
        """Extract pros from research findings"""
        pros = []

        for finding in findings[:3]:
            content_str = str(finding.content)
            content_lower = content_str.lower()

            # Look for positive indicators
            if any(
                word in content_lower
                for word in ["benefit", "advantage", "improve", "effective"]
            ):
                # Extract sentence containing these words
                sentences = content_str.split(".")
                for sentence in sentences:
                    if any(
                        word in sentence.lower() for word in ["benefit", "advantage"]
                    ):
                        pros.append(sentence.strip()[:100])
                        break

        if not pros:
            pros = [
                "Supported by research findings",
                "Based on proven TRIZ methodology",
                "Applicable to problem domain",
            ]

        return pros[:4]

    def _extract_cons_from_research(self, findings: List[ResearchFinding]) -> List[str]:
        """Extract cons from research findings"""
        cons = []

        for finding in findings[:3]:
            content_str = str(finding.content)
            content_lower = content_str.lower()

            # Look for challenges/limitations
            if any(
                word in content_lower
                for word in ["challenge", "limitation", "difficult", "risk"]
            ):
                sentences = content_str.split(".")
                for sentence in sentences:
                    if any(
                        word in sentence.lower() for word in ["challenge", "limitation"]
                    ):
                        cons.append(sentence.strip()[:100])
                        break

        if not cons:
            cons = [
                "May require initial investment",
                "Implementation complexity needs assessment",
                "Domain-specific validation recommended",
            ]

        return cons[:4]

    def _extract_implementation_hints(
        self, findings: List[ResearchFinding]
    ) -> List[str]:
        """Extract implementation hints from findings"""
        hints = []

        for finding in findings[:5]:
            content_str = str(finding.content)
            content_lower = content_str.lower()

            # Look for implementation guidance
            if any(
                word in content_lower
                for word in ["implement", "step", "process", "method"]
            ):
                sentences = content_str.split(".")
                for sentence in sentences:
                    if any(
                        word in sentence.lower()
                        for word in ["implement", "step", "first"]
                    ):
                        hints.append(sentence.strip()[:120])
                        break

        if not hints:
            hints = [
                "Start with feasibility analysis",
                "Create prototype for testing",
                "Validate with domain experts",
            ]

        return hints[:5]

    def _calculate_confidence(
        self,
        findings: List[ResearchFinding],
        principles: List[Dict[str, Any]],
        solutions: List[Dict[str, Any]],
    ) -> float:
        """Calculate overall confidence score based on research depth"""
        confidence = 0.5  # Base confidence

        # Boost for number of findings
        confidence += min(0.2, len(findings) * 0.01)

        # Boost for number of principles
        confidence += min(0.15, len(principles) * 0.03)

        # Boost for solution quality
        if solutions:
            avg_solution_confidence = sum(
                s.get("confidence", 0.5) for s in solutions
            ) / len(solutions)
            confidence += avg_solution_confidence * 0.2

        # Boost for source diversity
        unique_sources = len(set(f.source for f in findings))
        confidence += min(0.15, unique_sources * 0.02)

        return min(1.0, confidence)

    def _fallback_research(self, problem: str) -> List[ResearchFinding]:
        """Fallback research when vector service is unavailable"""
        # Use file-based search or direct principle lookup
        findings = []

        # Add principles as findings
        for i, principle in enumerate(self.principles.principles.values()):
            if i >= 10:  # Limit to 10
                break

            finding = ResearchFinding(
                source=f"TRIZ Principle {principle.principle_id}",
                content=f"{principle.principle_name}: {principle.description}",
                relevance_score=0.5,
                metadata={"principle_id": principle.principle_id},
            )
            findings.append(finding)

        return findings

    def _text_to_parameters(self, text: str) -> List[int]:
        """Convert text to TRIZ parameter numbers (simplified)"""
        # Simple keyword mapping
        param_keywords = {
            1: ["weight", "mass"],
            11: ["strength", "strong"],
            18: ["energy", "power"],
            29: ["productivity", "efficiency"],
        }

        text_lower = text.lower()
        params = []

        for param_id, keywords in param_keywords.items():
            if any(kw in text_lower for kw in keywords):
                params.append(param_id)

        return params if params else [1]  # Default to weight

    def _extract_domains(self, text: str) -> List[str]:
        """Extract relevant domains from text"""
        domains = []
        text_lower = text.lower()

        domain_keywords = {
            "aerospace": ["aircraft", "wing", "flight", "aviation"],
            "automotive": ["car", "vehicle", "engine", "automotive"],
            "medical": ["medical", "health", "patient", "clinical"],
            "manufacturing": ["production", "factory", "assembly", "manufacturing"],
            "electronics": ["electronic", "circuit", "sensor", "chip"],
            "construction": ["building", "construction", "structural", "architecture"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in text_lower for kw in keywords):
                domains.append(domain)

        return domains if domains else ["general"]

    def _is_materials_problem(self, problem: str) -> bool:
        """Detect if this is a materials selection/properties problem"""
        materials_keywords = [
            "material",
            "metal",
            "alloy",
            "composite",
            "polymer",
            "plastic",
            "aluminum",
            "aluminium",
            "steel",
            "titanium",
            "magnesium",
            "carbon fiber",
            "cfrp",
            "weight",
            "density",
            "strength",
            "formability",
            "bendable",
            "lightweight",
            "properties",
            "sheet",
            "component",
        ]
        problem_lower = problem.lower()
        keyword_count = sum(1 for kw in materials_keywords if kw in problem_lower)
        return keyword_count >= 3  # If 3+ materials keywords, it's a materials problem

    def _deep_materials_analysis(
        self, problem: str, initial_findings: List[ResearchFinding]
    ) -> List[ResearchFinding]:
        """
        Perform deep analysis of materials from books.
        Enhanced with CLI subprocess for comprehensive analysis.

        This goes beyond semantic search to actually READ and ANALYZE
        the book content about materials.
        """
        deep_findings = []

        # Extract materials mentioned in initial findings
        materials_findings = [
            f
            for f in initial_findings
            if "materials" in f.source.lower() or "composite" in f.source.lower()
        ]

        if not materials_findings:
            logger.warning("No materials findings to analyze deeply")
            return []

        # Use subprocess for deep analysis if available
        if self.use_subprocess and len(materials_findings) > 5:
            logger.info(
                f"Using CLI subprocess to analyze {len(materials_findings)} materials findings..."
            )
            return self._subprocess_materials_analysis(materials_findings, problem)

        # Fallback: regex-based analysis (original method)
        logger.info(f"Deep analyzing {len(materials_findings)} materials findings...")

        # Extract specific materials, properties, and comparisons from content
        analysis_limit = 10 if not self.use_subprocess else 50
        for finding in materials_findings[:analysis_limit]:
            content = str(finding.content)

            # Extract material names mentioned
            material_patterns = [
                r"(?:aluminum|aluminium|magnesium|titanium|steel|carbon fiber|CFRP|polymer|composite|alloy)\s+(?:alloy|sheet|composite)?",
                r"(?:AZ31|6061|7075|Ti-6Al-4V|CFRP|GFRP)",
            ]

            materials_found = []
            for pattern in material_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                materials_found.extend(matches)

            # Extract density/weight information
            density_pattern = r"density.*?(\d+\.?\d*)\s*(?:g/cm|kg/m)"
            densities = re.findall(density_pattern, content, re.IGNORECASE)

            # Extract strength/modulus information
            strength_pattern = (
                r"(?:strength|modulus|stiffness).*?(\d+\.?\d*)\s*(?:MPa|GPa)"
            )
            strengths = re.findall(strength_pattern, content, re.IGNORECASE)

            # Create enriched finding with extracted data
            if materials_found or densities or strengths:
                analysis_content = f"DEEP MATERIALS ANALYSIS:\n\n"
                analysis_content += f"Source: {finding.source}\n\n"

                if materials_found:
                    unique_materials = list(
                        set([m.strip() for m in materials_found[:5]])
                    )
                    analysis_content += (
                        f"Materials identified: {', '.join(unique_materials)}\n\n"
                    )

                if densities:
                    analysis_content += (
                        f"Density values found: {', '.join(densities[:3])} g/cm³\n\n"
                    )

                if strengths:
                    analysis_content += (
                        f"Strength values found: {', '.join(strengths[:3])} MPa/GPa\n\n"
                    )

                analysis_content += f"Context:\n{content[:1000]}"

                deep_finding = ResearchFinding(
                    source=f"ANALYZED_{finding.source}",
                    content=analysis_content,
                    relevance_score=finding.relevance_score
                    * 1.5,  # Boost analyzed findings
                    metadata={
                        **finding.metadata,
                        "analysis_type": "deep_materials",
                        "materials_found": materials_found[:5],
                        "densities": densities[:3],
                        "strengths": strengths[:3],
                    },
                    citations=finding.citations,
                )
                deep_findings.append(deep_finding)

        # Search for specific material comparisons
        comparison_queries = [
            "aluminum vs magnesium weight comparison density",
            "lightweight materials comparison table properties",
            "formable sheet metals ductility comparison",
            "CFRP alternatives bendable composites",
        ]

        for query in comparison_queries:
            try:
                query_embedding = self.embedding_service.generate_embedding(query)
                if query_embedding is not None:
                    results = self.vector_service.search(
                        collection_name="materials_knowledge",
                        query_vector=query_embedding,
                        limit=3,
                        score_threshold=0.0,
                    )

                    for result in results:
                        content = (
                            result.payload.get("full_content")
                            or result.payload.get("content")
                            or result.payload.get("chunk_text")
                            or ""
                        )

                        # Only add if it contains comparison keywords
                        if any(
                            word in str(content).lower()
                            for word in [
                                "vs",
                                "versus",
                                "compared",
                                "comparison",
                                "table",
                            ]
                        ):
                            comparison_finding = ResearchFinding(
                                source=f"COMPARISON_{result.payload.get('document_name', 'N/A')}",
                                content=f"MATERIALS COMPARISON:\n\nQuery: {query}\n\n{content[:2000]}",
                                relevance_score=result.score
                                * 1.8,  # High boost for comparisons
                                metadata={
                                    **result.payload,
                                    "analysis_type": "comparison",
                                    "query": query,
                                },
                                citations=[f"comparison:{result.id}"],
                            )
                            deep_findings.append(comparison_finding)
            except Exception as e:
                logger.warning(f"Comparison search failed for '{query}': {e}")
                continue

        logger.info(f"Generated {len(deep_findings)} deep materials analyses")
        return deep_findings

    def _subprocess_materials_analysis(
        self, materials_findings: List[ResearchFinding], problem: str
    ) -> List[ResearchFinding]:
        """
        Use CLI subprocess to analyze materials findings.
        This allows processing 50-500 findings vs 10 with regex.
        """
        deep_findings = []

        # Prepare findings for subprocess (use full content up to chunk limit)
        chunk_size = self.config["chunk_size"]
        findings_text = []

        for idx, finding in enumerate(materials_findings):
            content = str(finding.content)
            # Truncate to chunk size but keep full chunks
            content_excerpt = content[:chunk_size]
            findings_text.append(
                f"=== FINDING {idx+1} ===\n"
                f"Source: {finding.source}\n"
                f"Relevance: {finding.relevance_score:.3f}\n\n"
                f"{content_excerpt}\n"
            )

        # Execute subprocess analysis
        result = self.cli_executor.execute(
            task_type="materials_deep_analysis",
            count=len(materials_findings),
            total_chars=sum(len(t) for t in findings_text),
            findings="\n\n".join(findings_text),
        )

        # SAVE SUBPROCESS RESULT TO DISK
        self.persistence.save_subprocess_result(
            task_type="materials_deep_analysis",
            input_summary=f"{len(materials_findings)} materials findings from {len(set(f.source for f in materials_findings))} sources",
            result=result.data if result.success else {"error": result.error},
            execution_time=result.execution_time,
        )

        if not result.success:
            logger.warning(
                f"CLI subprocess failed: {result.error}. Falling back to regex analysis."
            )
            # Fallback to regex analysis for first 10
            return self._regex_materials_analysis(materials_findings[:10])

        # Parse subprocess results into findings
        data = result.data

        # Create findings from materials
        for material in data.get("materials", []):
            analysis_text = f"MATERIAL: {material['name']}\n\n"
            if material.get("density"):
                analysis_text += f"Density: {material['density']}\n"
            if material.get("strength"):
                analysis_text += f"Strength: {material['strength']}\n"
            if material.get("formability"):
                analysis_text += f"Formability: {material['formability']}\n"
            if material.get("properties"):
                analysis_text += f"Key Properties: {', '.join(material['properties'])}\n"

            deep_findings.append(
                ResearchFinding(
                    source=f"SUBPROCESS_MATERIALS_ANALYSIS",
                    content=analysis_text,
                    relevance_score=0.9,
                    metadata={"analysis_type": "subprocess_material", "material": material},
                )
            )

        # Create findings from comparisons
        for comparison in data.get("comparisons", []):
            comp_text = (
                f"COMPARISON: {comparison['material_a']} vs {comparison['material_b']}\n"
                f"Criterion: {comparison['criterion']}\n"
                f"Winner: {comparison['winner']}\n"
                f"Confidence: {comparison['confidence']}\n"
            )
            deep_findings.append(
                ResearchFinding(
                    source=f"SUBPROCESS_COMPARISON",
                    content=comp_text,
                    relevance_score=comparison["confidence"],
                    metadata={
                        "analysis_type": "subprocess_comparison",
                        "comparison": comparison,
                    },
                )
            )

        # Create findings from recommendations
        for rec in data.get("recommendations", []):
            rec_text = (
                f"RECOMMENDATION: {rec['material']}\n"
                f"Use Case: {rec['use_case']}\n"
                f"Pros: {', '.join(rec['pros'])}\n"
                f"Cons: {', '.join(rec['cons'])}\n"
                f"Score: {rec['score']}\n"
            )
            deep_findings.append(
                ResearchFinding(
                    source=f"SUBPROCESS_RECOMMENDATION",
                    content=rec_text,
                    relevance_score=rec["score"],
                    metadata={
                        "analysis_type": "subprocess_recommendation",
                        "recommendation": rec,
                    },
                )
            )

        # Add key insights as a single finding
        if data.get("key_insights"):
            insights_text = "KEY MATERIALS INSIGHTS:\n\n" + "\n".join(
                f"• {insight}" for insight in data["key_insights"]
            )
            deep_findings.append(
                ResearchFinding(
                    source=f"SUBPROCESS_INSIGHTS",
                    content=insights_text,
                    relevance_score=0.95,
                    metadata={
                        "analysis_type": "subprocess_insights",
                        "insights": data["key_insights"],
                    },
                )
            )

        logger.info(
            f"CLI subprocess analyzed {len(materials_findings)} findings "
            f"→ {len(deep_findings)} structured insights"
        )
        return deep_findings

    def _regex_materials_analysis(
        self, materials_findings: List[ResearchFinding]
    ) -> List[ResearchFinding]:
        """
        Fallback regex-based materials analysis (original method).
        Used when CLI subprocess is not available.
        """
        deep_findings = []

        for finding in materials_findings[:10]:
            content = str(finding.content)

            # Extract material names mentioned
            material_patterns = [
                r"(?:aluminum|aluminium|magnesium|titanium|steel|carbon fiber|CFRP|polymer|composite|alloy)\s+(?:alloy|sheet|composite)?",
                r"(?:AZ31|6061|7075|Ti-6Al-4V|CFRP|GFRP)",
            ]

            materials_found = []
            for pattern in material_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                materials_found.extend(matches)

            # Extract density/weight information
            density_pattern = r"density.*?(\d+\.?\d*)\s*(?:g/cm|kg/m)"
            densities = re.findall(density_pattern, content, re.IGNORECASE)

            # Extract strength/modulus information
            strength_pattern = r"(?:strength|modulus|stiffness).*?(\d+\.?\d*)\s*(?:MPa|GPa)"
            strengths = re.findall(strength_pattern, content, re.IGNORECASE)

            # Create enriched finding with extracted data
            if materials_found or densities or strengths:
                analysis_content = f"REGEX MATERIALS ANALYSIS:\n\n"
                analysis_content += f"Source: {finding.source}\n\n"

                if materials_found:
                    unique_materials = list(set([m.strip() for m in materials_found[:5]]))
                    analysis_content += (
                        f"Materials identified: {', '.join(unique_materials)}\n\n"
                    )

                if densities:
                    analysis_content += (
                        f"Density values found: {', '.join(densities[:3])} g/cm³\n\n"
                    )

                if strengths:
                    analysis_content += (
                        f"Strength values found: {', '.join(strengths[:3])} MPa/GPa\n\n"
                    )

                analysis_content += f"Context:\n{content[:1000]}"

                deep_finding = ResearchFinding(
                    source=f"REGEX_ANALYZED_{finding.source}",
                    content=analysis_content,
                    relevance_score=finding.relevance_score * 1.3,
                    metadata={
                        **finding.metadata,
                        "analysis_type": "regex_materials",
                        "materials_found": materials_found[:5],
                        "densities": densities[:3],
                        "strengths": strengths[:3],
                    },
                    citations=finding.citations,
                )
                deep_findings.append(deep_finding)

        return deep_findings


# Singleton instance
_research_agent: Optional[DeepResearchAgent] = None


def get_research_agent(reset: bool = False) -> DeepResearchAgent:
    """Get or create research agent singleton"""
    global _research_agent

    if reset or _research_agent is None:
        _research_agent = DeepResearchAgent()

    return _research_agent
