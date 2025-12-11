"""
Translation Model Module

Handles text translation using LLM-based approach for high-quality,
context-aware translations in emergency dispatch scenarios.
"""

import logging
from typing import Dict, Any, Optional

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class TranslationModel:
    """LLM-based translation model for emergency dispatch text."""

    def __init__(self, llm_config: Dict[str, Any], prompt_template_path: str):
        """
        Initialize the Translation Model.

        Args:
            llm_config: LLM configuration dictionary
            prompt_template_path: Path to the translation prompt template
        """
        self.llm_config = llm_config
        self.prompt_template_path = prompt_template_path
        self.llm = self._create_llm()
        self.prompt_template = self._load_prompt_template()
        logger.info("Translation Model initialized")

    def _create_llm(self):
        """Create LLM instance based on configuration."""
        provider = self.llm_config.get("provider", "openai")
        if provider == "openai":
            # Use GPT-4o-mini for cost-effective, high-quality translation
            return ChatOpenAI(
                model=self.llm_config.get("translation_model", "gpt-4o-mini"),
                temperature=self.llm_config.get("translation_temperature", 0.3),
                max_tokens=self.llm_config.get("translation_max_tokens", 2000)
            )
        raise ValueError(f"Unsupported LLM provider: {provider}")

    def _load_prompt_template(self) -> PromptTemplate:
        """Load translation prompt template from file."""
        try:
            with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return PromptTemplate(
                template=template,
                input_variables=["source_language", "target_language", "text"]
            )
        except FileNotFoundError:
            logger.warning(f"Translation prompt template not found at {self.prompt_template_path}, using default")
            return self._get_default_prompt_template()
        except Exception as e:
            logger.error(f"Failed to load translation prompt template: {e}")
            return self._get_default_prompt_template()

    def _get_default_prompt_template(self) -> PromptTemplate:
        """Get default translation prompt template."""
        default_template = """You are a professional translator specializing in emergency dispatch communications.

Translate the following text accurately while preserving:
- The original meaning and tone
- Emergency-related terminology
- Urgency indicators
- Context and nuance

Source Language: {source_language}
Target Language: {target_language}

Text to translate:
{text}

Provide ONLY the translated text without any explanations or metadata."""

        return PromptTemplate(
            template=default_template,
            input_variables=["source_language", "target_language", "text"]
        )

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code or name (e.g., 'ar', 'Arabic', 'en')
            source_language: Source language (optional, for context)

        Returns:
            Dictionary containing:
                - translated_text: The translated text
                - target_language: The target language
                - status: "success" or "error"
                - error: Error message (if status is "error")
        """
        try:
            logger.info(f"Translating text to {target_language}")

            # Format the prompt
            prompt_text = self.prompt_template.format(
                source_language=source_language if source_language else "auto-detected",
                target_language=target_language,
                text=text
            )

            # Call LLM for translation
            response = self.llm.invoke(prompt_text)
            translated_text = response.content.strip()

            logger.info("Translation completed successfully")

            return {
                "translated_text": translated_text,
                "target_language": target_language,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "translated_text": None,
                "target_language": target_language,
                "status": "error",
                "error": str(e)
            }

    def batch_translate(
        self,
        texts: list,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate multiple text segments.

        Args:
            texts: List of text strings to translate
            target_language: Target language code or name
            source_language: Source language (optional)

        Returns:
            Dictionary containing:
                - translated_texts: List of translated text strings
                - target_language: The target language
                - status: "success" or "error"
                - failed_indices: List of indices that failed to translate
        """
        try:
            logger.info(f"Batch translating {len(texts)} segments to {target_language}")

            translated_texts = []
            failed_indices = []

            for idx, text in enumerate(texts):
                result = self.translate(text, target_language, source_language)
                if result["status"] == "success":
                    translated_texts.append(result["translated_text"])
                else:
                    translated_texts.append(text)  # Keep original on failure
                    failed_indices.append(idx)

            logger.info(f"Batch translation completed: {len(texts) - len(failed_indices)}/{len(texts)} successful")

            return {
                "translated_texts": translated_texts,
                "target_language": target_language,
                "status": "success" if not failed_indices else "partial_success",
                "failed_indices": failed_indices
            }

        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            return {
                "translated_texts": texts,  # Return original texts on complete failure
                "target_language": target_language,
                "status": "error",
                "error": str(e),
                "failed_indices": list(range(len(texts)))
            }


def create_translation_model(config: Dict[str, Any]) -> TranslationModel:
    """
    Factory function to create TranslationModel instance.

    Args:
        config: Configuration dictionary

    Returns:
        TranslationModel instance
    """
    return TranslationModel(
        llm_config=config.get("models", {}).get("llm", {}),
        prompt_template_path=config.get("prompts", {}).get("translation", "config/prompts/translation_prompt.txt")
    )
