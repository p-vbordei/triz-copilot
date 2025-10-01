"""
Tool Response Formatting (T040)
Formats TRIZ tool responses for consistent output.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FormattedResponse:
    """Standardized response format"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "success": self.success,
            "message": self.message
        }
        
        if self.data is not None:
            result["data"] = self.data
        
        if self.error is not None:
            result["error"] = self.error
        
        if self.metadata is not None:
            result["metadata"] = self.metadata
        
        if self.timestamp is not None:
            result["timestamp"] = self.timestamp
        
        return result
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_text(self, verbose: bool = False) -> str:
        """Convert to human-readable text"""
        lines = []
        
        if self.success:
            lines.append(f"✓ {self.message}")
        else:
            lines.append(f"✗ {self.message}")
            if self.error:
                lines.append(f"Error: {self.error}")
        
        if self.data and verbose:
            lines.append("\nData:")
            lines.append(self._format_data(self.data, indent=2))
        
        if self.metadata and verbose:
            lines.append("\nMetadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_data(self, data: Any, indent: int = 0) -> str:
        """Format data for text output"""
        indent_str = " " * indent
        
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent_str}{key}:")
                    lines.append(self._format_data(value, indent + 2))
                else:
                    lines.append(f"{indent_str}{key}: {value}")
            return "\n".join(lines)
        
        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data, 1):
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent_str}[{i}]")
                    lines.append(self._format_data(item, indent + 2))
                else:
                    lines.append(f"{indent_str}• {item}")
            return "\n".join(lines)
        
        else:
            return f"{indent_str}{data}"


