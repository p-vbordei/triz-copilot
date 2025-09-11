"""
Health Checks and System Diagnostics (T054)
Provides health monitoring and diagnostics for TRIZ system.
"""

import time
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    from .config import get_config
except ImportError:
    from config import get_config

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status for a component"""
    component: str
    status: str  # healthy, degraded, unhealthy, unknown
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def is_healthy(self) -> bool:
        return self.status == "healthy"
    
    @property
    def is_degraded(self) -> bool:
        return self.status == "degraded"
    
    @property
    def is_unhealthy(self) -> bool:
        return self.status == "unhealthy"


@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    process_count: int
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HealthChecker:
    """Performs health checks on TRIZ components"""
    
    def __init__(self):
        """Initialize health checker"""
        self.config = get_config()
        self.checks = {
            "system": self.check_system_resources,
            "ollama": self.check_ollama,
            "qdrant": self.check_qdrant,
            "data_files": self.check_data_files,
            "sessions": self.check_sessions,
            "cache": self.check_cache,
        }
        
        self.last_check_time: Optional[datetime] = None
        self.last_results: Dict[str, HealthStatus] = {}
    
    def check_all(self, verbose: bool = False) -> Dict[str, HealthStatus]:
        """
        Run all health checks.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Dictionary of health statuses
        """
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                status = check_func(verbose=verbose)
                status.response_time_ms = (time.time() - start_time) * 1000
                results[name] = status
            except Exception as e:
                results[name] = HealthStatus(
                    component=name,
                    status="unhealthy",
                    message=f"Check failed: {str(e)}"
                )
                logger.error(f"Health check failed for {name}: {str(e)}")
        
        self.last_check_time = datetime.utcnow()
        self.last_results = results
        
        return results
    
    def check_system_resources(self, verbose: bool = False) -> HealthStatus:
        """
        Check system resource usage.
        
        Args:
            verbose: Include detailed metrics
        
        Returns:
            Health status
        """
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                process_count=len(psutil.pids())
            )
            
            # Determine status
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = "unhealthy"
                message = "Critical resource usage detected"
            elif cpu_percent > 75 or memory.percent > 75 or disk.percent > 85:
                status = "degraded"
                message = "High resource usage detected"
            else:
                status = "healthy"
                message = "System resources within normal range"
            
            details = metrics.to_dict() if verbose else None
            
            return HealthStatus(
                component="system",
                status=status,
                message=message,
                details=details
            )
            
        except Exception as e:
            return HealthStatus(
                component="system",
                status="unknown",
                message=f"Failed to check system resources: {str(e)}"
            )
    
    def check_ollama(self, verbose: bool = False) -> HealthStatus:
        """
        Check Ollama service health.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Health status
        """
        if not OLLAMA_AVAILABLE:
            return HealthStatus(
                component="ollama",
                status="unknown",
                message="Ollama library not installed"
            )
        
        try:
            # Try to connect to Ollama
            client = ollama.Client(host=self.config.embedding.ollama_host)
            
            # List models to verify connection
            models = client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            # Check if required model is available
            required_model = self.config.embedding.ollama_model
            has_required = any(required_model in name for name in model_names)
            
            if has_required:
                status = "healthy"
                message = f"Ollama service running with {required_model}"
            else:
                status = "degraded"
                message = f"Ollama running but {required_model} not found"
            
            details = {
                "host": self.config.embedding.ollama_host,
                "models_available": len(model_names),
                "required_model": required_model,
                "has_required_model": has_required
            }
            
            if verbose:
                details["models"] = model_names
            
            return HealthStatus(
                component="ollama",
                status=status,
                message=message,
                details=details if verbose else None
            )
            
        except Exception as e:
            return HealthStatus(
                component="ollama",
                status="unhealthy",
                message=f"Cannot connect to Ollama: {str(e)}",
                details={"host": self.config.embedding.ollama_host}
            )
    
    def check_qdrant(self, verbose: bool = False) -> HealthStatus:
        """
        Check Qdrant database health.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Health status
        """
        if not QDRANT_AVAILABLE:
            return HealthStatus(
                component="qdrant",
                status="unknown",
                message="Qdrant client not installed"
            )
        
        try:
            # Try to connect to Qdrant
            client = QdrantClient(
                host=self.config.database.qdrant_host,
                port=self.config.database.qdrant_port,
                api_key=self.config.database.qdrant_api_key
            )
            
            # Get collections info
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            # Check required collections
            required_collections = ["principles", "materials", "contradictions", "knowledge"]
            missing = [c for c in required_collections if c not in collection_names]
            
            if not missing:
                status = "healthy"
                message = "Qdrant service running with all collections"
            elif len(missing) < len(required_collections):
                status = "degraded"
                message = f"Qdrant running but missing collections: {', '.join(missing)}"
            else:
                status = "unhealthy"
                message = "Qdrant running but no required collections found"
            
            details = {
                "host": self.config.database.qdrant_host,
                "port": self.config.database.qdrant_port,
                "collections_count": len(collection_names),
                "missing_collections": missing
            }
            
            if verbose:
                details["collections"] = collection_names
            
            return HealthStatus(
                component="qdrant",
                status=status,
                message=message,
                details=details if verbose else None
            )
            
        except Exception as e:
            # Check if file-based fallback is available
            if self.config.enable_offline_mode:
                return HealthStatus(
                    component="qdrant",
                    status="degraded",
                    message="Qdrant unavailable, using file-based fallback",
                    details={"error": str(e)}
                )
            else:
                return HealthStatus(
                    component="qdrant",
                    status="unhealthy",
                    message=f"Cannot connect to Qdrant: {str(e)}",
                    details={
                        "host": self.config.database.qdrant_host,
                        "port": self.config.database.qdrant_port
                    }
                )
    
    def check_data_files(self, verbose: bool = False) -> HealthStatus:
        """
        Check data files availability.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Health status
        """
        required_files = [
            self.config.data_dir / "triz_principles.txt",
            self.config.data_dir / "contradiction_matrix.json",
        ]
        
        missing_files = []
        file_info = {}
        
        for file_path in required_files:
            if file_path.exists():
                if verbose:
                    stat = file_path.stat()
                    file_info[file_path.name] = {
                        "size_kb": stat.st_size / 1024,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
            else:
                missing_files.append(file_path.name)
        
        if not missing_files:
            status = "healthy"
            message = "All required data files present"
        elif len(missing_files) < len(required_files):
            status = "degraded"
            message = f"Missing data files: {', '.join(missing_files)}"
        else:
            status = "unhealthy"
            message = "No data files found"
        
        details = {
            "data_dir": str(self.config.data_dir),
            "required_files": len(required_files),
            "missing_files": missing_files
        }
        
        if verbose and file_info:
            details["files"] = file_info
        
        return HealthStatus(
            component="data_files",
            status=status,
            message=message,
            details=details if (verbose or missing_files) else None
        )
    
    def check_sessions(self, verbose: bool = False) -> HealthStatus:
        """
        Check session storage health.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Health status
        """
        session_dir = self.config.session.storage_dir
        
        if not session_dir.exists():
            return HealthStatus(
                component="sessions",
                status="unhealthy",
                message=f"Session directory does not exist: {session_dir}"
            )
        
        try:
            # Count session files
            session_files = list(session_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in session_files) / (1024 * 1024)  # MB
            
            # Check for old sessions
            cutoff_date = datetime.now() - timedelta(days=self.config.session.cleanup_days)
            old_sessions = [
                f for f in session_files
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff_date
            ]
            
            if len(session_files) > self.config.session.max_sessions:
                status = "degraded"
                message = f"Too many sessions ({len(session_files)}/{self.config.session.max_sessions})"
            elif old_sessions:
                status = "degraded"
                message = f"{len(old_sessions)} sessions need cleanup"
            else:
                status = "healthy"
                message = f"{len(session_files)} active sessions"
            
            details = {
                "session_dir": str(session_dir),
                "session_count": len(session_files),
                "total_size_mb": round(total_size, 2),
                "old_sessions": len(old_sessions),
                "max_sessions": self.config.session.max_sessions
            }
            
            return HealthStatus(
                component="sessions",
                status=status,
                message=message,
                details=details if verbose else None
            )
            
        except Exception as e:
            return HealthStatus(
                component="sessions",
                status="unhealthy",
                message=f"Failed to check sessions: {str(e)}"
            )
    
    def check_cache(self, verbose: bool = False) -> HealthStatus:
        """
        Check cache directory health.
        
        Args:
            verbose: Include detailed information
        
        Returns:
            Health status
        """
        cache_dir = self.config.cache_dir
        
        if not self.config.enable_caching:
            return HealthStatus(
                component="cache",
                status="healthy",
                message="Caching disabled"
            )
        
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            return HealthStatus(
                component="cache",
                status="healthy",
                message="Cache directory created"
            )
        
        try:
            # Calculate cache size
            cache_files = list(cache_dir.rglob("*"))
            file_count = sum(1 for f in cache_files if f.is_file())
            total_size = sum(f.stat().st_size for f in cache_files if f.is_file()) / (1024 * 1024)  # MB
            
            # Check cache size
            if total_size > 1000:  # 1GB
                status = "degraded"
                message = f"Cache size large: {total_size:.1f}MB"
            else:
                status = "healthy"
                message = f"Cache size: {total_size:.1f}MB"
            
            details = {
                "cache_dir": str(cache_dir),
                "file_count": file_count,
                "total_size_mb": round(total_size, 2)
            }
            
            return HealthStatus(
                component="cache",
                status=status,
                message=message,
                details=details if verbose else None
            )
            
        except Exception as e:
            return HealthStatus(
                component="cache",
                status="unhealthy",
                message=f"Failed to check cache: {str(e)}"
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get health check summary.
        
        Returns:
            Summary dictionary
        """
        if not self.last_results:
            self.check_all()
        
        healthy = sum(1 for s in self.last_results.values() if s.is_healthy)
        degraded = sum(1 for s in self.last_results.values() if s.is_degraded)
        unhealthy = sum(1 for s in self.last_results.values() if s.is_unhealthy)
        
        overall_status = "healthy"
        if unhealthy > 0:
            overall_status = "unhealthy"
        elif degraded > 0:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "components_checked": len(self.last_results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "components": {k: v.status for k, v in self.last_results.items()}
        }


