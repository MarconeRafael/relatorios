
import openai
import csv
import os
from keys import chave_openai
from transcrever_audio import transcrever_audio
from datetime import datetime
# Configuração da chave da API
openai.api_key = chave_openai  


# Nome do arquivo CSV com data atual
data_atual = datetime.now().strftime("%Y-%m-%d")
CSV_FILE = f"data/relatorios/relatorio_{data_atual}.csv"

# Garante que o cabeçalho do CSV seja escrito apenas se o arquivo não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Horário de Início", "Tarefa", "Nome do Cliente", "Horário de Fim", "Material Gasto"])

def organiza_fim(texto):
    """
    Utiliza o GPT para extrair informações sobre término da tarefa, materiais gastos e horário de fim.
    O GPT deve retornar o texto no formato:
    "Tarefa de (tarefa), do cliente (nome do cliente), foi gasto (material gasto), terminou na hora (hora de término)"
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Leia o texto e extraia as seguintes informações no formato: "
                        "'Tarefa de (tarefa), do cliente (nome do cliente), foi gasto (material gasto), terminou na hora (hora de término)'. "
                        "considere diferentes formas de falar a hora por exemplo 9 e 39 = 9:39 = 9 horas e 39 minutos etc"
                        "Se alguma informação estiver faltando, diga: 'Faltando: (a, b, c...)'."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        resposta_texto = resposta["choices"][0]["message"]["content"].strip()

        # Extraindo informações do texto usando a formatação esperada
        partes = resposta_texto.split(", ")
        dados = {chave: "" for chave in ["Nome do Cliente", "Tarefa", "Horário de Fim", "Material Gasto"]}

        try:
            dados["Tarefa"] = partes[0].split("Tarefa de ")[1] if "Tarefa de " in partes[0] else ""
            dados["Nome do Cliente"] = partes[1].split("do cliente ")[1] if "do cliente " in partes[1] else ""
            dados["Material Gasto"] = partes[2].split("foi gasto ")[1] if "foi gasto " in partes[2] else ""
            
            # Ajustando a extração do horário de fim
            horario_fim = partes[3].split("terminou na hora ")[1] if "terminou na hora " in partes[3] else ""
            
            # Corrigindo a extração da hora e minutos
            if horario_fim:
                # Adiciona o "h" se a hora estiver no formato de minutos
                if len(horario_fim) == 2:  # Exemplo: 39
                    dados["Horário de Fim"] = f"0h{horario_fim}"  # Como o horário 39 seria 0h39
                else:
                    dados["Horário de Fim"] = horario_fim.strip()
            else:
                dados["Horário de Fim"] = ""
                
        except IndexError:
            pass  # Mantém os campos vazios caso algo falte

        # Atualiza o CSV apenas nas linhas correspondentes
        linhas_atualizadas = []
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Lê o cabeçalho
            linhas = list(reader)

        for linha in linhas:
            # linha[1] -> Tarefa; linha[2] -> Nome do Cliente
            if (
                dados["Nome do Cliente"].strip().lower() in linha[2].strip().lower() and
                dados["Tarefa"].strip().lower() in linha[1].strip().lower() and
                linha[3].strip() == "" and
                linha[4].strip() == ""
            ):
                linha[3] = dados["Horário de Fim"]  # Preenche Horário de Fim
                linha[4] = dados["Material Gasto"]  # Preenche Material Gasto
            linhas_atualizadas.append(linha)

        # Reescreve o arquivo CSV atualizado
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Escreve o cabeçalho
            writer.writerows(linhas_atualizadas)  # Escreve os dados atualizados

        return resposta_texto  # Retorna o texto formatado para conferência

    except openai.error.OpenAIError as e:
        return f"Erro na API OpenAI: {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
