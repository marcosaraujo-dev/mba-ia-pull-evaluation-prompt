"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (formato "{username}/bug_to_user_story_v2")
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])

    description = prompt_data.get("description", "")
    techniques = prompt_data.get("techniques_applied", [])
    if techniques:
        description = f"{description} | Técnicas: {', '.join(techniques)}"

    tags = prompt_data.get("tags", [])

    url = hub.push(
        prompt_name,
        prompt_template,
        new_repo_is_public=True,
        new_repo_description=description,
        tags=tags,
    )

    print(f"   ✓ Push realizado com sucesso: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    prompts_file = load_yaml(PROMPT_FILE)
    if not prompts_file or PROMPT_KEY not in prompts_file:
        print(f"❌ Prompt '{PROMPT_KEY}' não encontrado em {PROMPT_FILE}")
        return 1

    prompt_data = prompts_file[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("   ✓ Prompt validado com sucesso")

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{username}/{PROMPT_KEY}"

    try:
        push_prompt_to_langsmith(prompt_name, prompt_data)
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt '{prompt_name}': {e}")
        return 1

    print(f"✅ Prompt publicado como: {prompt_name}")
    print(f"   Confira em: https://smith.langchain.com/prompts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
