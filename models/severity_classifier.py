"""
Severity Classification Model Module
"""

import logging
import json
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """Classifies emergency severity levels."""
    
    def __init__(self, llm_config: Dict[str, Any], prompt_template_path: str, rules_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.prompt_template_path = prompt_template_path
        self.rules_config = rules_config
        self.rules_cache = {}
        self.llm = self._create_llm()
        self.prompt_template = self._load_prompt_template()
        logger.info("Severity Classifier initialized")
    
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
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return PromptTemplate(
            template=template,
            input_variables=["language", "transcript", "incident_type", "severity_rules"]
        )
    
    def _load_rules(self, language: str) -> Dict[str, Any]:
        if language in self.rules_cache:
            return self.rules_cache[language]
        rules_path = self.rules_config.get(language, {}).get("severity_rules")
        if not rules_path:
            raise ValueError(f"No severity rules configured for language: {language}")
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        self.rules_cache[language] = rules
        return rules
    
    def _format_rules_for_prompt(self, rules: Dict[str, Any]) -> str:
        severity_levels = rules.get("severity_levels", [])
        formatted = "Available Severity Levels:\n"
        for level in severity_levels:
            formatted += f"- {level['level']}: {level['description']}\n"
        return formatted
    
    def classify(self, transcript: str, incident_type: str, language: str = "en") -> Dict[str, Any]:
        try:
            rules = self._load_rules(language)
            rules_text = self._format_rules_for_prompt(rules)
            prompt = self.prompt_template.format(
                language=language,
                transcript=transcript,
                incident_type=incident_type,
                severity_rules=rules_text
            )
            response = self.llm.invoke(prompt)
            try:
                result = json.loads(response.content)
            except:
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                result = json.loads(json_match.group()) if json_match else {}
            return result
        except Exception as e:
            logger.error(f"Severity classification failed: {e}")
            return {
                "severity_level": "MEDIUM",
                "confidence": 0.0,
                "reasoning": str(e),
                "urgency_indicators": []
            }


def create_severity_classifier(config: Dict[str, Any]) -> SeverityClassifier:
    return SeverityClassifier(
        llm_config=config.get("models", {}).get("llm", {}),
        prompt_template_path=config.get("prompts", {}).get("severity_classification"),
        rules_config=config.get("rules", {}).get("languages", {})
    )
