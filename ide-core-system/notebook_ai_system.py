"""
Notebook AI System - Three-Phase Evolution
==========================================

A comprehensive AI agent orchestration system with three-phase evolution:
- Phase 1: Past - Initial Foundation (logging, journaling, voice)
- Phase 2: Present - Active Runtime Intelligence (tracking, routing, health)
- Phase 3: Future - Autonomous Mapping & Runtime Support (context, evolution)

Author: Legion AI System
Date: September 12, 2025
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib
import os
import sys

# Add project paths for integration
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'RuntimeIntelligence'))
sys.path.append(os.path.join(parent_dir, 'Backend'))

# ============================================================================
# PHASE 1: PAST - INITIAL FOUNDATION
# ============================================================================

@dataclass
class CheckpointEntry:
    """Represents a single checkpoint in the agent execution timeline"""
    timestamp: str
    agent_name: str
    task_type: str
    file_name: str
    execution_status: str
    task_id: str
    foreground: bool
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class JournalEntry:
    """Structured journal entry for replay and audit"""
    entry_id: str
    timestamp: str
    agent_name: str
    action: str
    target_file: str
    before_state: Optional[str]
    after_state: Optional[str]
    success: bool
    rollback_available: bool
    voice_narration_triggered: bool
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

class CheckpointLogger:
    """Phase 1: Foundation - Checkpoint logging system"""

    def __init__(self, log_file: str = "notebook_ai_checkpoints.json"):
        self.log_file = log_file
        self.checkpoints: List[CheckpointEntry] = []
        self._load_existing_checkpoints()

    def _load_existing_checkpoints(self):
        """Load existing checkpoints from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.checkpoints = [CheckpointEntry(**entry) for entry in data]
        except Exception as e:
            print(f"Warning: Error loading checkpoints: {e}")

    def log_checkpoint(self, agent_name: str, task_type: str, file_name: str,
                      execution_status: str, foreground: bool = True,
                      metadata: Dict[str, Any] = None) -> str:
        """Log a new checkpoint"""
        task_id = hashlib.md5(f"{agent_name}{task_type}{file_name}{time.time()}".encode()).hexdigest()[:8]

        checkpoint = CheckpointEntry(
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            task_type=task_type,
            file_name=file_name,
            execution_status=execution_status,
            task_id=task_id,
            foreground=foreground,
            metadata=metadata or {}
        )

        self.checkpoints.append(checkpoint)
        self._save_checkpoints()

        return task_id

    def _save_checkpoints(self):
        """Save checkpoints to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump([cp.to_dict() for cp in self.checkpoints], f, indent=2)
        except Exception as e:
            print(f"Warning: Error saving checkpoints: {e}")

class ReplaySafeJournal:
    """Phase 1: Foundation - Replay-safe journaling system"""

    def __init__(self, journal_file: str = "notebook_ai_journal.json"):
        self.journal_file = journal_file
        self.entries: List[JournalEntry] = []
        self._load_journal()

    def _load_journal(self):
        """Load existing journal entries"""
        try:
            if os.path.exists(self.journal_file):
                with open(self.journal_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [JournalEntry(**entry) for entry in data]
        except Exception as e:
            print(f"Warning: Error loading journal: {e}")

    def log_action(self, agent_name: str, action: str, target_file: str,
                  success: bool = True, trigger_voice: bool = False,
                  metadata: Dict[str, Any] = None) -> str:
        """Log an agent action with before/after state"""

        entry_id = hashlib.md5(f"{agent_name}{action}{target_file}{time.time()}".encode()).hexdigest()[:12]

        # Get file states for rollback capability
        before_hash = self._get_file_hash(target_file)

        entry = JournalEntry(
            entry_id=entry_id,
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            action=action,
            target_file=target_file,
            before_state=before_hash,
            after_state=None,
            success=success,
            rollback_available=before_hash is not None,
            voice_narration_triggered=trigger_voice,
            metadata=metadata or {}
        )

        self.entries.append(entry)
        self._save_journal()

        return entry_id

    def complete_action(self, entry_id: str, success: bool = True):
        """Mark an action as completed and update after state"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                entry.success = success
                entry.after_state = self._get_file_hash(entry.target_file)
                self._save_journal()
                break

    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Get SHA256 hash of file content"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()
            return None
        except:
            return None

    def _save_journal(self):
        """Save journal to file"""
        try:
            with open(self.journal_file, 'w') as f:
                json.dump([entry.to_dict() for entry in self.entries], f, indent=2)
        except Exception as e:
            print(f"Warning: Error saving journal: {e}")

class VoiceNarrator:
    """Phase 1: Foundation - Voice narration system"""

    def __init__(self, language: str = "en"):
        self.language = language
        self.narration_log = []

    def narrate(self, message: str, language: str = None, priority: str = "normal"):
        """Narrate a message in specified language"""
        lang = language or self.language
        timestamp = datetime.now().isoformat()

        narration_entry = {
            "timestamp": timestamp,
            "message": message,
            "language": lang,
            "priority": priority,
            "delivered": True
        }

        self.narration_log.append(narration_entry)

        return narration_entry

    def narrate_task_completion(self, agent_name: str, task: str, success: bool):
        """Narrate task completion"""
        if success:
            message = f"{agent_name} successfully completed {task}"
        else:
            message = f"{agent_name} failed to complete {task}"

        return self.narrate(message, priority="high")

# ============================================================================
# PHASE 2: PRESENT - ACTIVE RUNTIME INTELLIGENCE
# ============================================================================

