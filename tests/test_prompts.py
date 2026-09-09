"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
import re
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt v2 antes de cada teste."""
        prompts = load_prompts(PROMPT_FILE)
        assert prompts and PROMPT_KEY in prompts, (
            f"Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE}"
        )
        self.prompt_data = prompts[PROMPT_KEY]
        self.system_prompt = self.prompt_data.get("system_prompt", "") or ""
        self.user_prompt = self.prompt_data.get("user_prompt", "") or ""

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt_data, "Campo 'system_prompt' não encontrado"
        assert self.system_prompt.strip() != "", "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(r"voc[êe]\s+[ée]\s+(um|uma|o|a)\s+\w+", self.system_prompt, re.IGNORECASE), (
            "'system_prompt' não define uma persona explícita (ex: 'Você é um...')"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        texto = self.system_prompt + " " + self.user_prompt
        assert re.search(r"markdown", texto, re.IGNORECASE) or re.search(
            r"user story|como um.*eu quero.*para que", texto, re.IGNORECASE
        ), "'system_prompt'/'user_prompt' não exigem formato Markdown nem User Story padrão"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        assert re.search(r"exemplo", self.system_prompt, re.IGNORECASE), (
            "'system_prompt' não contém exemplos (Few-shot Learning)"
        )
        assert self.system_prompt.lower().count("exemplo") >= 2, (
            "'system_prompt' deve conter pelo menos 2 exemplos de entrada/saída"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        texto = self.system_prompt + " " + self.user_prompt
        assert "[TODO]" not in texto and "TODO" not in texto, (
            "Foi encontrado um [TODO] pendente no prompt"
        )

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', encontradas: {len(techniques)}"
        )

    def test_prompt_structure_is_valid(self):
        """Valida a estrutura geral do prompt usando validate_prompt_structure (utils.py)."""
        is_valid, errors = validate_prompt_structure(self.prompt_data)
        assert is_valid, f"Prompt inválido: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])