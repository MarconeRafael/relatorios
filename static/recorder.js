let mediaRecorderInicio;
let mediaRecorderFim;
let recordedChunksInicio = [];
let recordedChunksFim = [];

// Ao clicar no botão "Gravar Início"
document.getElementById('btnGravarInicio').addEventListener('click', async function() {
    const botaoGravarInicio = document.getElementById('btnGravarInicio');
    
    if (mediaRecorderInicio && mediaRecorderInicio.state === "recording") {
        // Para a gravação de início
        mediaRecorderInicio.stop();
        botaoGravarInicio.textContent = "Gravar Início";  // Altera o texto do botão para "Gravar Início"
    } else {
        // Inicia a gravação de início
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Seu navegador não suporta gravação de áudio.");
            return;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recordedChunksInicio = [];
            mediaRecorderInicio = new MediaRecorder(stream);
            
            mediaRecorderInicio.ondataavailable = function(e) {
                if (e.data.size > 0) {
                    recordedChunksInicio.push(e.data);
                }
            };
            
            mediaRecorderInicio.onstop = function() {
                const blob = new Blob(recordedChunksInicio, { type: 'audio/webm' });
                enviarAudio(blob, 'inicio');  // Envia o áudio de início para o servidor
            };
            
            mediaRecorderInicio.start();
            botaoGravarInicio.textContent = "Fim da Gravação";  // Altera o texto do botão para "Fim da Gravação"
        } catch (err) {
            console.error("Erro ao acessar o microfone: ", err);
        }
    }
});

// Ao clicar no botão "Gravar Fim"
document.getElementById('btnGravarFim').addEventListener('click', async function() {
    const botaoGravarFim = document.getElementById('btnGravarFim');
    
    if (mediaRecorderFim && mediaRecorderFim.state === "recording") {
        // Para a gravação de fim
        mediaRecorderFim.stop();
        botaoGravarFim.textContent = "Gravar Fim";  // Altera o texto do botão para "Gravar Fim"
    } else {
        // Inicia a gravação de fim
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Seu navegador não suporta gravação de áudio.");
            return;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recordedChunksFim = [];
            mediaRecorderFim = new MediaRecorder(stream);
            
            mediaRecorderFim.ondataavailable = function(e) {
                if (e.data.size > 0) {
                    recordedChunksFim.push(e.data);
                }
            };
            
            mediaRecorderFim.onstop = function() {
                const blob = new Blob(recordedChunksFim, { type: 'audio/webm' });
                enviarAudio(blob, 'fim');  // Envia o áudio de fim para o servidor
            };
            
            mediaRecorderFim.start();
            botaoGravarFim.textContent = "Fim da Gravação";  // Altera o texto do botão para "Fim da Gravação"
        } catch (err) {
            console.error("Erro ao acessar o microfone: ", err);
        }
    }
});

// Função para enviar o áudio para o servidor
function enviarAudio(blob, tipo) {
    const formData = new FormData();
    const nomeArquivo = tipo === 'inicio' ? "inicio.webm" : "fim.webm";
    
    formData.append('audio_data', blob, nomeArquivo);
    formData.append('tipo', tipo); // Envia o tipo da gravação
    
    fetch('/processar_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcricao) {
            if (tipo === 'inicio') {
                document.getElementById('textoTranscricaoInicio').innerText = data.transcricao;
            } else {
                document.getElementById('textoTranscricaoFim').innerText = data.transcricao;
            }
        } else if (data.error) {
            const textoErro = "Erro: " + data.error;
            if (tipo === 'inicio') {
                document.getElementById('textoTranscricaoInicio').innerText = textoErro;
            } else {
                document.getElementById('textoTranscricaoFim').innerText = textoErro;
            }
        }
    })
    .catch(error => {
        console.error("Erro na requisição:", error);
        if (tipo === 'inicio') {
            document.getElementById('textoTranscricaoInicio').innerText = "Erro ao enviar áudio.";
        } else {
            document.getElementById('textoTranscricaoFim').innerText = "Erro ao enviar áudio.";
        }
    });
}
