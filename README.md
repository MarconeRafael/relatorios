# Relatórios Automáticos com OpenAI e Transcrição de Áudio

Este projeto utiliza a API da OpenAI para transcrever áudios e gerar relatórios organizados automaticamente. Inclui uma interface web para upload de áudios, visualização de gráficos e geração de relatórios em PDF.

## 📂 Estrutura do Diretório

```
relatorios/
├── app.py                  # Aplicação Flask principal
├── main.py                 # Ponto de entrada alternativo
├── data/
│   ├── audios/            # Áudios enviados pelos usuários
│   ├── graficos/          # Gráficos gerados automaticamente
│   └── relatorios/        # Relatórios em CSV e PDF
├── eficiencia_material.py # Cálculos de eficiência de materiais
├── eficiencia_tempo.py    # Cálculos de eficiência temporal
├── gerar_pdf.py           # Geração de PDFs a partir dos dados
├── graficos_material.py   # Geração de gráficos de materiais
├── graficos_tempo.py      # Geração de gráficos temporais
├── inicio.py              # Processamento inicial de relatórios
├── transcrever_audio.py   # Transcrição de áudio usando OpenAI
├── static/
│   ├── recorder.js        # Script para gravação de áudio
│   └── style.css          # Estilos da interface web
├── templates/
│   ├── graficos.html      # Página de visualização de gráficos
│   ├── index.html         # Página principal com upload de áudio
│   └── relatorios.html    # Página de relatórios gerados
├── keys.py                # Configuração da chave da API OpenAI
├── LICENSE                # Licença Apache 2.0
└── README.md              # Documentação do projeto
```

## 🚀 Como Usar

### 1️⃣ **Configuração Inicial**
```bash
# Clonar repositório e instalar dependências
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

pip install -r requirements.txt  # Instalar Flask, OpenAI e outras dependências
```

### 2️⃣ **Configurar Chave da OpenAI**
Edite `keys.py` e insira sua chave:
```python
chave_openai = "sua-chave-aqui"
```

### 3️⃣ **Executar Aplicação Web**
```bash
python app.py
```
Acesse http://localhost:5000 no navegador para:
- Gravar/upload de áudio diretamente na interface
- Visualizar relatórios processados
- Acessar gráficos de eficiência
- Download de relatórios em PDF

### 4️⃣ **Fluxo de Processamento**
1. Áudio é salvo em `data/audios/`
2. Transcrição via OpenAI é armazenada temporariamente
3. Relatório estruturado é gerado e salvo em `data/relatorios/`
4. Gráficos são atualizados em `data/graficos/`

### 5️⃣ **Geração de Relatórios (CLI)**
Para processamento manual via terminal:
```python
from transcrever_audio import transcrever_audio
from inicio import organiza

texto = transcrever_audio("data/audios/seu_audio.ogg")
relatorio = organiza(texto)
print(relatorio)
```

### 6️⃣ **Geração de Gráficos (CLI)**
```python
from graficos_material import gerar_graficos as graf_materiais
from graficos_tempo import gerar_graficos as graf_tempo

graf_materiais()
graf_tempo()
```

## 📊 Saída Esperada
- Relatórios diários em CSV: `data/relatorios/relatorio_YYYY-MM-DD.csv`
- Gráficos atualizados: 
  - `data/graficos/eficiencia_material.png`
  - `data/graficos/eficiencia_tempo.png`
- PDF consolidado: `data/relatorios/relatorio_eficiencia.pdf`

## 🌐 Recursos da Interface Web
- Gravação de áudio direto no navegador
- Upload de arquivos de áudio (formato OGG)
- Visualização de histórico de relatórios
- Dashboard interativo com métricas de eficiência
- Download de relatórios em formato PDF

## 📜 Licença
Distribuído sob licença Apache 2.0. Veja [LICENSE](LICENSE) para detalhes.