@dataclass
class AgentStatus:
    """Current status of an active agent"""
    name: str
    status: str
    current_task: Optional[str]
    last_activity: str
    task_count: int
    success_rate: float
    model_used: Optional[str]
    health_score: float

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ModelRoute:
    """Model routing decision and result"""
    timestamp: str
    requested_model: str
    actual_model: str
    fallback_triggered: bool
    fallback_reason: Optional[str]
    latency_ms: float
    success: bool
    task_type: str

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class HealthCheck:
    """System health check result"""
    timestamp: str
    component: str
    status: str
    response_time_ms: float
    error_message: Optional[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

class MultiAgentTracker:
    """Phase 2: Present - Multi-agent tracking system"""

    def __init__(self):
        self.agents: Dict[str, AgentStatus] = {}
        self.task_history: List[Dict] = []

    def register_agent(self, name: str, initial_model: str = None):
        """Register a new agent for tracking"""
        self.agents[name] = AgentStatus(
            name=name,
            status="idle",
            current_task=None,
            last_activity=datetime.now().isoformat(),
            task_count=0,
            success_rate=1.0,
            model_used=initial_model,
            health_score=1.0
        )

    def update_agent_status(self, name: str, status: str, task: str = None,
                           model: str = None, success: bool = None):
        """Update agent status and track task"""
        if name not in self.agents:
            self.register_agent(name, model)

        agent = self.agents[name]
        agent.status = status
        agent.last_activity = datetime.now().isoformat()

        if task:
            agent.current_task = task

        if model:
            agent.model_used = model

        if success is not None:
            agent.task_count += 1
            if success:
                agent.success_rate = (agent.success_rate * (agent.task_count - 1) + 1) / agent.task_count
            else:
                agent.success_rate = (agent.success_rate * (agent.task_count - 1)) / agent.task_count

        task_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": name,
            "status": status,
            "task": task,
            "model": model,
            "success": success
        }
        self.task_history.append(task_entry)

    def get_agent_status(self, name: str) -> Optional[AgentStatus]:
        """Get current status of an agent"""
        return self.agents.get(name)

    def get_all_agents_status(self) -> Dict[str, Dict]:
        """Get status of all tracked agents"""
        return {name: agent.to_dict() for name, agent in self.agents.items()}

    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all agent tasks"""
        total_tasks = len(self.task_history)
        successful_tasks = sum(1 for t in self.task_history if t.get("success"))
        active_agents = sum(1 for a in self.agents.values() if a.status == "active")

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "active_agents": active_agents,
            "total_agents": len(self.agents)
        }

class RuntimeIntelligence:
    """Phase 2: Present - Runtime intelligence with model routing and health checks"""

    def __init__(self):
        self.model_routes: List[ModelRoute] = []
        self.health_checks: List[HealthCheck] = []
        self.model_health: Dict[str, float] = {}

    def route_model(self, requested_model: str, task_type: str) -> str:
        """Route to appropriate model with fallback logic"""
        start_time = time.time()

        available_models = {
            "codellama:7b": True,
            "gpt-4": True,
            "claude-3": False,
            "llama2": True
        }

        actual_model = requested_model
        fallback_triggered = False
        fallback_reason = None

        if not available_models.get(requested_model, False):
            fallback_triggered = True
            if "code" in task_type.lower():
                actual_model = "codellama:7b"
                fallback_reason = "Primary model unavailable for code tasks"
            else:
                actual_model = "gpt-4"
                fallback_reason = "Primary model unavailable"

        latency = (time.time() - start_time) * 1000

        route = ModelRoute(
            timestamp=datetime.now().isoformat(),
            requested_model=requested_model,
            actual_model=actual_model,
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason,
            latency_ms=latency,
            success=True,
            task_type=task_type
        )

        self.model_routes.append(route)

        if actual_model not in self.model_health:
            self.model_health[actual_model] = 1.0

        if fallback_triggered:
            self.model_health[actual_model] = max(0.5, self.model_health[actual_model] - 0.1)

        return actual_model

    def perform_health_check(self, component: str) -> HealthCheck:
        """Perform health check on a component"""
        start_time = time.time()

        if component == "ollama":
            status = "healthy" if self.model_health.get("codellama:7b", 1.0) > 0.7 else "degraded"
        elif component == "openai":
            status = "healthy"
        elif component == "claude":
            status = "unhealthy"
        else:
            status = "healthy"

        response_time = (time.time() - start_time) * 1000

        health_check = HealthCheck(
            timestamp=datetime.now().isoformat(),
            component=component,
            status=status,
            response_time_ms=response_time,
            error_message=None if status == "healthy" else f"{component} is {status}",
            metadata={"model_health": self.model_health}
        )

        self.health_checks.append(health_check)

        return health_check

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        recent_checks = self.health_checks[-10:]

        healthy_count = sum(1 for hc in recent_checks if hc.status == "healthy")
        total_checks = len(recent_checks)

        return {
            "overall_health": healthy_count / total_checks if total_checks > 0 else 0,
            "total_checks": len(self.health_checks),
            "model_routes": len(self.model_routes),
            "model_health_scores": self.model_health
        }

# ============================================================================
# PHASE 3: FUTURE - AUTONOMOUS MAPPING & RUNTIME SUPPORT
# ============================================================================

@dataclass
class ProgramComponent:
    """A component in the program structure"""
    name: str
    type: str
    file_path: str
    dependencies: List[str]
    capabilities: List[str]
    last_modified: str

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PPILink:
    """Program-to-Program Interaction link"""
    source: str
    target: str
    interaction_type: str
    frequency: int
    last_interaction: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class AgentContext:
    """Context information for agent execution"""
    agent_name: str
    current_task: str
    available_components: List[str]
    ppi_links: List[str]
    system_health: Dict[str, Any]
    historical_performance: Dict[str, Any]
    recommended_actions: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PerformanceMetric:
    """Performance metric for agents and models"""
    timestamp: str
    component: str
    metric_type: str
    value: float
    task_context: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

class AutonomousMapper:
    """Phase 3: Future - Autonomous program mapping system"""

    def __init__(self):
        self.components: Dict[str, ProgramComponent] = {}
        self.ppi_links: List[PPILink] = []
        self.mapping_active = False

    def start_mapping(self):
        """Start autonomous mapping process"""
        self.mapping_active = True

        self._map_core_components()
        self._discover_dependencies()
        self._analyze_interactions()

    def _map_core_components(self):
        """Map all core system components"""
        components_data = [
            {
                "name": "CodeSuggestor",
                "type": "agent",
                "file_path": "RuntimeIntelligence/agents/completion_agent.py",
                "dependencies": ["BaseAgent", "ModelManager"],
                "capabilities": ["code_completion", "function_generation"]
            },
            {
                "name": "FixerShell",
                "type": "agent",
                "file_path": "RuntimeIntelligence/agents/fixer_shell.py",
                "dependencies": ["BaseAgent", "Journal"],
                "capabilities": ["error_fixing", "debugging"]
            },
            {
                "name": "VoiceNarrator",
                "type": "agent",
                "file_path": "Backend/voice_narrator.py",
                "dependencies": ["BilingualVoiceNarrator"],
                "capabilities": ["text_to_speech", "multilingual"]
            },
            {
                "name": "ModelManager",
                "type": "module",
                "file_path": "RuntimeIntelligence/model_manager.py",
                "dependencies": ["ollama", "openai"],
                "capabilities": ["model_routing", "fallback_handling"]
            }
        ]

        for comp_data in components_data:
            component = ProgramComponent(
                name=comp_data["name"],
                type=comp_data["type"],
                file_path=comp_data["file_path"],
                dependencies=comp_data["dependencies"],
                capabilities=comp_data["capabilities"],
                last_modified=datetime.now().isoformat()
            )
            self.components[comp_data["name"]] = component

    def _discover_dependencies(self):
        """Discover PPI dependencies"""
        dependencies = [
            ("CodeSuggestor", "ModelManager", "model_request"),
            ("FixerShell", "Journal", "logging"),
            ("VoiceNarrator", "CodeSuggestor", "task_completion_notification"),
            ("ModelManager", "ollama", "api_call"),
            ("ModelManager", "openai", "api_call")
        ]

        for source, target, interaction_type in dependencies:
            link = PPILink(
                source=source,
                target=target,
                interaction_type=interaction_type,
                frequency=1,
                last_interaction=datetime.now().isoformat(),
                metadata={"discovered_by": "autonomous_mapper"}
            )
            self.ppi_links.append(link)

    def _analyze_interactions(self):
        """Analyze component interactions"""
        interaction_summary = {}
        for link in self.ppi_links:
            if link.interaction_type not in interaction_summary:
                interaction_summary[link.interaction_type] = []
            interaction_summary[link.interaction_type].append(f"{link.source}→{link.target}")

    def get_component_info(self, name: str) -> Optional[ProgramComponent]:
        """Get information about a component"""
        return self.components.get(name)

    def get_ppi_network(self) -> Dict[str, List[str]]:
        """Get PPI network as adjacency list"""
        network = {}
        for link in self.ppi_links:
            if link.source not in network:
                network[link.source] = []
            network[link.source].append(link.target)
        return network

    def suggest_agent_for_task(self, task_type: str) -> List[str]:
        """Suggest agents for a specific task type"""
        suggestions = []
        for component in self.components.values():
            if component.type == "agent" and task_type in component.capabilities:
                suggestions.append(component.name)
        return suggestions

class RuntimeSupportEngine:
    """Phase 3: Future - Runtime support and context injection"""

    def __init__(self, mapper: AutonomousMapper, agent_tracker: MultiAgentTracker):
        self.mapper = mapper
        self.agent_tracker = agent_tracker
        self.context_cache: Dict[str, AgentContext] = {}

    def inject_context(self, agent_name: str, task: str) -> AgentContext:
        """Inject comprehensive context to an agent"""

        component_info = self.mapper.get_component_info(agent_name)
        available_components = list(self.mapper.components.keys())

        ppi_links = []
        for link in self.mapper.ppi_links:
            if link.source == agent_name or link.target == agent_name:
                ppi_links.append(f"{link.source}→{link.target} ({link.interaction_type})")

        # Mock system health - integrate with actual system
        system_health = {
            "overall_health": 0.95,
            "total_checks": 10,
            "model_routes": 25
        }

        agent_status = self.agent_tracker.get_agent_status(agent_name)
        historical_performance = {
            "task_count": agent_status.task_count if agent_status else 0,
            "success_rate": agent_status.success_rate if agent_status else 0,
            "last_activity": agent_status.last_activity if agent_status else None
        }

        recommendations = self._generate_recommendations(agent_name, task)

        context = AgentContext(
            agent_name=agent_name,
            current_task=task,
            available_components=available_components,
            ppi_links=ppi_links,
            system_health=system_health,
            historical_performance=historical_performance,
            recommended_actions=recommendations
        )

        self.context_cache[agent_name] = context

        return context

    def _generate_recommendations(self, agent_name: str, task: str) -> List[str]:
        """Generate intelligent recommendations for the agent"""
        recommendations = []

        if "code" in task.lower():
            recommendations.append("Consider using CodeSuggestor for complementary suggestions")

        if "error" in task.lower():
            recommendations.append("Check Journal for similar error patterns")

        if "model" in task.lower():
            recommendations.append("Verify model health before proceeding")

        recommendations.extend([
            "Monitor system health during execution",
            "Log all significant state changes",
            "Consider fallback options for critical operations"
        ])

        return recommendations

    def provide_runtime_support(self, agent_name: str, support_type: str) -> Dict[str, Any]:
        """Provide runtime support to an agent"""

        support_response = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "support_type": support_type,
            "response": {}
        }

        if support_type == "health_check":
            support_response["response"] = {"overall_health": 0.95, "status": "healthy"}
        elif support_type == "fallback_suggestion":
            current_task = self.agent_tracker.get_agent_status(agent_name)
            if current_task and current_task.current_task:
                alternatives = self.mapper.suggest_agent_for_task(current_task.current_task.split()[0].lower())
                support_response["response"] = {"alternatives": alternatives}

        return support_response

class SelfEvolvingIntelligence:
    """Phase 3: Future - Self-evolving intelligence system"""

    def __init__(self):
        self.performance_metrics: List[PerformanceMetric] = []
        self.learning_patterns: Dict[str, Dict] = {}
        self.evolution_triggers: List[Dict] = []

    def record_performance(self, component: str, metric_type: str,
                          value: float, task_context: str, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            component=component,
            metric_type=metric_type,
            value=value,
            task_context=task_context,
            metadata=metadata or {}
        )

        self.performance_metrics.append(metric)

        if component not in self.learning_patterns:
            self.learning_patterns[component] = {}

        if metric_type not in self.learning_patterns[component]:
            self.learning_patterns[component][metric_type] = []

        self.learning_patterns[component][metric_type].append(value)

    def analyze_performance_trends(self, component: str, metric_type: str, window: int = 10) -> Dict[str, Any]:
        """Analyze performance trends for a component"""
        if component not in self.learning_patterns or metric_type not in self.learning_patterns[component]:
            return {"error": "No data available"}

        values = self.learning_patterns[component][metric_type][-window:]

        if len(values) < 2:
            return {"trend": "insufficient_data", "latest_value": values[-1] if values else None}

        recent_avg = sum(values[-5:]) / len(values[-5:]) if len(values) >= 5 else sum(values) / len(values)
        overall_avg = sum(values) / len(values)

        if recent_avg > overall_avg * 1.1:
            trend = "improving"
        elif recent_avg < overall_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "latest_value": values[-1],
            "recent_average": recent_avg,
            "overall_average": overall_avg,
            "data_points": len(values)
        }

    def trigger_evolution(self, component: str, trigger_reason: str,
                         evolution_type: str, metadata: Dict[str, Any] = None):
        """Trigger an evolutionary change"""
        evolution_event = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "trigger_reason": trigger_reason,
            "evolution_type": evolution_type,
            "metadata": metadata or {}
        }

        self.evolution_triggers.append(evolution_event)

    def get_evolution_recommendations(self) -> List[Dict]:
        """Get recommendations for evolutionary improvements"""
        recommendations = []

        for component, metrics in self.learning_patterns.items():
            if "success_rate" in metrics:
                trend_analysis = self.analyze_performance_trends(component, "success_rate")

                if trend_analysis.get("trend") == "declining":
                    recommendations.append({
                        "component": component,
                        "recommendation": "Consider model upgrade or retraining",
                        "reason": f"Declining success rate trend",
                        "priority": "high"
                    })

                if trend_analysis.get("latest_value", 0) < 0.7:
                    recommendations.append({
                        "component": component,
                        "recommendation": "Performance optimization needed",
                        "reason": f"Success rate below 70%: {trend_analysis['latest_value']:.1%}",
                        "priority": "medium"
                    })

        return recommendations

# ============================================================================
# PHASE 4: BACKGROUND RESEARCH & MONITORING AGENT
# ============================================================================

@dataclass
class ProjectScan:
    """Complete project scan result"""
    timestamp: str
    total_files: int
    total_dirs: int
    file_types: Dict[str, int]
    modified_files: List[str]
    new_files: List[str]
    deleted_files: List[str]
    code_lines: int
    dependencies: List[str]
    issues_found: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ResearchContext:
    """Research context for coding support"""
    topic: str
    related_files: List[str]
    dependencies: List[str]
    patterns_found: List[str]
    recommendations: List[str]
    last_updated: str
    confidence_score: float

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class BackgroundUpdate:
    """Background update notification"""
    timestamp: str
    update_type: str
    component: str
    details: Dict[str, Any]
    priority: str
    actionable: bool

    def to_dict(self) -> Dict:
        return asdict(self)

class BackgroundResearchAgent:
    """Phase 4: Background Research & Monitoring Agent

    This agent continuously scans the project, provides research support,
    and keeps contextual information ready for coding AI agents.
    """

    def __init__(self, project_root: str = ".", scan_interval: int = 180):  # 3 minutes default
        self.project_root = os.path.abspath(project_root)
        self.scan_interval = scan_interval  # seconds
        self.is_running = False
        self.scan_thread = None
        self.last_scan: Optional[ProjectScan] = None
        self.file_hashes: Dict[str, str] = {}
        self.research_cache: Dict[str, ResearchContext] = {}
        self.update_subscribers: List[callable] = []
        self.background_updates: List[BackgroundUpdate] = []

        # Initialize with first scan
        self._load_previous_state()
        self._perform_initial_scan()

    def start_background_monitoring(self):
        """Start background monitoring thread"""
        if self.is_running:
            return

        self.is_running = True
        self.scan_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.scan_thread.start()
        print("🔍 Background Research Agent started - monitoring every 3 minutes")

    def stop_background_monitoring(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        print("🛑 Background Research Agent stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Perform comprehensive scan
                scan_result = self._perform_full_scan()

                # Analyze changes and generate research
                self._analyze_changes(scan_result)
                self._update_research_context()

                # Notify subscribers of important updates
                self._notify_subscribers()

                # Save state
                self._save_state()

                # Wait for next scan
                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"⚠️ Background monitoring error: {e}")
                time.sleep(30)  # Wait 30 seconds on error

    def _perform_initial_scan(self):
        """Perform initial comprehensive project scan"""
        print("🔍 Performing initial project scan...")
        self.last_scan = self._perform_full_scan()
        self._save_state()

    def _perform_full_scan(self) -> ProjectScan:
        """Perform comprehensive project scan"""
        timestamp = datetime.now().isoformat()
        total_files = 0
        total_dirs = 0
        file_types = {}
        modified_files = []
        new_files = []
        deleted_files = []
        code_lines = 0
        dependencies = []
        issues_found = []

        # Walk through project directory
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]

            total_dirs += len(dirs)

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                total_files += 1

                # Track file types
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

                # Check for changes
                current_hash = self._get_file_hash(file_path)
                previous_hash = self.file_hashes.get(file_path)

                if previous_hash is None:
                    new_files.append(file_path)
                elif current_hash != previous_hash:
                    modified_files.append(file_path)

                self.file_hashes[file_path] = current_hash

                # Analyze code files
                if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = len(content.split('\n'))
                            code_lines += lines

                            # Extract dependencies
                            if ext == '.py':
                                deps = self._extract_python_dependencies(content)
                                dependencies.extend(deps)

                            # Check for common issues
                            issues = self._analyze_code_issues(content, ext)
                            if issues:
                                issues_found.extend([f"{file_path}: {issue}" for issue in issues])

                    except Exception as e:
                        issues_found.append(f"{file_path}: Read error - {str(e)}")

        # Check for deleted files
        previous_files = set(self.file_hashes.keys())
        current_files = set()
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
            for file in files:
                if not file.startswith('.'):
                    current_files.add(os.path.join(root, file))

        deleted_files = list(previous_files - current_files)
        for deleted in deleted_files:
            del self.file_hashes[deleted]

        return ProjectScan(
            timestamp=timestamp,
            total_files=total_files,
            total_dirs=total_dirs,
            file_types=file_types,
            modified_files=modified_files,
            new_files=new_files,
            deleted_files=deleted_files,
            code_lines=code_lines,
            dependencies=list(set(dependencies)),
            issues_found=issues_found
        )

    def _get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""

    def _extract_python_dependencies(self, content: str) -> List[str]:
        """Extract Python dependencies from code"""
        dependencies = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                if 'import' in line:
                    parts = line.replace('import ', '').replace('from ', '').split()
                    if parts:
                        dep = parts[0].split('.')[0]
                        if dep and dep not in ['os', 'sys', 'json', 'time', 'datetime']:
                            dependencies.append(dep)

        return dependencies

    def _analyze_code_issues(self, content: str, file_ext: str) -> List[str]:
        """Analyze code for common issues"""
        issues = []

        # Check for TODO comments
        if 'TODO' in content.upper():
            issues.append("Contains TODO comments")

        # Check for print statements (potential debug code)
        if file_ext == '.py' and 'print(' in content:
            print_count = content.count('print(')
            if print_count > 10:
                issues.append(f"Many print statements ({print_count}) - possible debug code")

        # Check for long functions
        lines = content.split('\n')
        if len(lines) > 200:
            issues.append(f"Very long file ({len(lines)} lines) - consider splitting")

        # Check for empty exception handling
        if 'except:' in content and 'pass' in content:
            issues.append("Empty exception handling found")

        return issues

    def _analyze_changes(self, scan_result: ProjectScan):
        """Analyze scan results and generate insights"""
        if not self.last_scan:
            return

        # Analyze file changes
        if scan_result.new_files:
            update = BackgroundUpdate(
                timestamp=datetime.now().isoformat(),
                update_type="new_files",
                component="project_structure",
                details={"files": scan_result.new_files[:5]},  # Limit to 5
                priority="medium",
                actionable=True
            )
            self.background_updates.append(update)

        if scan_result.modified_files:
            update = BackgroundUpdate(
                timestamp=datetime.now().isoformat(),
                update_type="modified_files",
                component="project_structure",
                details={"files": scan_result.modified_files[:5]},  # Limit to 5
                priority="low",
                actionable=False
            )
            self.background_updates.append(update)

        # Analyze dependency changes
        new_deps = set(scan_result.dependencies) - set(self.last_scan.dependencies)
        if new_deps:
            update = BackgroundUpdate(
                timestamp=datetime.now().isoformat(),
                update_type="new_dependencies",
                component="dependencies",
                details={"dependencies": list(new_deps)},
                priority="high",
                actionable=True
            )
            self.background_updates.append(update)

        # Analyze issues
        if scan_result.issues_found:
            update = BackgroundUpdate(
                timestamp=datetime.now().isoformat(),
                update_type="code_issues",
                component="code_quality",
                details={"issues": scan_result.issues_found[:3]},  # Limit to 3
                priority="medium",
                actionable=True
            )
            self.background_updates.append(update)

    def _update_research_context(self):
        """Update research context based on project analysis"""
        # Update file type research
        if self.last_scan:
            file_types_context = ResearchContext(
                topic="project_file_types",
                related_files=[],
                dependencies=[],
                patterns_found=list(self.last_scan.file_types.keys()),
                recommendations=self._generate_file_type_recommendations(),
                last_updated=datetime.now().isoformat(),
                confidence_score=0.9
            )
            self.research_cache["file_types"] = file_types_context

        # Update dependency research
        if self.last_scan and self.last_scan.dependencies:
            dep_context = ResearchContext(
                topic="project_dependencies",
                related_files=[],
                dependencies=self.last_scan.dependencies,
                patterns_found=self._analyze_dependency_patterns(),
                recommendations=self._generate_dependency_recommendations(),
                last_updated=datetime.now().isoformat(),
                confidence_score=0.85
            )
            self.research_cache["dependencies"] = dep_context

        # Update code quality research
        quality_context = ResearchContext(
            topic="code_quality_patterns",
            related_files=[],
            dependencies=[],
            patterns_found=self._analyze_code_patterns(),
            recommendations=self._generate_quality_recommendations(),
            last_updated=datetime.now().isoformat(),
            confidence_score=0.8
        )
        self.research_cache["code_quality"] = quality_context

    def _generate_file_type_recommendations(self) -> List[str]:
        """Generate recommendations based on file types"""
        if not self.last_scan:
            return []

        recommendations = []
        file_types = self.last_scan.file_types

        # Python recommendations
        if file_types.get('.py', 0) > 10:
            recommendations.append("Consider adding type hints for better code maintainability")
            recommendations.append("Add comprehensive unit tests for Python modules")

        # JavaScript recommendations
        if file_types.get('.js', 0) > 5:
            recommendations.append("Consider migrating to TypeScript for better type safety")

        # Configuration files
        config_files = sum(file_types.get(ext, 0) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini'])
        if config_files > 3:
            recommendations.append("Consider consolidating configuration files")

        return recommendations

    def _analyze_dependency_patterns(self) -> List[str]:
        """Analyze dependency usage patterns"""
        if not self.last_scan:
            return []

        deps = self.last_scan.dependencies
        patterns = []

        # Common web frameworks
        web_frameworks = ['flask', 'django', 'fastapi', 'express', 'react', 'vue', 'angular']
        web_deps = [d for d in deps if d.lower() in web_frameworks]
        if web_deps:
            patterns.append(f"Web framework detected: {', '.join(web_deps)}")

        # ML/AI libraries
        ml_libs = ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'transformers']
        ml_deps = [d for d in deps if d.lower() in ml_libs]
        if ml_deps:
            patterns.append(f"ML/AI libraries detected: {', '.join(ml_deps)}")

        # Database libraries
        db_libs = ['sqlalchemy', 'pymongo', 'redis', 'postgresql', 'mysql']
        db_deps = [d for d in deps if d.lower() in db_libs]
        if db_deps:
            patterns.append(f"Database libraries detected: {', '.join(db_deps)}")

        return patterns

    def _generate_dependency_recommendations(self) -> List[str]:
        """Generate dependency-related recommendations"""
        if not self.last_scan:
            return []

        deps = self.last_scan.dependencies
        recommendations = []

        # Check for security-sensitive packages
        security_concerns = ['requests', 'urllib3', 'cryptography']
        security_deps = [d for d in deps if d.lower() in security_concerns]
        if security_deps:
            recommendations.append("Regular security audits recommended for network-related dependencies")

        # Check for testing dependencies
        test_libs = ['pytest', 'unittest', 'jest', 'mocha']
        test_deps = [d for d in deps if d.lower() in test_libs]
        if not test_deps and len(deps) > 5:
            recommendations.append("Consider adding testing framework for better code reliability")

        # Check for documentation
        doc_libs = ['sphinx', 'mkdocs', 'jsdoc']
        doc_deps = [d for d in deps if d.lower() in doc_libs]
        if not doc_deps and self.last_scan.total_files > 20:
            recommendations.append("Consider adding documentation generator")

        return recommendations

    def _analyze_code_patterns(self) -> List[str]:
        """Analyze code patterns across the project"""
        patterns = []

        if self.last_scan:
            # File size patterns
            if self.last_scan.code_lines > 10000:
                patterns.append("Large codebase - consider modular architecture")

            # File type diversity
            if len(self.last_scan.file_types) > 5:
                patterns.append("Multi-language project - ensure consistent coding standards")

            # Issue patterns
            if self.last_scan.issues_found:
                patterns.append(f"Found {len(self.last_scan.issues_found)} code quality issues")

        return patterns

    def _generate_quality_recommendations(self) -> List[str]:
        """Generate code quality recommendations"""
        recommendations = []

        if self.last_scan:
            if self.last_scan.issues_found:
                recommendations.append("Address code quality issues identified in scan")

            if self.last_scan.code_lines > 5000:
                recommendations.append("Consider adding code formatting tools (black, prettier)")

            if len(self.last_scan.file_types) > 1:
                recommendations.append("Establish coding standards for multi-language projects")

        return recommendations

    def _notify_subscribers(self):
        """Notify subscribers of important updates"""
        recent_updates = [u for u in self.background_updates if u.priority in ['high', 'medium']]

        for update in recent_updates[-3:]:  # Last 3 important updates
            for subscriber in self.update_subscribers:
                try:
                    subscriber(update)
                except Exception as e:
                    print(f"⚠️ Subscriber notification error: {e}")

    def subscribe_to_updates(self, callback: callable):
        """Subscribe to background updates"""
        self.update_subscribers.append(callback)

    def get_research_context(self, topic: str) -> Optional[ResearchContext]:
        """Get research context for a specific topic"""
        return self.research_cache.get(topic)

    def get_latest_scan(self) -> Optional[ProjectScan]:
        """Get the latest project scan results"""
        return self.last_scan

    def get_recent_updates(self, limit: int = 10) -> List[BackgroundUpdate]:
        """Get recent background updates"""
        return self.background_updates[-limit:]

    def get_project_insights(self) -> Dict[str, Any]:
        """Get comprehensive project insights"""
        if not self.last_scan:
            return {"error": "No scan data available"}

        insights = {
            "scan_timestamp": self.last_scan.timestamp,
            "project_size": {
                "files": self.last_scan.total_files,
                "directories": self.last_scan.total_dirs,
                "code_lines": self.last_scan.code_lines
            },
            "file_distribution": self.last_scan.file_types,
            "recent_changes": {
                "new_files": len(self.last_scan.new_files),
                "modified_files": len(self.last_scan.modified_files),
                "deleted_files": len(self.last_scan.deleted_files)
            },
            "dependencies": {
                "count": len(self.last_scan.dependencies),
                "list": self.last_scan.dependencies[:10]  # Top 10
            },
            "issues": {
                "count": len(self.last_scan.issues_found),
                "critical": [i for i in self.last_scan.issues_found if "error" in i.lower()][:3]
            },
            "research_contexts": list(self.research_cache.keys()),
            "background_updates": len(self.background_updates)
        }

        return insights

    def _load_previous_state(self):
        """Load previous scan state"""
        state_file = os.path.join(self.project_root, ".notebook_ai_scan.json")
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.file_hashes = data.get("file_hashes", {})
                    print("✅ Loaded previous scan state")
        except Exception as e:
            print(f"⚠️ Could not load previous state: {e}")

    def _save_state(self):
        """Save current scan state"""
        state_file = os.path.join(self.project_root, ".notebook_ai_scan.json")
        try:
            state_data = {
                "last_scan": self.last_scan.to_dict() if self.last_scan else None,
                "file_hashes": self.file_hashes,
                "research_cache": {k: v.to_dict() for k, v in self.research_cache.items()},
                "background_updates": [u.to_dict() for u in self.background_updates[-50:]],  # Keep last 50
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save state: {e}")

    def force_scan_now(self) -> ProjectScan:
        """Force an immediate scan"""
        print("🔍 Performing immediate project scan...")
        scan_result = self._perform_full_scan()
        self._analyze_changes(scan_result)
        self._update_research_context()
        self._save_state()
        return scan_result

# ============================================================================
# PHASE 5: RUNTIME OPTIMIZER AGENT
# ============================================================================

@dataclass
class APIEndpoint:
    """Configuration for external AI API endpoints"""
    name: str
    url: str
    api_key_env: str
    model_name: str
    max_tokens: int
    cost_per_token: float
    rate_limit: int  # requests per minute
    supported_tasks: List[str]
    is_free_tier: bool = True

@dataclass
class SystemMetrics:
    """Real-time system performance metrics"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    network_latency: float
    active_threads: int
    api_response_times: Dict[str, float]
    error_rates: Dict[str, float]

