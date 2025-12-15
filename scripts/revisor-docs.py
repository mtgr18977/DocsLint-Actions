import os
import sys
import anthropic
import difflib

# Códigos de cor ANSI para o terminal ficar igual ao GitHub (Verde/Vermelho)
COR_VERMELHA = '\033[91m'
COR_VERDE = '\033[92m'
COR_RESET = '\033[0m'

def corrigir_texto_com_claude(texto_chunk, client):
    # Se for linha vazia ou muito curta, ignora para economizar tokens
    if len(texto_chunk.strip()) < 5:
        return texto_chunk

    prompt = f"""
    Você é um editor técnico (Technical Writer).
    Sua única tarefa é reescrever frases na VOZ PASSIVA para a VOZ ATIVA.
    Use "you" como sujeito se estiver implícito.
    Mantenha a formatação Markdown exata.
    Retorne APENAS o texto resultante.
    
    Texto: {texto_chunk}
    """
    
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Erro na API: {e}")
        return texto_chunk

def main():
    # 1. Configuração
    if len(sys.argv) < 2:
        print("Uso: python revisor_docs.py <arquivo.md>")
        return

    arquivo_entrada = sys.argv[1]
    
    # Pegando a chave da variável de ambiente ou input manual
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Erro: Defina a variável de ambiente ANTHROPIC_API_KEY")
        return

    client = anthropic.Anthropic(api_key=api_key)

    print(f"🔍 Analisando {arquivo_entrada} com Claude...\n")

    # 2. Lendo o arquivo original
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        linhas_originais = f.readlines()

    # 3. Processando (Vamos agrupar o texto para não chamar a API a cada linha)
    # Para simplificar este exemplo, vamos processar o arquivo inteiro como uma string,
    # mas em produção o ideal é dividir por parágrafos.
    texto_completo = "".join(linhas_originais)
    
    # Vamos dividir por linhas para mandar blocos para a IA (simulação simples)
    # Na prática, mandamos blocos maiores, mas aqui vamos iterar para ver o progresso
    linhas_corrigidas = []
    
    for linha in linhas_originais:
        nova_linha = corrigir_texto_com_claude(linha, client)
        linhas_corrigidas.append(nova_linha)
        # Feedback visual simples (ponto a cada linha processada)
        print(".", end="", flush=True)
    
    print("\n\n--- RELATÓRIO DE MUDANÇAS ---\n")

    # 4. Gerando o Diff (Comparação visual)
    diff = difflib.ndiff(linhas_originais, linhas_corrigidas)
    
    mudancas_encontradas = False
    
    for linha in diff:
        codigo = linha[0] # O primeiro caractere indica a mudança
        texto = linha[2:].rstrip() # O resto é o texto
        
        if codigo == '-': # Linha removida (Original)
            print(f"{COR_VERMELHA}- {texto}{COR_RESET}")
            mudancas_encontradas = True
        elif codigo == '+': # Linha adicionada (Correção)
            print(f"{COR_VERDE}+ {texto}{COR_RESET}")
            mudancas_encontradas = True
        elif codigo == ' ': # Linha sem alteração
            # Opcional: imprimir linhas que não mudaram em cinza ou branco
            # print(f"  {texto}") 
            pass

    if not mudancas_encontradas:
        print("✅ Nenhuma voz passiva detectada. O texto já está ótimo!")
    else:
        # Salvar o novo arquivo
        nome_saida = "corrigido_" + arquivo_entrada
        with open(nome_saida, 'w', encoding='utf-8') as f:
            f.writelines(linhas_corrigidas)
        print(f"\n💾 Arquivo corrigido salvo como: {nome_saida}")

if __name__ == "__main__":
    main()