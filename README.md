# Relatórios Automáticos com OpenAI e Transcrição de Áudio

Este projeto utiliza a API da OpenAI para transcrever áudios e gerar relatórios organizados automaticamente. O áudio é processado e convertido em um relatório estruturado, que é salvo em um arquivo CSV.

## 📂 Estrutura do Diretório

O projeto está organizado da seguinte maneira:

```
relatorios/
│── data/                  # Diretório para armazenar arquivos de áudio
│   ├── WhatsApp Ptt 2025-02-22 at 08.54.35.ogg  # Exemplo de áudio
│── keys.py                # Arquivo contendo a chave da API OpenAI
│── LICENSE                # Licença do projeto
│── organiza.py            # Código para organizar e salvar o relatório
│── transcrever_audio.py   # Código para transcrever o áudio
│── __pycache__/           # Cache de compilação do Python
│── venv/                  # Ambiente virtual para dependências
│── relatorios.csv         # Arquivo onde os relatórios são armazenados
```

## 🚀 Como Usar

### 1️⃣ **Instalar as Dependências**
Antes de começar, ative o ambiente virtual e instale as bibliotecas necessárias:

```bash
source venv/bin/activate  # Ativar o ambiente virtual (Linux/macOS)
pip install openai pydub  # Instalar as dependências necessárias
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
from organiza import organiza

# Caminho do arquivo de áudio
path = "data/WhatsApp Ptt 2025-02-22 at 08.54.35.ogg"

# Transcrevendo o áudio
texto = transcrever_audio(path)

# Gerando o relatório e salvando no CSV
relatorio = organiza(texto)

# Exibindo o resultado
print(relatorio)
```

### 4️⃣ **Saída Esperada**
Após rodar o código, um relatório formatado será salvo em `relatorios.csv`, com as colunas:

```
Horário de Início, Tarefa, Nome do Cliente, Serviço, Horário de Fim
```

O **horário de fim** permanecerá vazio até ser preenchido posteriormente.

## 📜 Licença

Este projeto está licenciado sob a licença Apache 2.0. Consulte o arquivo `LICENSE` para mais detalhes.