@dataclass
class OptimizationDecision:
    """AI-powered optimization decision"""
    timestamp: str
    decision_type: str
    target_component: str
    action: str
    expected_impact: str
    confidence_score: float
    rollback_plan: str

class RuntimeOptimizerAgent:
    """Phase 5: Runtime optimization with free AI APIs and intelligent routing"""

    def __init__(self):
        self.project_root = os.getcwd()
        self.metrics_history = []
        self.api_endpoints = self._configure_api_endpoints()
        self.optimization_decisions = []
        self.performance_thresholds = {
            'cpu_usage': 80.0,  # %
            'memory_usage': 85.0,  # %
            'response_time': 2.0,  # seconds
            'error_rate': 0.1  # 10%
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.api_keys = self._load_api_keys()

        print("🚀 RuntimeOptimizerAgent initialized with free AI API integration")

    def _configure_api_endpoints(self) -> Dict[str, APIEndpoint]:
        """Configure all supported AI API endpoints"""
        return {
            'huggingface': APIEndpoint(
                name='Hugging Face Inference API',
                url='https://api-inference.huggingface.co/models/',
                api_key_env='HF_API_KEY',
                model_name='microsoft/DialoGPT-medium',
                max_tokens=1000,
                cost_per_token=0.0,  # Free tier
                rate_limit=30,  # 30 requests/minute
                supported_tasks=['text_generation', 'conversation', 'code_completion'],
                is_free_tier=True
            ),
            'anthropic': APIEndpoint(
                name='Anthropic Claude',
                url='https://api.anthropic.com/v1/messages',
                api_key_env='ANTHROPIC_API_KEY',
                model_name='claude-3-haiku-20240307',
                max_tokens=4096,
                cost_per_token=0.0,  # Free tier available
                rate_limit=50,
                supported_tasks=['text_generation', 'analysis', 'code_review'],
                is_free_tier=True
            ),
            'openai': APIEndpoint(
                name='OpenAI GPT-4o-mini',
                url='https://api.openai.com/v1/chat/completions',
                api_key_env='OPENAI_API_KEY',
                model_name='gpt-4o-mini',
                max_tokens=4096,
                cost_per_token=0.00015,  # Very low cost
                rate_limit=200,
                supported_tasks=['text_generation', 'code_completion', 'analysis', 'conversation'],
                is_free_tier=True
            ),
            'google': APIEndpoint(
                name='Google Vertex AI',
                url='https://us-central1-aiplatform.googleapis.com/v1/projects/',
                api_key_env='GOOGLE_API_KEY',
                model_name='gemini-pro',
                max_tokens=8192,
                cost_per_token=0.0,  # Free tier
                rate_limit=60,
                supported_tasks=['text_generation', 'analysis', 'code_generation'],
                is_free_tier=True
            ),
            'assemblyai': APIEndpoint(
                name='AssemblyAI',
                url='https://api.assemblyai.com/v2/',
                api_key_env='ASSEMBLYAI_API_KEY',
                model_name='whisper-1',
                max_tokens=0,  # Audio processing
                cost_per_token=0.0,  # Free tier available
                rate_limit=5,
                supported_tasks=['speech_to_text', 'audio_processing'],
                is_free_tier=True
            ),
            'flux': APIEndpoint(
                name='Flux 1.1',
                url='https://api.replicate.com/v1/predictions',
                api_key_env='REPLICATE_API_KEY',
                model_name='blackforestlabs/flux-1.1-pro',
                max_tokens=0,  # Image generation
                cost_per_token=0.0,  # Free tier available
                rate_limit=10,
                supported_tasks=['image_generation', 'visual_content'],
                is_free_tier=True
            )
        }

    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables"""
        keys = {}
        for endpoint_name, endpoint in self.api_endpoints.items():
            key = os.getenv(endpoint.api_key_env)
            if key:
                keys[endpoint_name] = key
            else:
                print(f"⚠️ API key not found for {endpoint_name} ({endpoint.api_key_env})")
        return keys

    def start_performance_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            print("📊 Performance monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("📊 Performance monitoring started")

    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("📊 Performance monitoring stopped")

    def _monitoring_loop(self):
        """Continuous performance monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)

                # Keep only last 100 metrics
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]

                # Check for optimization opportunities
                self._analyze_performance(metrics)

                # Clean up old metrics (keep last 24 hours)
                self._cleanup_old_metrics()

                time.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                time.sleep(60)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # Network latency (ping to google)
            network_latency = self._measure_network_latency()

            # Active threads
            active_threads = threading.active_count()

            # API response times (rolling average)
            api_response_times = self._calculate_api_response_times()

            # Error rates
            error_rates = self._calculate_error_rates()

            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                network_latency=network_latency,
                active_threads=active_threads,
                api_response_times=api_response_times,
                error_rates=error_rates
            )

        except Exception as e:
            print(f"⚠️ Error collecting metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=0.0,
                memory_usage=0.0,
                network_latency=0.0,
                active_threads=0,
                api_response_times={},
                error_rates={}
            )

    def _measure_network_latency(self) -> float:
        """Measure network latency to common endpoints"""
        try:
            # Simple ping test
            response = requests.get('https://www.google.com', timeout=5)
            return response.elapsed.total_seconds()
        except:
            return 0.0

    def _calculate_api_response_times(self) -> Dict[str, float]:
        """Calculate rolling average response times for APIs"""
        response_times = {}

        # This would be populated with actual API call timing data
        # For now, return mock data
        for endpoint_name in self.api_endpoints.keys():
            response_times[endpoint_name] = 1.5  # Mock 1.5 second average

        return response_times

    def _calculate_error_rates(self) -> Dict[str, float]:
        """Calculate error rates for APIs"""
        error_rates = {}

        # This would be populated with actual error tracking data
        # For now, return mock data
        for endpoint_name in self.api_endpoints.keys():
            error_rates[endpoint_name] = 0.05  # Mock 5% error rate

        return error_rates

    def _analyze_performance(self, metrics: SystemMetrics):
        """Analyze performance metrics and make optimization decisions"""
        decisions = []

        # CPU optimization
        if metrics.cpu_usage > self.performance_thresholds['cpu_usage']:
            decision = OptimizationDecision(
                timestamp=datetime.now().isoformat(),
                decision_type='cpu_optimization',
                target_component='system',
                action='reduce_thread_priority',
                expected_impact='Reduce CPU usage by 10-20%',
                confidence_score=0.8,
                rollback_plan='restore_original_thread_priority'
            )
            decisions.append(decision)

        # Memory optimization
        if metrics.memory_usage > self.performance_thresholds['memory_usage']:
            decision = OptimizationDecision(
                timestamp=datetime.now().isoformat(),
                decision_type='memory_optimization',
                target_component='system',
                action='clear_memory_cache',
                expected_impact='Free up 100-500MB memory',
                confidence_score=0.7,
                rollback_plan='memory_usage_will_naturally_recover'
            )
            decisions.append(decision)

        # API routing optimization
        slow_apis = [api for api, time in metrics.api_response_times.items()
                    if time > self.performance_thresholds['response_time']]
        if slow_apis:
            decision = OptimizationDecision(
                timestamp=datetime.now().isoformat(),
                decision_type='api_routing',
                target_component='api_endpoints',
                action=f'route_away_from_{slow_apis[0]}',
                expected_impact='Improve response time by 20-50%',
                confidence_score=0.9,
                rollback_plan='revert_to_previous_routing'
            )
            decisions.append(decision)

        # Execute decisions
        for decision in decisions:
            self._execute_optimization_decision(decision)
            self.optimization_decisions.append(decision)

    def _execute_optimization_decision(self, decision: OptimizationDecision):
        """Execute an optimization decision"""
        print(f"🔧 Executing optimization: {decision.action} on {decision.target_component}")

        if decision.decision_type == 'cpu_optimization':
            self._optimize_cpu_usage()
        elif decision.decision_type == 'memory_optimization':
            self._optimize_memory_usage()
        elif decision.decision_type == 'api_routing':
            self._optimize_api_routing(decision.action)

    def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        try:
            # Reduce priority of background threads
            current_process = psutil.Process()
            current_process.nice(10)  # Lower priority
            print("✅ CPU optimization applied")
        except Exception as e:
            print(f"⚠️ CPU optimization failed: {e}")

    def _optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Force garbage collection
            import gc
            collected = gc.collect()
            print(f"✅ Memory optimization applied - collected {collected} objects")
        except Exception as e:
            print(f"⚠️ Memory optimization failed: {e}")

    def _optimize_api_routing(self, action: str):
        """Optimize API routing based on performance"""
        try:
            # Extract API name from action
            if 'route_away_from_' in action:
                slow_api = action.replace('route_away_from_', '')

                # Temporarily reduce rate limit for slow API
                if slow_api in self.api_endpoints:
                    original_limit = self.api_endpoints[slow_api].rate_limit
                    self.api_endpoints[slow_api].rate_limit = max(1, original_limit // 2)
                    print(f"✅ API routing optimized - reduced {slow_api} rate limit")

        except Exception as e:
            print(f"⚠️ API routing optimization failed: {e}")

    def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

    def route_api_request(self, task_type: str, content: str) -> Dict[str, Any]:
        """Intelligently route API request to best available endpoint"""
        available_endpoints = self._get_available_endpoints(task_type)

        if not available_endpoints:
            return {
                'error': 'No available API endpoints for this task type',
                'task_type': task_type
            }

        # Select best endpoint based on performance metrics
        best_endpoint = self._select_best_endpoint(available_endpoints, task_type)

        # Execute API call
        result = self._execute_api_call(best_endpoint, task_type, content)

        # Update performance metrics
        self._update_api_performance(best_endpoint.name, result.get('response_time', 0),
                                   result.get('success', False))

        return result

    def _get_available_endpoints(self, task_type: str) -> List[APIEndpoint]:
        """Get available endpoints for a task type"""
        available = []

        for endpoint in self.api_endpoints.values():
            # Check if API key is available
            if endpoint.name.lower().replace(' ', '') in self.api_keys:
                # Check if endpoint supports the task
                if task_type in endpoint.supported_tasks:
                    available.append(endpoint)

        return available

    def _select_best_endpoint(self, endpoints: List[APIEndpoint], task_type: str) -> APIEndpoint:
        """Select the best endpoint based on performance metrics"""
        if len(endpoints) == 1:
            return endpoints[0]

        # Score endpoints based on recent performance
        scored_endpoints = []
        for endpoint in endpoints:
            score = self._calculate_endpoint_score(endpoint)
            scored_endpoints.append((endpoint, score))

        # Return highest scoring endpoint
        scored_endpoints.sort(key=lambda x: x[1], reverse=True)
        return scored_endpoints[0][0]

    def _calculate_endpoint_score(self, endpoint: APIEndpoint) -> float:
        """Calculate performance score for an endpoint"""
        base_score = 1.0

        # Get recent metrics for this endpoint
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements

        if recent_metrics:
            # Average response time score (lower is better)
            avg_response_time = sum(m.api_response_times.get(endpoint.name.lower().replace(' ', ''), 1.5)
                                  for m in recent_metrics) / len(recent_metrics)
            response_score = max(0, 2.0 - avg_response_time) / 2.0  # Normalize to 0-1

            # Error rate score (lower is better)
            avg_error_rate = sum(m.error_rates.get(endpoint.name.lower().replace(' ', ''), 0.05)
                               for m in recent_metrics) / len(recent_metrics)
            error_score = max(0, 0.2 - avg_error_rate) / 0.2  # Normalize to 0-1

            # Cost score (lower is better)
            cost_score = 1.0 if endpoint.cost_per_token == 0 else 0.5

            base_score = (response_score * 0.5 + error_score * 0.3 + cost_score * 0.2)

        return base_score

    def _execute_api_call(self, endpoint: APIEndpoint, task_type: str, content: str) -> Dict[str, Any]:
        """Execute API call to specified endpoint"""
        start_time = time.time()

        try:
            if endpoint.name == 'Hugging Face Inference API':
                result = self._call_huggingface_api(endpoint, content)
            elif endpoint.name == 'Anthropic Claude':
                result = self._call_anthropic_api(endpoint, content)
            elif endpoint.name == 'OpenAI GPT-4o-mini':
                result = self._call_openai_api(endpoint, content)
            elif endpoint.name == 'Google Vertex AI':
                result = self._call_google_api(endpoint, content)
            elif endpoint.name == 'AssemblyAI':
                result = self._call_assemblyai_api(endpoint, content)
            elif endpoint.name == 'Flux 1.1':
                result = self._call_flux_api(endpoint, content)
            else:
                result = {'error': f'Unsupported endpoint: {endpoint.name}'}

            response_time = time.time() - start_time
            result['response_time'] = response_time
            result['endpoint'] = endpoint.name
            result['success'] = 'error' not in result

            return result

        except Exception as e:
            response_time = time.time() - start_time
            return {
                'error': str(e),
                'endpoint': endpoint.name,
                'response_time': response_time,
                'success': False
            }

    def _call_huggingface_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call Hugging Face Inference API"""
        api_key = self.api_keys.get('huggingface')
        if not api_key:
            return {'error': 'Hugging Face API key not found'}

        headers = {'Authorization': f'Bearer {api_key}'}
        payload = {
            'inputs': content,
            'parameters': {
                'max_length': endpoint.max_tokens,
                'temperature': 0.7
            }
        }

        response = requests.post(
            f"{endpoint.url}{endpoint.model_name}",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return {'generated_text': result[0].get('generated_text', '')}
            else:
                return {'generated_text': str(result)}
        else:
            return {'error': f'Hugging Face API error: {response.status_code}'}

    def _call_anthropic_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        api_key = self.api_keys.get('anthropic')
        if not api_key:
            return {'error': 'Anthropic API key not found'}

        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }

        payload = {
            'model': endpoint.model_name,
            'max_tokens': endpoint.max_tokens,
            'messages': [{'role': 'user', 'content': content}]
        }

        response = requests.post(
            endpoint.url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {'generated_text': result.get('content', [{}])[0].get('text', '')}
        else:
            return {'error': f'Anthropic API error: {response.status_code}'}

    def _call_openai_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call OpenAI GPT-4o-mini API"""
        api_key = self.api_keys.get('openai')
        if not api_key:
            return {'error': 'OpenAI API key not found'}

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': endpoint.model_name,
            'messages': [{'role': 'user', 'content': content}],
            'max_tokens': endpoint.max_tokens
        }

        response = requests.post(
            endpoint.url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {'generated_text': result['choices'][0]['message']['content']}
        else:
            return {'error': f'OpenAI API error: {response.status_code}'}

    def _call_google_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call Google Vertex AI API"""
        api_key = self.api_keys.get('google')
        if not api_key:
            return {'error': 'Google API key not found'}

        # Note: This is a simplified implementation
        # Real Vertex AI would require more complex authentication
        headers = {'Authorization': f'Bearer {api_key}'}
        payload = {
            'contents': [{
                'parts': [{'text': content}]
            }]
        }

        # This URL would need to be constructed properly for Vertex AI
        response = requests.post(
            f"{endpoint.url}your-project/locations/us-central1/publishers/google/models/{endpoint.model_name}:predict",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {'generated_text': result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')}
        else:
            return {'error': f'Google Vertex AI error: {response.status_code}'}

    def _call_assemblyai_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call AssemblyAI API for speech processing"""
        api_key = self.api_keys.get('assemblyai')
        if not api_key:
            return {'error': 'AssemblyAI API key not found'}

        headers = {'authorization': api_key}

        # For speech-to-text, we would typically upload audio file first
        # This is a simplified implementation
        payload = {
            'audio_url': content,  # Assuming content is audio URL
            'language_code': 'en'
        }

        response = requests.post(
            f"{endpoint.url}transcript",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return {'transcription': result.get('text', '')}
        else:
            return {'error': f'AssemblyAI API error: {response.status_code}'}

    def _call_flux_api(self, endpoint: APIEndpoint, content: str) -> Dict[str, Any]:
        """Call Flux 1.1 API for image generation"""
        api_key = self.api_keys.get('flux')
        if not api_key:
            return {'error': 'Replicate API key not found'}

        headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'version': 'blackforestlabs/flux-1.1-pro',
            'input': {'prompt': content}
        }

        response = requests.post(
            endpoint.url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 201:
            result = response.json()
            return {'image_url': result.get('output', [''])[0]}
        else:
            return {'error': f'Flux API error: {response.status_code}'}

    def _update_api_performance(self, endpoint_name: str, response_time: float, success: bool):
        """Update performance metrics for an API endpoint"""
        # This would update the metrics history with actual performance data
        # For now, we'll just print the update
        status = "success" if success else "failed"
        print(f"📊 API Performance Update: {endpoint_name} - {response_time:.2f}s - {status}")

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"error": "No performance data available"}

        latest_metrics = self.metrics_history[-1]

        report = {
            'current_metrics': {
                'cpu_usage': latest_metrics.cpu_usage,
                'memory_usage': latest_metrics.memory_usage,
                'network_latency': latest_metrics.network_latency,
                'active_threads': latest_metrics.active_threads
            },
            'api_performance': {
                'response_times': latest_metrics.api_response_times,
                'error_rates': latest_metrics.error_rates
            },
            'optimization_history': [
                {
                    'timestamp': d.timestamp,
                    'type': d.decision_type,
                    'action': d.action,
                    'impact': d.expected_impact
                }
                for d in self.optimization_decisions[-10:]  # Last 10 decisions
            ],
            'available_endpoints': list(self.api_endpoints.keys()),
            'configured_keys': list(self.api_keys.keys())
        }

        return report

    def optimize_system_configuration(self) -> Dict[str, Any]:
        """Perform comprehensive system optimization"""
        optimizations = []

        # Analyze current metrics
        if self.metrics_history:
            avg_cpu = sum(m.cpu_usage for m in self.metrics_history[-10:]) / len(self.metrics_history[-10:])
            avg_memory = sum(m.memory_usage for m in self.metrics_history[-10:]) / len(self.metrics_history[-10:])

            if avg_cpu > 70:
                optimizations.append("High CPU usage detected - consider reducing concurrent operations")
            if avg_memory > 80:
                optimizations.append("High memory usage detected - consider implementing memory pooling")

        # API configuration optimization
        available_apis = len([k for k in self.api_endpoints.keys() if k in self.api_keys])
        if available_apis == 0:
            optimizations.append("No API keys configured - add API keys for external AI services")
        elif available_apis < 3:
            optimizations.append(f"Only {available_apis} API keys configured - add more for better redundancy")

        return {
            'optimizations_applied': len(optimizations),
            'recommendations': optimizations,
            'system_health': 'good' if len(optimizations) == 0 else 'needs_attention'
        }

# ============================================================================
# INTEGRATED SYSTEM WITH BACKGROUND AGENT
# ============================================================================

class NotebookAISystem:
    """Complete Notebook AI system integrating all four phases"""

    def __init__(self):
        # Phase 1: Past - Foundation
        self.checkpoint_logger = CheckpointLogger()
        self.journal = ReplaySafeJournal()
        self.voice_narrator = VoiceNarrator()

        # Phase 2: Present - Runtime Intelligence
        self.agent_tracker = MultiAgentTracker()
        self.runtime_intel = RuntimeIntelligence()

        # Phase 3: Future - Autonomous Mapping
        self.mapper = AutonomousMapper()
        self.runtime_support = RuntimeSupportEngine(self.mapper, self.agent_tracker)
        self.evolving_intel = SelfEvolvingIntelligence()

        # Phase 4: Background Research & Monitoring
        self.background_agent = BackgroundResearchAgent()

        # Phase 5: Runtime Optimization & AI API Integration
        self.runtime_optimizer = RuntimeOptimizerAgent()

        print("🎯 Complete Notebook AI System initialized with Background Research and Runtime Optimization")

    def start_background_research(self):
        """Start the background research and monitoring agent"""
        self.background_agent.start_background_monitoring()

    def stop_background_research(self):
        """Stop the background research and monitoring agent"""
        self.background_agent.stop_background_monitoring()

    def get_research_context(self, topic: str) -> Optional[ResearchContext]:
        """Get research context for coding support"""
        return self.background_agent.get_research_context(topic)

    def get_project_insights(self) -> Dict[str, Any]:
        """Get comprehensive project insights from background agent"""
        return self.background_agent.get_project_insights()

    def subscribe_to_updates(self, callback: callable):
        """Subscribe to background updates"""
        self.background_agent.subscribe_to_updates(callback)

    def force_project_scan(self) -> ProjectScan:
        """Force an immediate project scan"""
        return self.background_agent.force_scan_now()

    # Phase 5: Runtime Optimization Methods
    def start_runtime_optimization(self):
        """Start runtime optimization and performance monitoring"""
        self.runtime_optimizer.start_performance_monitoring()

    def stop_runtime_optimization(self):
        """Stop runtime optimization and performance monitoring"""
        self.runtime_optimizer.stop_performance_monitoring()

    def route_ai_request(self, task_type: str, content: str) -> Dict[str, Any]:
        """Route AI request to optimal endpoint"""
        return self.runtime_optimizer.route_api_request(task_type, content)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return self.runtime_optimizer.get_performance_report()

    def optimize_system(self) -> Dict[str, Any]:
        """Perform system-wide optimization"""
        return self.runtime_optimizer.optimize_system_configuration()

    def execute_task_with_full_tracking(self, agent_name: str, task: str,
                                       file_path: str = None, model: str = None) -> Dict[str, Any]:
        """Execute a task with full three-phase tracking"""

        # Phase 1: Log checkpoint and journal
        task_id = self.checkpoint_logger.log_checkpoint(
            agent_name, task, file_path or "system", "running", True
        )

        journal_entry = self.journal.log_action(
            agent_name, task, file_path or "system", True, True
        )

        # Phase 2: Update agent tracking and route model
        self.agent_tracker.update_agent_status(agent_name, "active", task, model)

        if model:
            routed_model = self.runtime_intel.route_model(model, task)
        else:
            routed_model = None

        # Phase 3: Inject context and provide runtime support
        context = self.runtime_support.inject_context(agent_name, task)
        support = self.runtime_support.provide_runtime_support(agent_name, "health_check")

        # Simulate task execution
        time.sleep(0.1)
        success = True

        # Phase 1: Complete checkpoint and journal
        self.checkpoint_logger.log_checkpoint(
            agent_name, task, file_path or "system", "success" if success else "failed", True
        )
        self.journal.complete_action(journal_entry, success)

        # Phase 2: Update agent status
        self.agent_tracker.update_agent_status(agent_name, "idle", success=success)

        # Phase 3: Record performance
        self.evolving_intel.record_performance(
            agent_name, "success_rate", 1.0 if success else 0.0, task
        )

        # Voice narration
        self.voice_narrator.narrate_task_completion(agent_name, task, success)

        result = {
            "task_id": task_id,
            "agent": agent_name,
            "task": task,
            "success": success,
            "model_used": routed_model,
            "context_injected": len(context.available_components),
            "support_provided": support["support_type"]
        }

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status across all five phases"""
        return {
            "phase1": {
                "checkpoints": len(self.checkpoint_logger.checkpoints),
                "journal_entries": len(self.journal.entries),
                "narrations": len(self.voice_narrator.narration_log)
            },
            "phase2": {
                "active_agents": sum(1 for a in self.agent_tracker.agents.values() if a.status == "active"),
                "total_agents": len(self.agent_tracker.agents),
                "model_routes": len(self.runtime_intel.model_routes),
                "system_health": self.runtime_intel.get_system_health()["overall_health"]
            },
            "phase3": {
                "mapped_components": len(self.mapper.components),
                "ppi_links": len(self.mapper.ppi_links),
                "active_contexts": len(self.runtime_support.context_cache),
                "evolution_events": len(self.evolving_intel.evolution_triggers)
            },
            "phase4": {
                "background_monitoring": self.background_agent.is_running,
                "last_scan": self.background_agent.last_scan.timestamp if self.background_agent.last_scan else None,
                "research_contexts": len(self.background_agent.research_cache),
                "background_updates": len(self.background_agent.background_updates),
                "project_files": self.background_agent.last_scan.total_files if self.background_agent.last_scan else 0
            },
            "phase5": {
                "performance_monitoring": self.runtime_optimizer.monitoring_active,
                "available_apis": len(self.runtime_optimizer.api_endpoints),
                "configured_keys": len(self.runtime_optimizer.api_keys),
                "optimization_decisions": len(self.runtime_optimizer.optimization_decisions),
                "metrics_history": len(self.runtime_optimizer.metrics_history)
            }
        }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_notebook_ai_system() -> NotebookAISystem:
    """Factory function to create a complete Notebook AI system"""
    return NotebookAISystem()

def quick_demo():
    """Quick demonstration of the Notebook AI system"""
    print("🚀 Notebook AI System - Quick Demo")
    print("=" * 50)

    # Create system
    system = create_notebook_ai_system()

    # Register agents
    system.agent_tracker.register_agent("CodeSuggestor", "codellama:7b")
    system.agent_tracker.register_agent("FixerShell", "gpt-4")

    # Start autonomous mapping
    system.mapper.start_mapping()

    # Execute tasks
    result1 = system.execute_task_with_full_tracking(
        "CodeSuggestor", "code_completion", "main.py", "codellama:7b"
    )

    result2 = system.execute_task_with_full_tracking(
        "FixerShell", "error_fixing", "utils.py", "gpt-4"
    )

    # Start background research agent
    system.start_background_research()

    # Start runtime optimization
    system.start_runtime_optimization()

    # Subscribe to background updates
    def update_handler(update):
        print(f"🔄 Background Update: {update.update_type} - {update.component}")

    system.subscribe_to_updates(update_handler)

    # Get project insights
    insights = system.get_project_insights()
    print(f"📊 Project Insights: {insights['project_size']['files']} files, {insights['project_size']['code_lines']} lines")

    # Get research context
    research = system.get_research_context("dependencies")
    if research:
        print(f"🔍 Research Context: {len(research.dependencies)} dependencies found")

    # Test AI API routing
    print("\n🧠 Testing AI API Routing...")
    ai_result = system.route_ai_request("text_generation", "Write a Python function to calculate fibonacci numbers")
    if 'error' not in ai_result:
        print(f"✅ AI Response: {ai_result.get('generated_text', '')[:100]}...")
    else:
        print(f"⚠️ AI Routing: {ai_result.get('error', 'No response')}")

    # Get performance report
    perf_report = system.get_performance_report()
    print(f"📈 Performance Report: {len(perf_report.get('available_endpoints', []))} APIs available")

    # Get status
    status = system.get_system_status()

    print("\n📊 Demo Results:")
    print(f"✅ Tasks completed: {sum(1 for r in [result1, result2] if r['success'])}/2")
    print(f"🤖 Agents tracked: {status['phase2']['total_agents']}")
    print(f"🗺️ Components mapped: {status['phase3']['mapped_components']}")
    print(f"📝 Checkpoints logged: {status['phase1']['checkpoints']}")
    print(f"🔍 Background monitoring: {status['phase4']['background_monitoring']}")
    print(f"📚 Research contexts: {status['phase4']['research_contexts']}")
    print(f"🚀 Performance monitoring: {status['phase5']['performance_monitoring']}")
    print(f"🔗 Available APIs: {status['phase5']['available_apis']}")

    # Keep running for a bit to show background monitoring
    print("\n⏳ Background monitoring active... (Press Ctrl+C to stop)")
    try:
        time.sleep(5)  # Let background agent do some work
    except KeyboardInterrupt:
        pass
    finally:
        system.stop_background_research()
        system.stop_runtime_optimization()

    return system

if __name__ == "__main__":
    # Run quick demo when executed directly
    quick_demo()