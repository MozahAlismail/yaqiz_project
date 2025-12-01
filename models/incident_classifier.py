"""
Incident Classification Model Module
"""

import logging
import json
from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IncidentClassification(BaseModel):
    incident_type: str
    confidence: float
    reasoning: str
    keywords_found: List[str]


class IncidentClassifier:
    def __init__(self, llm_config: Dict[str, Any], prompt_template_path: str, rules_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.prompt_template_path = prompt_template_path
        self.rules_config = rules_config
        self.rules_cache = {}
        self.llm = self._create_llm()
        self.prompt_template = self._load_prompt_template()
        self.output_parser = JsonOutputParser(pydantic_object=IncidentClassification)
        logger.info("Incident Classifier initialized")
    
    def _create_llm(self):
        provider = self.llm_config.get("provider", "openai")
        if provider == "openai":
            return ChatOpenAI(
                model=self.llm_config.get("model_name", "gpt-4-turbo-preview"),
                temperature=self.llm_config.get("temperature", 0.1),
                max_tokens=self.llm_config.get("max_tokens", 500)
            )
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _load_prompt_template(self) -> PromptTemplate:
        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            template = f.read()
        return PromptTemplate(template=template, input_variables=["language", "transcript", "incident_rules"])
    
    def _load_rules(self, language: str) -> Dict[str, Any]:
        if language in self.rules_cache:
            return self.rules_cache[language]
        rules_path = self.rules_config.get(language, {}).get("incident_rules")
        if not rules_path:
            raise ValueError(f"No incident rules configured for language: {language}")
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
        self.rules_cache[language] = rules
        return rules
    
    def _format_rules_for_prompt(self, rules: Dict[str, Any]) -> str:
        incident_types = rules.get("incident_types", [])
        formatted = "Available Incident Types:"
        for incident in incident_types:
            formatted += f"- {incident['type']}: {incident['description']}"
        return formatted
    
    def classify(self, transcript: str, language: str = "en") -> Dict[str, Any]:
        try:
            rules = self._load_rules(language)
            rules_text = self._format_rules_for_prompt(rules)
            prompt = self.prompt_template.format(language=language, transcript=transcript, incident_rules=rules_text)
            response = self.llm.invoke(prompt)
            try:
                result = json.loads(response.content)
            except:
                import re
                json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
                result = json.loads(json_match.group()) if json_match else {}
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {"incident_type": "UNKNOWN", "confidence": 0.0, "reasoning": str(e), "keywords_found": []}


def create_incident_classifier(config: Dict[str, Any]) -> IncidentClassifier:
    return IncidentClassifier(
        llm_config=config.get("models", {}).get("llm", {}),
        prompt_template_path=config.get("prompts", {}).get("incident_classification"),
        rules_config=config.get("rules", {}).get("languages", {})
    )