class ResponseFormatter:
    """Formats responses from TRIZ tools"""
    
    def __init__(self, default_format: str = "json"):
        """
        Initialize formatter.
        
        Args:
            default_format: Default output format (json, text, dict)
        """
        self.default_format = default_format
        self.formatters = {
            "json": self._format_json,
            "text": self._format_text,
            "dict": self._format_dict,
            "markdown": self._format_markdown
        }
        
        logger.info(f"Response formatter initialized with format: {default_format}")
    
    def format_success(
        self,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format a successful response.
        
        Args:
            message: Success message
            data: Response data
            metadata: Additional metadata
            format_type: Output format
        
        Returns:
            Formatted response
        """
        response = FormattedResponse(
            success=True,
            message=message,
            data=data,
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
        
        return self._format_response(response, format_type or self.default_format)
    
    def format_error(
        self,
        message: str,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format an error response.
        
        Args:
            message: Error message
            error: Detailed error
            metadata: Additional metadata
            format_type: Output format
        
        Returns:
            Formatted response
        """
        response = FormattedResponse(
            success=False,
            message=message,
            error=error,
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
        
        return self._format_response(response, format_type or self.default_format)
    
    def format_principle(
        self,
        principle_id: int,
        principle_data: Dict[str, Any],
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format TRIZ principle response.
        
        Args:
            principle_id: Principle number
            principle_data: Principle information
            format_type: Output format
        
        Returns:
            Formatted principle
        """
        data = {
            "principle_id": principle_id,
            "name": principle_data.get("name", f"Principle {principle_id}"),
            "description": principle_data.get("description", ""),
            "examples": principle_data.get("examples", []),
            "applications": principle_data.get("applications", [])
        }
        
        return self.format_success(
            f"TRIZ Principle {principle_id}: {data['name']}",
            data=data,
            format_type=format_type
        )
    
    def format_contradiction(
        self,
        improving: int,
        worsening: int,
        principles: List[int],
        confidence: float,
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format contradiction matrix result.
        
        Args:
            improving: Improving parameter
            worsening: Worsening parameter
            principles: Recommended principles
            confidence: Confidence score
            format_type: Output format
        
        Returns:
            Formatted contradiction result
        """
        data = {
            "contradiction": {
                "improving": improving,
                "worsening": worsening
            },
            "recommended_principles": principles,
            "confidence_score": round(confidence, 2),
            "principle_count": len(principles)
        }
        
        return self.format_success(
            f"Found {len(principles)} principles for contradiction {improving}-{worsening}",
            data=data,
            metadata={"source": "contradiction_matrix"},
            format_type=format_type
        )
    
    def format_analysis(
        self,
        problem: str,
        solutions: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format TRIZ analysis result.
        
        Args:
            problem: Problem statement
            solutions: List of solutions
            metadata: Analysis metadata
            format_type: Output format
        
        Returns:
            Formatted analysis
        """
        data = {
            "problem_statement": problem,
            "solution_count": len(solutions),
            "solutions": solutions,
            "analysis_complete": True
        }
        
        return self.format_success(
            f"Generated {len(solutions)} solution concepts",
            data=data,
            metadata=metadata,
            format_type=format_type
        )
    
    def format_workflow_stage(
        self,
        session_id: str,
        stage: str,
        data: Optional[Dict[str, Any]] = None,
        next_action: Optional[str] = None,
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format workflow stage response.
        
        Args:
            session_id: Session ID
            stage: Current stage
            data: Stage data
            next_action: Next action prompt
            format_type: Output format
        
        Returns:
            Formatted stage response
        """
        response_data = {
            "session_id": session_id,
            "current_stage": stage,
            "stage_data": data or {},
            "next_action": next_action
        }
        
        return self.format_success(
            f"Workflow stage: {stage}",
            data=response_data,
            format_type=format_type
        )
    
    def format_materials(
        self,
        materials: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        format_type: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format materials recommendation.
        
        Args:
            materials: Recommended materials
            requirements: Input requirements
            format_type: Output format
        
        Returns:
            Formatted materials response
        """
        data = {
            "requirements": requirements,
            "recommendation_count": len(materials),
            "materials": materials
        }
        
        return self.format_success(
            f"Found {len(materials)} suitable materials",
            data=data,
            format_type=format_type
        )
    
    def _format_response(
        self,
        response: FormattedResponse,
        format_type: str
    ) -> Union[str, Dict[str, Any]]:
        """Apply formatting to response"""
        formatter = self.formatters.get(format_type, self._format_dict)
        return formatter(response)
    
    def _format_json(self, response: FormattedResponse) -> str:
        """Format as JSON"""
        return response.to_json()
    
    def _format_text(self, response: FormattedResponse) -> str:
        """Format as text"""
        return response.to_text(verbose=True)
    
    def _format_dict(self, response: FormattedResponse) -> Dict[str, Any]:
        """Format as dictionary"""
        return response.to_dict()
    
    def _format_markdown(self, response: FormattedResponse) -> str:
        """Format as markdown"""
        lines = []
        
        # Header
        if response.success:
            lines.append(f"## ✅ {response.message}")
        else:
            lines.append(f"## ❌ {response.message}")
            if response.error:
                lines.append(f"\n**Error:** {response.error}")
        
        # Data section
        if response.data:
            lines.append("\n### Data")
            lines.append(self._data_to_markdown(response.data))
        
        # Metadata section
        if response.metadata:
            lines.append("\n### Metadata")
            for key, value in response.metadata.items():
                lines.append(f"- **{key}:** {value}")
        
        # Timestamp
        if response.timestamp:
            lines.append(f"\n*Generated: {response.timestamp}*")
        
        return "\n".join(lines)
    
    def _data_to_markdown(self, data: Any, level: int = 0) -> str:
        """Convert data to markdown format"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"\n**{key}:**")
                    lines.append(self._data_to_markdown(value, level + 1))
                else:
                    lines.append(f"- **{key}:** {value}")
            return "\n".join(lines)
        
        elif isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, dict):
                    lines.append(self._data_to_markdown(item, level + 1))
                else:
                    lines.append(f"- {item}")
            return "\n".join(lines)
        
        else:
            return str(data)


# Singleton instance
_default_formatter: Optional[ResponseFormatter] = None


def get_formatter(
    default_format: str = "json",
    reset: bool = False
) -> ResponseFormatter:
    """Get or create default formatter"""
    global _default_formatter
    
    if reset or _default_formatter is None:
        _default_formatter = ResponseFormatter(default_format=default_format)
    
    return _default_formatter


# Convenience functions
def format_success(
    message: str,
    data: Optional[Dict[str, Any]] = None,
    format_type: str = "json"
) -> Union[str, Dict[str, Any]]:
    """Format success response"""
    formatter = get_formatter()
    return formatter.format_success(message, data, format_type=format_type)


def format_error(
    message: str,
    error: Optional[str] = None,
    format_type: str = "json"
) -> Union[str, Dict[str, Any]]:
    """Format error response"""
    formatter = get_formatter()
    return formatter.format_error(message, error, format_type=format_type)