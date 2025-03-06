import csv
import json
import openai
from keys import chave_openai
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Configuração da API
openai.api_key = chave_openai

TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO = {
    "Colagem de Filme (Normal)": {"Filme": 1.03, "Cola Una": 60},  # Aplicação do Filme
    "Corte de Isopor": {},  # Corte do EPS (CNC – Corte Reto e Esquadro)
    "Pintura Eletrostática": {"Pó para Pintura": 140},  # Pintura Eletrostática
    "Colagem de Cola Mel": {"Cola Mel": 40},  # Montagem de Telhas
}

def extrair_info_material(tarefa_text, material_gasto_text):
    """
    Utiliza a API do GPT para normalizar a tarefa e extrair:
      - o nome da tarefa normalizada (deve ser uma das chaves da tabela),
      - o nome do material específico (se aplicável),
      - o valor numérico referente ao material gasto.
    Retorna um tuple (tarefa_normalizada, material, material_usado).
    """
    prompt = (
        "Você é um assistente que extrai informações numéricas e normaliza nomes de tarefas. "
        "A partir dos dados a seguir, extraia e retorne um JSON com as seguintes chaves:\n"
        " - tarefa: a tarefa normalizada (deve ser uma das opções: "
        f"{', '.join(TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO.keys())})\n"
        " - material: o nome do material correspondente, se aplicável. Se a tarefa tiver mais de um material esperado, "
        "escolha aquele que melhor corresponda ao valor numérico fornecido.\n"
        " - material_usado: o valor numérico referente ao material gasto.\n\n"
        f"Tarefa: {tarefa_text}\n"
        f"Material Gasto: {material_gasto_text}\n\n"
        "Responda apenas com o JSON."
    )
    
    try:
        print("Iniciando a chamada para a API GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que extrai informações numéricas de textos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        print("Resposta da API recebida:", response)
        resposta_texto = response["choices"][0]["message"]["content"].strip()
        print("Resposta do GPT:", resposta_texto)
        dados = json.loads(resposta_texto)
        tarefa_normalizada = dados.get("tarefa", tarefa_text)
        material = dados.get("material", "")  # Pode ser vazio se não aplicável
        material_usado = float(dados.get("material_usado", 0))
        print(f"Tarefa normalizada: {tarefa_normalizada}, Material: {material}, Material Usado: {material_usado}")
    except Exception as e:
        print(f"Erro ao extrair info via GPT: {e}")
        tarefa_normalizada = tarefa_text
        material = ""
        try:
            material_usado = float(material_gasto_text)
        except Exception:
            material_usado = 0
        print(f"Tarefa normalizada (fallback): {tarefa_normalizada}, Material: {material}, Material Usado: {material_usado}")
    return tarefa_normalizada, material, material_usado

def gerar_pdf_material(dados, caminho_pdf):
    """Gera um PDF a partir dos dados de eficiência de material."""
    try:
        print(f"Iniciando a geração do PDF em {caminho_pdf}...")
        pdf = SimpleDocTemplate(caminho_pdf, pagesize=letter)
        # Cabeçalhos da tabela
        cabecalhos = ["Etapa", "Material", "Material Usado", "Material Esperado", "Diferença de Material", "Status"]
        
        # Prepara os dados para a tabela
        dados_tabela = [cabecalhos]
        for item in dados:
            linha = [
                item["Etapa"],
                item["Material"],
                item["Material Usado"],
                item["Material Esperado"],
                item["Diferença de Material"],
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

def calcular_eficiencia_material(caminho_csv):
    """
    Calcula a eficiência do material usado com base no arquivo CSV e na tabela de material esperado.
    Utiliza a API do GPT para extrair e normalizar as informações de 'Tarefa' e 'Material Gasto',
    identificando também o material específico, se aplicável.
    Multiplica o valor esperado unitário pelo valor extraído da coluna "Metros Quadrados".
    """
    resultados = []

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("Cabeçalhos do CSV:", reader.fieldnames)

        for linha in reader:
            tarefa_text = linha.get('Tarefa')
            material_gasto_text = linha.get('Material Gasto')
            metros_quadrados_text = linha.get('Metros Quadrados', '1')  # Assume 1 se não existir
            print(f"\nProcessando tarefa: {tarefa_text}")

            # Extrai e normaliza informações usando a API do GPT
            tarefa_normalizada, material, material_usado = extrair_info_material(tarefa_text, material_gasto_text)
            print(f"Tarefa normalizada: {tarefa_normalizada}, Material: {material}, Material Usado: {material_usado}")

            # Extrai o valor numérico dos metros quadrados
            try:
                metros_quadrados = float(''.join(ch for ch in metros_quadrados_text if ch.isdigit() or ch == '.'))
                print(f"Metros quadrados extraídos: {metros_quadrados}")
            except Exception as e:
                print(f"Erro ao extrair metros quadrados: {e}")
                metros_quadrados = 1

            # Se houver material esperado para a tarefa, multiplica pelo valor dos metros quadrados
            if tarefa_normalizada in TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO:
                esperado = TABELA_MATERIAL_ESPERADO_POR_METRO_QUADRADO[tarefa_normalizada]
                print(f"Material esperado para a tarefa {tarefa_normalizada}: {esperado}")
                if isinstance(esperado, dict):
                    if material in esperado:
                        material_esperado_unitario = esperado[material]
                        print(f"Material esperado para {material}: {material_esperado_unitario}")
                    else:
                        try:
                            used_val = float(material_usado)
                            best_key = None
                            best_diff = None
                            for key, val in esperado.items():
                                diff = abs(used_val - val)
                                if best_diff is None or diff < best_diff:
                                    best_diff = diff
                                    best_key = key
                            if best_key is not None:
                                material = best_key
                                material_esperado_unitario = esperado[best_key]
                                print(f"Melhor material: {material}, Esperado: {material_esperado_unitario}")
                            else:
                                material_esperado_unitario = 0
                        except Exception:
                            material_esperado_unitario = 0
                elif isinstance(esperado, (int, float)):
                    material_esperado_unitario = esperado
                else:
                    material_esperado_unitario = 0

                # Multiplica o material esperado unitário pelo número de metros quadrados
                material_esperado = material_esperado_unitario * metros_quadrados
                print(f"Material esperado após multiplicação: {material_esperado}")

                if isinstance(material_esperado, (int, float)):
                    diferenca_material = material_usado - material_esperado
                    status = "Verde" if diferenca_material <= 0 else "Vermelho"
                else:
                    diferenca_material = "(a definir)"
                    status = "(Verde/Vermelho)"
            else:
                material_esperado = "(a definir)"
                diferenca_material = "(a definir)"
                status = "(Verde/Vermelho)"

            print(f"Diferença de material: {diferenca_material}, Status: {status}")
            
            resultados.append({
                "Etapa": tarefa_normalizada,
                "Material": material,
                "Material Usado": material_usado,
                "Material Esperado": material_esperado,
                "Diferença de Material": diferenca_material,
                "Status": status
            })

    return resultados

def salvar_csv_material(resultados, caminho_csv):
    """Salva os resultados de eficiência de material em um arquivo CSV."""
    try:
        with open(caminho_csv, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = resultados[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"✅ Relatório salvo com sucesso em CSV: {caminho_csv}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo CSV: {e}")

def gerar_relatorio_eficiencia_material(caminho_csv):
    caminho_csv = caminho_csv
    """
    Gera o relatório de eficiência de material:
      - Lê o CSV com as colunas: Horário de Início, Tarefa, Nome do Cliente, Horário de Fim, Material Gasto, Metros Quadrados.
      - Usa a API do GPT para extrair e normalizar as informações de 'Tarefa' e 'Material Gasto',
        comparando o valor extraído com o valor esperado (da tabela de referência).
      - Multiplica o valor esperado unitário pelo valor dos metros quadrados.
      - Gera um relatório (em PDF e CSV) com os resultados.
    """
      
    PDF_FILE = "data/relatorios/relatorio_eficiencia_material.pdf"
    CSV_FILE = "data/relatorios/relatorio_eficiencia_material.csv"

    relatorios = calcular_eficiencia_material(caminho_csv)
    print("Relatórios gerados:", relatorios)

    if relatorios:
        try:
            gerar_pdf_material(relatorios, PDF_FILE)
        except Exception as e:
            print(f"❌ Erro ao gerar o PDF: {e}")
        salvar_csv_material(relatorios, CSV_FILE)
    else:
        print("⚠️ Nenhum dado disponível para gerar o relatório de eficiência de material.")
