"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """
    Puxa o prompt de baixa qualidade do LangSmith Hub e monta a estrutura
    de dados a ser salva em YAML (mesmo formato do prompts/bug_to_user_story_v1.yml).

    Returns:
        Dicionário no formato esperado por save_yaml, ou None em caso de erro
    """
    print(f"   Puxando prompt do LangSmith Hub: {PROMPT_NAME}")
    prompt_template = hub.pull(PROMPT_NAME)

    system_prompt = prompt_template.messages[0].prompt.template
    user_prompt = prompt_template.messages[1].prompt.template

    print("   ✓ Prompt carregado com sucesso")

    return {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        prompt_data = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"❌ Erro ao puxar prompt '{PROMPT_NAME}': {e}")
        return 1

    if not save_yaml(prompt_data, OUTPUT_PATH):
        return 1

    print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