class SystemDiagnostics:
    """System diagnostics and troubleshooting"""
    
    def __init__(self):
        """Initialize diagnostics"""
        self.health_checker = HealthChecker()
        self.config = get_config()
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """
        Run complete system diagnostics.
        
        Returns:
            Diagnostic results
        """
        logger.info("Running system diagnostics...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "health_checks": {},
            "system_info": self.get_system_info(),
            "configuration": self.get_config_summary(),
            "recommendations": []
        }
        
        # Run health checks
        health_results = self.health_checker.check_all(verbose=True)
        results["health_checks"] = {k: v.to_dict() for k, v in health_results.items()}
        
        # Generate recommendations
        results["recommendations"] = self.generate_recommendations(health_results)
        
        # Overall assessment
        results["overall_assessment"] = self.assess_system(health_results)
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            System info dictionary
        """
        import platform
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "total_disk_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary.
        
        Returns:
            Config summary
        """
        return {
            "debug_mode": self.config.debug,
            "log_level": self.config.log_level,
            "offline_mode": self.config.enable_offline_mode,
            "caching_enabled": self.config.enable_caching,
            "vector_search_enabled": self.config.enable_vector_search,
            "ollama_model": self.config.embedding.ollama_model,
            "qdrant_host": f"{self.config.database.qdrant_host}:{self.config.database.qdrant_port}"
        }
    
    def generate_recommendations(self, health_results: Dict[str, HealthStatus]) -> List[str]:
        """
        Generate recommendations based on health checks.
        
        Args:
            health_results: Health check results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # System resources
        system_health = health_results.get("system")
        if system_health and system_health.is_degraded:
            recommendations.append("Consider increasing system resources or reducing load")
        
        # Ollama
        ollama_health = health_results.get("ollama")
        if ollama_health and ollama_health.is_unhealthy:
            recommendations.append(f"Start Ollama service: ollama serve")
        elif ollama_health and ollama_health.is_degraded:
            recommendations.append(f"Pull required model: ollama pull {self.config.embedding.ollama_model}")
        
        # Qdrant
        qdrant_health = health_results.get("qdrant")
        if qdrant_health and qdrant_health.is_unhealthy:
            if self.config.enable_offline_mode:
                recommendations.append("System running in offline mode with file-based storage")
            else:
                recommendations.append("Start Qdrant service or enable offline mode")
        
        # Sessions
        session_health = health_results.get("sessions")
        if session_health and session_health.is_degraded:
            recommendations.append("Run session cleanup to remove old sessions")
        
        # Cache
        cache_health = health_results.get("cache")
        if cache_health and cache_health.is_degraded:
            recommendations.append("Consider clearing cache to free up space")
        
        return recommendations
    
    def assess_system(self, health_results: Dict[str, HealthStatus]) -> str:
        """
        Assess overall system status.
        
        Args:
            health_results: Health check results
        
        Returns:
            Assessment message
        """
        unhealthy = [k for k, v in health_results.items() if v.is_unhealthy]
        degraded = [k for k, v in health_results.items() if v.is_degraded]
        
        if unhealthy:
            return f"System has critical issues with: {', '.join(unhealthy)}"
        elif degraded:
            return f"System operational with degraded components: {', '.join(degraded)}"
        else:
            return "System fully operational"
    
    def export_diagnostics(
        self,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Export diagnostics to file.
        
        Args:
            output_file: Output file path
        
        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = Path(f"triz_diagnostics_{datetime.now():%Y%m%d_%H%M%S}.json")
        
        results = self.run_diagnostics()
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Diagnostics exported to {output_file}")
        return output_file


# Convenience functions
def check_health(verbose: bool = False) -> Dict[str, HealthStatus]:
    """
    Run health checks.
    
    Args:
        verbose: Include detailed information
    
    Returns:
        Health check results
    """
    checker = HealthChecker()
    return checker.check_all(verbose=verbose)


def get_health_summary() -> Dict[str, Any]:
    """
    Get health summary.
    
    Returns:
        Health summary
    """
    checker = HealthChecker()
    return checker.get_summary()


def run_diagnostics() -> Dict[str, Any]:
    """
    Run system diagnostics.
    
    Returns:
        Diagnostic results
    """
    diagnostics = SystemDiagnostics()
    return diagnostics.run_diagnostics()


if __name__ == "__main__":
    # Run diagnostics when executed as script
    import json
    
    print("Running TRIZ System Health Checks...\n")
    
    # Run health checks
    health_results = check_health(verbose=True)
    
    # Print results
    for component, status in health_results.items():
        icon = "✅" if status.is_healthy else "⚠️" if status.is_degraded else "❌"
        print(f"{icon} {component}: {status.message}")
        if status.details:
            print(f"   Details: {json.dumps(status.details, indent=2)}")
    
    # Print summary
    print("\n" + "="*50)
    summary = get_health_summary()
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"Healthy: {summary['healthy']}/{summary['components_checked']}")
    print(f"Degraded: {summary['degraded']}/{summary['components_checked']}")
    print(f"Unhealthy: {summary['unhealthy']}/{summary['components_checked']}")
    
    # Export diagnostics
    print("\nExporting full diagnostics...")
    diagnostics = SystemDiagnostics()
    output_file = diagnostics.export_diagnostics()
    print(f"Diagnostics saved to: {output_file}")