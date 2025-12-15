import os
import sys
import anthropic
from github import Github
from github import Auth

def corrigir_frase(texto_original, client_anthropic):
    """
    Envia a frase para o Claude. Retorna o texto original se der erro ou se não houver mudança.
    """
    # Ignora linhas curtas, títulos, ou linhas que parecem código/comentários
    if len(texto_original.strip()) < 10 or texto_original.strip().startswith(('#', '```', '![', '<', '>', '-')):
        return texto_original

    prompt = f"""
    Atue como um Editor Técnico. Analise a frase abaixo.
    Se estiver na VOZ PASSIVA, reescreva para VOZ ATIVA (assuma "you" como sujeito).
    
    Regras:
    1. Se já estiver na voz ativa, retorne EXATAMENTE o texto original.
    2. Mantenha formatação Markdown.
    3. NÃO explique, apenas retorne o texto.
    
    Frase: "{texto_original.strip()}"
    """
    
    try:
        # MUDANÇA: Usando Claude 3 Haiku (versão estável e universalmente disponível)
        message = client_anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        texto_novo = message.content[0].text.strip()
        
        # Se a IA devolver o mesmo texto (ou vazio), ignoramos
        if texto_novo == texto_original.strip():
            return texto_original
            
        return texto_novo
    except Exception as e:
        # Se der erro na API, apenas logamos e seguimos sem quebrar o script
        print(f"⚠️ [Claude API Error] Linha ignorada: {e}")
        return texto_original

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    
    if len(sys.argv) < 2:
        print("❌ Erro: Caminho do arquivo não fornecido.")
        sys.exit(1)
    arquivo_path = sys.argv[1]

    if not (github_token and anthropic_key and repo_name and pr_number):
        print("❌ Erro: Variáveis de ambiente faltando.")
        sys.exit(1)

    print(f"🔍 Iniciando análise de: {arquivo_path}")

    # Autenticação robusta
    auth = Auth.Token(github_token)
    gh = Github(auth=auth)
    
    try:
        repo = gh.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        claude = anthropic.Anthropic(api_key=anthropic_key)
        
        # Pega o último commit para comentar na versão correta do PR
        commits = list(pr.get_commits())
        last_commit = commits[-1]
    except Exception as e:
        print(f"❌ Erro ao conectar GitHub: {e}")
        sys.exit(1)

    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"❌ Arquivo local não encontrado: {arquivo_path}")
        sys.exit(1)

    sugestoes = 0
    
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        if not linha_limpa: 
            continue

        novo_texto = corrigir_frase(linha, claude)

        # Só comentamos se houver diferença REAL
        if novo_texto != linha_limpa:
            print(f"💡 Sugestão Linha {i+1}:")
            print(f"   🔴 {linha_limpa}")
            print(f"   🟢 {novo_texto}")

            body = f"""
**Sugestão de Voz Ativa (AI)** 🤖
```suggestion
{novo_texto}
```
"""
            try:
                # Usa 'commit' em vez de 'commit_id'
                pr.create_review_comment(
                    body=body,
                    commit=last_commit,
                    path=arquivo_path,
                    line=i + 1
                )
                sugestoes += 1
                print("   ✅ Comentário postado.")
            except Exception as e:
                print(f"   ⚠️ Não postado (Linha não alterada no PR ou erro API): {e}")

    if sugestoes == 0:
        print("✅ Nenhuma sugestão necessária.")
    else:
        print(f"🚀 {sugestoes} sugestões enviadas para o PR!")

if __name__ == "__main__":
    main()