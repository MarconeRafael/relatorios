import openai
import csv
import os
import re
from datetime import datetime, timedelta
from keys import chave_openai

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

def parse_horario(horario_str, start_time_str):
    """
    Converte textos como "9 e 39", "9h39" ou "39" em "HHhMM".
    Se apenas minutos, calcula com base no horário de início.
    """
    try:
        # Tenta extrair horas e minutos com regex
        match = re.match(r'(\d{1,2})[hH :]*(?:e|:| e )? *(\d{2})', horario_str)
        if match:
            hora = int(match.group(1))
            minuto = int(match.group(2))
            return f"{hora}h{minuto:02d}"
        
        # Se for apenas minutos (ex: "39")
        elif horario_str.isdigit() and len(horario_str) == 2:
            start = datetime.strptime(start_time_str, "%Hh%M")
            minutos = int(horario_str)
            
            # Calcula se a hora deve incrementar
            if minutos < start.minute:
                hora_final = start.hour + 1
                if hora_final >= 24:
                    hora_final = 0
                return f"{hora_final}h{minutos:02d}"
            else:
                return f"{start.hour}h{minutos:02d}"
        
        # Caso padrão (retorna o valor original se não conseguir parsear)
        return horario_str
    
    except:
        return horario_str  # Fallback seguro

def organiza_fim(texto):
    """
    Extrai informações do término da tarefa com GPT e atualiza o CSV.
    """
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extraia as informações no formato: "
                        "'Tarefa de (tarefa), do cliente (nome do cliente), foi gasto (material gasto), terminou na hora (hora de término)'. "
                        "FORMATO DA HORA: SEMPRE 'HHhMM' (ex: 9h39). Se faltar dados, informe 'Faltando: ...'"
                    )
                },
                {"role": "user", "content": texto}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        resposta_texto = resposta["choices"][0]["message"]["content"].strip()
        partes = resposta_texto.split(", ")
        dados = {chave: "" for chave in ["Nome do Cliente", "Tarefa", "Horário de Fim", "Material Gasto"]}

        try:
            dados["Tarefa"] = partes[0].split("Tarefa de ")[1] if "Tarefa de " in partes[0] else ""
            dados["Nome do Cliente"] = partes[1].split("do cliente ")[1] if "do cliente " in partes[1] else ""
            dados["Material Gasto"] = partes[2].split("foi gasto ")[1] if "foi gasto " in partes[2] else ""
            dados["Horário de Fim"] = partes[3].split("terminou na hora ")[1] if "terminou na hora " in partes[3] else ""
        except IndexError:
            pass

        # Atualiza o CSV com parsing dinâmico do horário
        linhas_atualizadas = []
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)
            linhas = list(reader)

        for linha in linhas:
            if (
                dados["Nome do Cliente"].strip().lower() in linha[2].strip().lower() and
                dados["Tarefa"].strip().lower() in linha[1].strip().lower() and
                linha[3].strip() == "" and
                linha[4].strip() == ""
            ):
                # Parseia o horário de término com base no horário de início da linha
                horario_fim_parsed = parse_horario(dados["Horário de Fim"], linha[0])
                linha[3] = horario_fim_parsed
                linha[4] = dados["Material Gasto"]
            linhas_atualizadas.append(linha)

        # Reescreve o CSV
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(linhas_atualizadas)

        return resposta_texto

    except openai.error.OpenAIError as e:
        return f"Erro na API OpenAI: {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"