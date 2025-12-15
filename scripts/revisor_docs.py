import os
import sys
import anthropic
from github import Github

def corrigir_frase(texto_original, client_anthropic):
    """
    Envia a frase para o Claude para verificar voz passiva.
    Retorna o texto corrigido ou o original se não houver mudança.
    """
    # Ignora linhas muito curtas, títulos, blocos de código ou itens de lista simples
    if len(texto_original.strip()) < 10 or texto_original.strip().startswith(('#', '```', '![', '<')):
        return texto_original

    prompt = f"""
    Atue como um Editor Técnico (Technical Writer).
    Analise a frase abaixo. Se ela estiver na VOZ PASSIVA, reescreva para VOZ ATIVA.
    Assuma que o sujeito é "you" (o usuário/leitor) se estiver oculto.
    
    Regras CRÍTICAS:
    1. Se a frase já estiver na voz ativa, retorne EXATAMENTE o texto original, sem mudar nada.
    2. Se mudar, retorne APENAS o novo texto corrigido.
    3. Mantenha a formatação Markdown (negrito, itálico, links) INTACTA.
    
    Frase: "{texto_original.strip()}"
    """
    
    try:
        message = client_anthropic.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        texto_novo = message.content[0].text.strip()
        
        # Validação extra: se o texto for igual, retorna original
        if texto_novo == texto_original.strip():
            return texto_original
            
        return texto_novo
    except Exception as e:
        print(f"⚠️ Erro ao consultar Claude: {e}")
        return texto_original

def main():
    # 1. Validar Variáveis de Ambiente
    github_token = os.getenv("GITHUB_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    
    # O arquivo vem como argumento do comando python
    if len(sys.argv) < 2:
        print("❌ Erro: Caminho do arquivo não fornecido.")
        sys.exit(1)
        
    arquivo_path = sys.argv[1]

    if not (github_token and anthropic_key and repo_name and pr_number):
        print("❌ Erro: Variáveis de ambiente faltando (GITHUB_TOKEN, ANTHROPIC_API_KEY, PR_NUMBER).")
        sys.exit(1)

    print(f"🔍 Iniciando análise de: {arquivo_path}")

    # 2. Inicializar Clientes
    try:
        gh = Github(github_token)
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        claude = anthropic.Anthropic(api_key=anthropic_key)
        
        # Pega o último commit para atrelar o comentário a ele
        # Isso garante que o comentário apareça na versão atual do PR
        commits = list(pr.get_commits())
        last_commit = commits[-1]
    except Exception as e:
        print(f"❌ Erro ao conectar com GitHub: {e}")
        sys.exit(1)

    # 3. Ler o arquivo
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado no disco: {arquivo_path}")
        sys.exit(1)

    # 4. Processar Linha a Linha
    sugestoes_feitas = 0
    
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        
        # Pula linhas vazias
        if not linha_limpa:
            continue

        novo_texto = corrigir_frase(linha, claude)

        # Se houve correção
        if novo_texto != linha_limpa:
            print(f"💡 Sugestão na linha {i+1}:")
            print(f"   🔴 {linha_limpa}")
            print(f"   🟢 {novo_texto}")

            body_suggestion = f"""
**Sugestão de Voz Ativa (AI)** 🤖

```suggestion
{novo_texto}
```
"""
            try:
                # Tenta postar o comentário na linha específica
                # create_review_comment exige commit_id, path e line (ou position)
                pr.create_review_comment(
                    body=body_suggestion,
                    commit_id=last_commit,
                    path=arquivo_path,
                    line=i + 1 # GitHub lines são 1-based
                )
                sugestoes_feitas += 1
            except Exception as e:
                # O GitHub só permite comentar em linhas que foram alteradas no PR (no diff).
                # Se a linha não faz parte do diff, ele retorna erro. Isso é normal.
                print(f"⚠️ Pulei a linha {i+1} (provavelmente não foi alterada neste PR): {e}")

    if sugestoes_feitas == 0:
        print("✅ Nenhuma correção aplicável encontrada nas linhas alteradas.")
    else:
        print(f"🚀 {sugestoes_feitas} comentários postados com sucesso!")

if __name__ == "__main__":
    main()