import csv
from datetime import datetime
import openai
from keys import chave_openai  # Certifique-se de que a chave da API está disponível
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Dicionário para converter números por extenso para dígitos
NUMBER_WORDS = {
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13,
    "catorze": 14, "quatorze": 14, "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18,
    "dezenove": 19, "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50
}

def token_para_numero(token):
    """Tenta converter um token (número em dígitos ou por extenso) para inteiro."""
    try:
        return int(token)
    except ValueError:
        return NUMBER_WORDS.get(token, None)

def parse_spoken_time(texto):
    """
    Converte uma string de horário falado em (hora, minuto).
    Exemplos:
      "oito e trinta e dois" -> (8, 32)
      "oito horas e trinta minutos" -> (8, 30)
    """
    # Converter para minúsculas e remover palavras irrelevantes e pontuações
    texto = texto.lower().replace("horas", "").replace("hora", "")
    texto = texto.replace("minutos", "").replace("minuto", "")
    texto = texto.replace(":", " ").replace(",", " ")
    
    # Separar tokens e remover conectivos comuns
    tokens = [t for t in texto.split() if t not in ["e", "de"]]
    if not tokens:
        raise ValueError("Nenhum token encontrado na entrada.")

    # Se existir pelo menos um token numérico já em dígito, use-o
    # Assumimos que o primeiro token é a hora e o restante representam os minutos
    # Exemplo: "8 trinta e dois" -> tokens: ["8", "trinta", "dois"]
    hora_token = tokens[0]
    hora = token_para_numero(hora_token)
    if hora is None:
        raise ValueError(f"Não foi possível interpretar a hora: {hora_token}")
    
    # Os tokens restantes serão interpretados como minuto
    minutos = 0
    if len(tokens) > 1:
        # Para compor o minuto, somamos os valores de cada token (ex: "trinta" + "dois" = 30 + 2)
        for token in tokens[1:]:
            valor = token_para_numero(token)
            if valor is None:
                raise ValueError(f"Não foi possível interpretar o token dos minutos: {token}")
            minutos += valor
    # Se não houver indicação dos minutos, assume 0
    return hora, minutos

def formatar_horario_tempo(horario):
    """
    Formata o horário para o formato 'YYYY-MM-DD HH:MM:SS' de forma inteligente,
    aceitando variações como "oito e trinta e dois" ou "8:30".
    """
    data_padrao = "2025-02-22"  # Data padrão, ajuste conforme necessário

    # Primeiro, tente tratar horários no formato numérico com separador ':'
    try:
        if ':' in horario:
            # Remove caracteres extras e normaliza
            horario_normalizado = horario.replace('h', ':').strip().rstrip('.')
            partes = horario_normalizado.split(':')
            if len(partes) == 1:
                horario_formatado = f"{data_padrao} {partes[0].zfill(2)}:00:00"
            elif len(partes) == 2:
                horario_formatado = f"{data_padrao} {partes[0].zfill(2)}:{partes[1].zfill(2)}:00"
            else:
                horario_formatado = f"{data_padrao} {partes[0].zfill(2)}:{partes[1].zfill(2)}:{partes[2].zfill(2)}"
            datetime.strptime(horario_formatado, "%Y-%m-%d %H:%M:%S")
            return horario_formatado
    except Exception as e:
        # Se falhar, tenta pelo parser inteligente
        pass

    # Se não estiver em formato numérico, usa o parser para entrada falada
    try:
        hora, minuto = parse_spoken_time(horario)
        horario_formatado = f"{data_padrao} {hora:02d}:{minuto:02d}:00"
        datetime.strptime(horario_formatado, "%Y-%m-%d %H:%M:%S")
        return horario_formatado
    except Exception as e:
        print(f"Erro ao formatar o horário: {horario}. {e}")
        return None

def calcular_tempo_gasto_tempo(horario_inicio, horario_fim):
    """Calcula o tempo gasto entre dois horários formatados."""
    inicio_formatado = formatar_horario_tempo(horario_inicio)
    fim_formatado = formatar_horario_tempo(horario_fim)

    if not inicio_formatado:
        print(f"Erro ao formatar o horário de início: {horario_inicio}")
        return 0
    if not fim_formatado:
        print(f"Erro ao formatar o horário de fim: {horario_fim}")
        return 0

    try:
        inicio = datetime.strptime(inicio_formatado, "%Y-%m-%d %H:%M:%S")
        fim = datetime.strptime(fim_formatado, "%Y-%m-%d %H:%M:%S")
        tempo_gasto = (fim - inicio).total_seconds() / 60  # Em minutos
        if tempo_gasto < 0:
            print(f"Erro: O tempo gasto é negativo. Início: {inicio_formatado}, Fim: {fim_formatado}")
            return 0
        print(f"Tempo Gasto calculado: {tempo_gasto} minutos")
        return tempo_gasto
    except Exception as e:
        print(f"Erro ao calcular o tempo gasto: {e}")
        return 0

