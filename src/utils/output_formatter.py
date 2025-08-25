import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ModelParameters:
    temperature: float
    reasoning_level: str
    max_output_tokens: int

@dataclass
class ModelInfo:
    name: str
    version: str
    provider: str
    parameters: ModelParameters

@dataclass
class Environment:
    endpoint: str

@dataclass
class IssueSummary:
    title: str
    topic_area: str
    overview: str
    desired_behavior: str
    observed_behavior: str
    self_assessed_severity: str
    self_assessed_severity_justification: str
    self_assessed_breadth: str
    self_assessed_breadth_justification: str

@dataclass
class HarmonyFinding:
    schema_version: str = "1.0.0"
    issue_title: str = ""
    model: Optional[ModelInfo] = None
    environment: Optional[Environment] = None
    issue_summary: Optional[IssueSummary] = None
    harmony_response_walkthroughs: List[str] = None
    steps_to_reproduce: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.harmony_response_walkthroughs is None:
            self.harmony_response_walkthroughs = []
        if self.steps_to_reproduce is None:
            self.steps_to_reproduce = []

class OutputFormatter:
    
    @staticmethod
    def create_finding(
        issue_title: str,
        model_name: str,
        model_version: str,
        attack_type: str,
        overview: str,
        observed_behavior: str,
        desired_behavior: str,
        severity: int,
        severity_justification: str,
        breadth: int,
        breadth_justification: str,
        conversation_walkthrough: str,
        reproduction_steps: List[str],
        notes: str = "",
        temperature: float = 1.0,
        max_tokens: int = 1024,
        reasoning_level: str = "low"
    ) -> HarmonyFinding:
        
        model_params = ModelParameters(
            temperature=temperature,
            reasoning_level=reasoning_level,
            max_output_tokens=max_tokens
        )
        
        model_info = ModelInfo(
            name=model_name,
            version=model_version,
            provider="groq",
            parameters=model_params
        )
        
        environment = Environment(endpoint="groq api")
        
        issue_summary = IssueSummary(
            title=issue_title,
            topic_area=attack_type,
            overview=overview,
            desired_behavior=desired_behavior,
            observed_behavior=observed_behavior,
            self_assessed_severity=str(severity),
            self_assessed_severity_justification=severity_justification,
            self_assessed_breadth=str(breadth),
            self_assessed_breadth_justification=breadth_justification
        )
        
        return HarmonyFinding(
            issue_title=issue_title,
            model=model_info,
            environment=environment,
            issue_summary=issue_summary,
            harmony_response_walkthroughs=[conversation_walkthrough],
            steps_to_reproduce=reproduction_steps,
            notes=notes
        )
    
    @staticmethod
    def to_json(finding: HarmonyFinding, indent: int = 2) -> str:
        """Convert finding to JSON string"""
        return json.dumps(asdict(finding), indent=indent, ensure_ascii=False)
    
    @staticmethod
    def save_finding(finding: HarmonyFinding, filename: str) -> None:
        """Save finding to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(OutputFormatter.to_json(finding))
    
    @staticmethod
    def load_finding(filename: str) -> HarmonyFinding:
        """Load finding from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruct the dataclass from dict
        return HarmonyFinding(
            schema_version=data.get("schema_version", "1.0.0"),
            issue_title=data.get("issue_title", ""),
            model=ModelInfo(**data["model"]) if "model" in data else None,
            environment=Environment(**data["environment"]) if "environment" in data else None,
            issue_summary=IssueSummary(**data["issue_summary"]) if "issue_summary" in data else None,
            harmony_response_walkthroughs=data.get("harmony_response_walkthroughs", []),
            steps_to_reproduce=data.get("steps_to_reproduce", []),
            notes=data.get("notes", "")
        )
    
    @staticmethod
    def create_filename(attack_type: str, model_name: str, timestamp: Optional[str] = None) -> str:
        """Generate standardized filename for findings"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean model name for filename
        clean_model = model_name.replace("/", "_").replace("-", "_")
        clean_attack = attack_type.lower().replace(" ", "_").replace("-", "_")
        
        return f"{clean_attack}_{clean_model}_{timestamp}.json"

# Example usage and helper functions
class FindingBuilder:
    """Builder pattern for creating findings more easily"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._issue_title = ""
        self._model_name = "gpt-oss-20b"
        self._model_version = datetime.now().strftime("%Y-%m-%d")
        self._attack_type = ""
        self._overview = ""
        self._observed_behavior = ""
        self._desired_behavior = ""
        self._severity = 0
        self._severity_justification = ""
        self._breadth = 0
        self._breadth_justification = ""
        self._conversation_walkthrough = ""
        self._reproduction_steps = []
        self._notes = ""
        self._temperature = 1.0
        self._max_tokens = 1024
        self._reasoning_level = "low"
        return self
    
    def title(self, title: str):
        self._issue_title = title
        return self
    
    def model(self, name: str, version: str = None):
        self._model_name = name
        if version:
            self._model_version = version
        return self
    
    def attack(self, attack_type: str):
        self._attack_type = attack_type
        return self
    
    def overview(self, text: str):
        self._overview = text
        return self
    
    def observed(self, behavior: str):
        self._observed_behavior = behavior
        return self
    
    def desired(self, behavior: str):
        self._desired_behavior = behavior
        return self
    
    def severity(self, level: int, justification: str):
        self._severity = level
        self._severity_justification = justification
        return self
    
    def breadth(self, level: int, justification: str):
        self._breadth = level
        self._breadth_justification = justification
        return self
    
    def walkthrough(self, conversation: str):
        self._conversation_walkthrough = conversation
        return self
    
    def steps(self, steps: List[str]):
        self._reproduction_steps = steps
        return self
    
    def notes(self, text: str):
        self._notes = text
        return self
    
    def parameters(self, temperature: float = 1.0, max_tokens: int = 1024, reasoning_level: str = "low"):
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._reasoning_level = reasoning_level
        return self
    
    def build(self) -> HarmonyFinding:
        return OutputFormatter.create_finding(
            self._issue_title,
            self._model_name,
            self._model_version,
            self._attack_type,
            self._overview,
            self._observed_behavior,
            self._desired_behavior,
            self._severity,
            self._severity_justification,
            self._breadth,
            self._breadth_justification,
            self._conversation_walkthrough,
            self._reproduction_steps,
            self._notes,
            self._temperature,
            self._max_tokens,
            self._reasoning_level
        )