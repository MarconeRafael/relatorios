# Relatórios Automáticos com OpenAI e Transcrição de Áudio

Este projeto utiliza a API da OpenAI para transcrever áudios e gerar relatórios organizados automaticamente. O áudio é processado e convertido em um relatório estruturado, que é salvo em um arquivo CSV. Além disso, ele calcula a eficiência das tarefas realizadas e gera gráficos com base nos dados coletados.

## 📂 Estrutura do Diretório

O projeto está organizado da seguinte maneira:

```
relatorios/
│── data/                  # Diretório para armazenar arquivos de áudio e relatórios
│   ├── WhatsApp Ptt 2025-02-22 at 08.54.35.ogg  # Exemplo de áudio
│   ├── relatorios.csv     # Arquivo onde os relatórios de eficiência são armazenados
│   ├── relatorio_eficiencia.csv  # Relatório de eficiência detalhado
│── ├── relatorio_eficiencia.pdf  # PDF do relatório de eficiência
│── ├── keys.py            # Arquivo contendo a chave da API OpenAI
│── ├── LICENSE            # Licença do projeto
│── ├── inicio.py          # Código para organizar e salvar o relatório
│── ├── transcrever_audio.py   # Código para transcrever o áudio
│── ├── eficiencia.py      # Código para calcular a eficiência e gerar PDFs/CSV
│── ├── graficos.py        # Código para gerar gráficos com os dados de eficiência
│── ├── README.md          # Este arquivo
│── ├── __pycache__/       # Cache de compilação do Python
│── ├── venv/              # Ambiente virtual para dependências
```

## 🚀 Como Usar

### 1️⃣ **Instalar as Dependências**
Antes de começar, ative o ambiente virtual e instale as bibliotecas necessárias:

```bash
source venv/bin/activate  # Ativar o ambiente virtual (Linux/macOS)
pip install openai pydub matplotlib seaborn  # Instalar as dependências necessárias
```

### 2️⃣ **Configurar a Chave da API**
Edite o arquivo `keys.py` e adicione sua chave da OpenAI:

```python
chave_openai = "SUA_CHAVE_AQUI"
```

### 3️⃣ **Transcrever e Processar um Áudio**
Para transcrever um áudio e gerar o relatório:

```python
from transcrever_audio import transcrever_audio
from inicio import organiza

# Caminho do arquivo de áudio
path = "data/WhatsApp Ptt 2025-02-22 at 08.54.35.ogg"

# Transcrevendo o áudio
texto = transcrever_audio(path)

# Gerando o relatório e salvando no CSV
relatorio = organiza(texto)

# Exibindo o resultado
print(relatorio)
```

### 4️⃣ **Calcular a Eficiência e Gerar Relatórios**
Para calcular a eficiência das tarefas e gerar gráficos:

```python
from eficiencia import gerar_relatorio_eficiencia
from graficos import gerar_graficos

# Gerando o relatório de eficiência
gerar_relatorio_eficiencia()

# Gerando os gráficos a partir dos dados de eficiência
gerar_graficos()
```

### 5️⃣ **Saída Esperada**
Após rodar o código, um relatório formatado será salvo em `relatorio_eficiencia.csv`, com as colunas:

```
Etapa, Tempo Gasto (min), Tempo Esperado (min), Diferença de Tempo, Status
```

Além disso, um PDF (relatorio_eficiencia.pdf) e gráficos correspondentes serão gerados e salvos na pasta apropriada.

## 📜 Licença

Este projeto está licenciado sob a licença Apache 2.0. Consulte o arquivo `LICENSE` para mais detalhes.
