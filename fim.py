import openai
import csv
import os
from keys import chave_openai
from transcrever_audio import transcrever_audio
from datetime import datetime

# Configuração da chave da API
openai.api_key = chave_openai  

# Criar diretório caso não exista
os.makedirs("data/relatorios", exist_ok=True)

# Nome do arquivo CSV com data atual
data_atual = datetime.now().strftime("%Y-%m-%d")
CSV_FILE = f"data/relatorios/relatorio_{data_atual}.csv"

# Garante que o cabeçalho do CSV seja escrito apenas se o arquivo não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Horário de Início", "Tarefa", "Nome do Cliente",
            "Horário de Fim", "Material Gasto", "Metros Quadrados"
        ])

def organiza_fim(texto):
    """
    Utiliza o GPT para extrair informações sobre término da tarefa, materiais gastos,
    metros quadrados e horário de fim.
    O GPT deve retornar o texto no formato:
    "Tarefa de (tarefa), do cliente (nome do cliente), foi gasto (material gasto),
    foi feito (metros quadrados), terminou na hora (hora de término)"
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Leia o texto e extraia as seguintes informações no formato: "
                        "'Tarefa de (tarefa), do cliente (nome do cliente), foi gasto (material gasto), "
                        "foi feito (metros quadrados), terminou na hora (hora de término)'. "
                        "Considere diferentes formas de falar a hora, por exemplo: 9 e 39 = 9:39 = 9 horas e 39 minutos, etc. "
                        "Se alguma informação estiver faltando, diga: 'Faltando: (a, b, c...)'."
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        resposta_texto = resposta["choices"][0]["message"]["content"].strip()

        # Extraindo informações usando o formato esperado, dividindo em 5 partes
        partes = resposta_texto.split(", ")
        dados = {
            "Tarefa": "",
            "Nome do Cliente": "",
            "Material Gasto": "",
            "Metros Quadrados": "",
            "Horário de Fim": ""
        }

        if len(partes) >= 5:
            dados["Tarefa"] = partes[0].replace("Tarefa de ", "").strip() \
                                if "Tarefa de " in partes[0] else ""
            dados["Nome do Cliente"] = partes[1].replace("do cliente ", "").strip() \
                                if "do cliente " in partes[1] else ""
            dados["Material Gasto"] = partes[2].replace("foi gasto ", "").strip() \
                                if "foi gasto " in partes[2] else ""
            dados["Metros Quadrados"] = partes[3].replace("foi feito ", "").strip() \
                                if "foi feito " in partes[3] else ""
            dados["Horário de Fim"] = partes[4].replace("terminou na hora ", "").strip() \
                                if "terminou na hora " in partes[4] else ""
        else:
            # Se não houver 5 partes, tenta extrair individualmente
            for parte in partes:
                if "Tarefa de " in parte:
                    dados["Tarefa"] = parte.replace("Tarefa de ", "").strip()
                elif "do cliente " in parte:
                    dados["Nome do Cliente"] = parte.replace("do cliente ", "").strip()
                elif "foi gasto " in parte:
                    dados["Material Gasto"] = parte.replace("foi gasto ", "").strip()
                elif "foi feito " in parte:
                    dados["Metros Quadrados"] = parte.replace("foi feito ", "").strip()
                elif "terminou na hora " in parte:
                    dados["Horário de Fim"] = parte.replace("terminou na hora ", "").strip()

        # Ajusta a formatação do horário de fim se necessário
        horario_fim = dados["Horário de Fim"]
        if horario_fim and len(horario_fim) == 2:
            dados["Horário de Fim"] = f"0h{horario_fim}"
        else:
            dados["Horário de Fim"] = horario_fim.strip() if horario_fim else ""

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
                linha[4].strip() == "" and
                linha[5].strip() == ""
            ):
                linha[3] = dados["Horário de Fim"]        # Preenche Horário de Fim
                linha[4] = dados["Material Gasto"]          # Preenche Material Gasto
                linha[5] = dados["Metros Quadrados"]        # Preenche Metros Quadrados

            linhas_atualizadas.append(linha)

        # Reescreve o arquivo CSV atualizado
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)         # Escreve o cabeçalho
            writer.writerows(linhas_atualizadas)  # Escreve os dados atualizados

        return resposta_texto  # Retorna o texto formatado para conferência

    except openai.error.OpenAIError as e:
        return f"Erro na API OpenAI: {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"