def gerar_pdf_tempo(dados, caminho_pdf):
    """Gera um PDF a partir dos dados de eficiência."""
    try:
        pdf = SimpleDocTemplate(caminho_pdf, pagesize=letter)

        # Cabeçalhos da tabela
        cabecalhos = ["Etapa", "Tempo Gasto (min)", "Tempo Esperado (min)", "Diferença de Tempo", "Status"]
        dados_tabela = [cabecalhos]
        for item in dados:
            linha = [
                item["Etapa"],
                item["Tempo Gasto (min)"],
                item["Tempo Esperado (min)"],
                item["Diferença de Tempo"],
                item["Status"]
            ]
            dados_tabela.append(linha)

        tabela = Table(dados_tabela)
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        tabela.setStyle(estilo)

        pdf.build([tabela])
        print(f"✅ PDF gerado com sucesso: {caminho_pdf}")
    except Exception as e:
        print(f"❌ Erro ao gerar o PDF: {e}")

# Definindo os parâmetros de tempo esperado para cada tarefa (em minutos)
TABELA_TEMPO_ESPERADO = {
    "Aplicação do Filme": 0.3,                     
    "Corte do EPS (CNC – Corte Reto)": 5,          
    "Corte do EPS (CNC – Corte com Esquadro)": 8.75,
    "Pintura Eletrostática": 1.2,                  
    "Montagem de Telhas": 0.8
}
def encontrar_tarefa_padrao(tarefa):
    """
    Procura uma chave na TABELA_TEMPO_ESPERADO que esteja contida (case-insensitive)
    na string da tarefa. Retorna a chave encontrada ou None se não encontrar.
    """
    tarefa_lower = tarefa.lower()
    for chave in TABELA_TEMPO_ESPERADO:
        if chave.lower() in tarefa_lower:
            return chave
    return None

def calcular_eficiencia_tempo(caminho_csv):
    """Calcula a eficiência com base no arquivo CSV e na tabela de tempo esperado."""
    resultados = []

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("Cabeçalhos do CSV:", reader.fieldnames)  # Debug: mostra os cabeçalhos do CSV

        for linha in reader:
            tarefa = linha['Tarefa']
            tempo_inicial = linha['Horário de Início']
            tempo_final = linha['Horário de Fim']
            print(f"\nProcessando tarefa: {tarefa}")

            # Calcula o tempo gasto (em minutos) com base nos horários
            tempo_gasto = calcular_tempo_gasto_tempo(tempo_inicial, tempo_final)
            print(f"Tempo Gasto: {tempo_gasto} minutos")

            # Tenta extrair o valor numérico de "Metros Quadrados"
            metros_quadrados_str = linha.get('Metros Quadrados', '')
            try:
                # Se estiver vazio, usa valor padrão 1
                metros_quadrados = float(''.join(ch for ch in metros_quadrados_str if ch.isdigit() or ch == '.')) if metros_quadrados_str.strip() else 1
            except Exception as e:
                print(f"Erro ao extrair metros quadrados: {e}")
                metros_quadrados = 1  # Valor padrão

            # Verifica se a tarefa corresponde a uma das chaves esperadas usando substring
            chave_tarefa = encontrar_tarefa_padrao(tarefa)
            if chave_tarefa:
                tempo_esperado_unitario = TABELA_TEMPO_ESPERADO[chave_tarefa]
                # Calcula o tempo esperado multiplicando pelo número de metros quadrados
                tempo_esperado = tempo_esperado_unitario * metros_quadrados
                print(f"Tempo Esperado para '{chave_tarefa}' ({metros_quadrados} unidades): {tempo_esperado} minutos")

                diferenca_tempo = tempo_gasto - tempo_esperado
                status = "Verde" if diferenca_tempo <= 0 else "Vermelho"

                resultados.append({
                    "Etapa": chave_tarefa,
                    "Tempo Gasto (min)": tempo_gasto,
                    "Tempo Esperado (min)": tempo_esperado,
                    "Diferença de Tempo": diferenca_tempo,
                    "Status": status
                })
            else:
                print(f"A tarefa '{tarefa}' não corresponde a nenhuma chave esperada na tabela.")

    return resultados

def salvar_csv_tempo(resultados, caminho_csv):
    """Salva os resultados de eficiência em um arquivo CSV."""
    try:
        with open(caminho_csv, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = resultados[0].keys()  # Usa as chaves do primeiro dicionário como cabeçalhos
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"✅ Relatório salvo com sucesso em CSV: {caminho_csv}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo CSV: {e}")

def gerar_relatorio_eficiencia_tempo(caminho_csv):
    """Gera o relatório de eficiência e chama as funções para gerar o PDF e salvar em CSV."""
    PDF_FILE = "data/relatorios/relatorio_eficiencia.pdf"
    CSV_FILE = "data/relatorios/relatorio_eficiencia_tempo.csv"

    relatorios = calcular_eficiencia_tempo(caminho_csv)
    print("Relatórios gerados:", relatorios)

    if relatorios:
        try:
            gerar_pdf_tempo(relatorios, PDF_FILE)
        except Exception as e:
            print(f"❌ Erro ao gerar o PDF: {e}")
        salvar_csv_tempo(relatorios, CSV_FILE)
    else:
        print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência.")

# Exemplo de uso:
# Suponha que seu CSV contenha entradas como:
# Tarefa,Horário de Início,Horário de Fim,Metros Quadrados
# Montagem de Telhas,oito horas e trinta e dois,oito horas e cinquenta e dois,10
#
# Você pode chamar:
# gerar_relatorio_eficiencia_tempo("caminho/do/seu_arquivo.csv")
