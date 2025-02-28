import openai
import csv
import os
from datetime import datetime
from keys import chave_openai
from transcrever_audio import transcrever_audio

# Configuração da chave da API
openai.api_key = chave_openai  

# Função para gerar o nome do arquivo com a data atual
def gerar_nome_relatorio():
    data_atual = datetime.now().strftime("%Y-%m-%d")  # Formato da data: "YYYY-MM-DD"
    return f"data/relatorios/relatorio_{data_atual}.csv"

# Nome do arquivo CSV com data atual
CSV_FILE = gerar_nome_relatorio()

# Garante que o cabeçalho do CSV seja escrito apenas se o arquivo não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Horário de Início", "Tarefa", "Nome do Cliente", "Horário de Fim", "Material Gasto"])

def organiza_inicio(texto):
    """
    Utiliza o GPT para determinar a intenção do texto e organizar a resposta no formato esperado.
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Leia o texto e extraia as seguintes informações no formato: "
                        "'Às (horário de início), início da tarefa (tarefa), "
                        "dando início ao cliente (nome do cliente)'. "
                        "Se alguma informação estiver faltando, diga: 'Faltando: (a, b, c...)'."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        resposta_texto = resposta["choices"][0]["message"]["content"].strip()
        
        # Extraindo informações do texto (supondo que o GPT sempre retorna no formato correto)
        partes = resposta_texto.split(", ")
        dados = {chave: "" for chave in ["Horário de Início", "Tarefa", "Nome do Cliente"]}

        try:
            dados["Horário de Início"] = partes[0].split("Às ")[1] if "Às " in partes[0] else ""
            dados["Tarefa"] = partes[1].split("início da tarefa ")[1] if "início da tarefa " in partes[1] else ""
            dados["Nome do Cliente"] = partes[2].split("dando início ao cliente ")[1] if "dando início ao cliente " in partes[2] else ""
        except IndexError:
            pass  # Se der erro, mantém os campos vazios

        # Salva os dados no CSV com as colunas "Horário de Fim" e "Material Gasto" vazias
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([dados["Horário de Início"], dados["Tarefa"], dados["Nome do Cliente"], "", ""])  
        
        return resposta_texto  # Retorna o texto formatado para conferência
    
    except openai.error.OpenAIError as e:
        return f"Erro na API OpenAI: {str(e)}"
    
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
