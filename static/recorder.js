// Exemplo básico usando a API MediaRecorder para gravar áudio no navegador.
// OBS: A implementação pode variar conforme a necessidade e compatibilidade dos navegadores.

let mediaRecorder;
let recordedChunks = [];

// Ao clicar no botão, inicia ou para a gravação
document.getElementById('btnGravar').addEventListener('click', async function() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        // Para a gravação
        mediaRecorder.stop();
    } else {
        // Inicia a gravação
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Seu navegador não suporta gravação de áudio.");
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recordedChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = function(e) {
                if (e.data.size > 0) {
                    recordedChunks.push(e.data);
                }
            };
            
            mediaRecorder.onstop = function() {
                const blob = new Blob(recordedChunks, { type: 'audio/webm' });
                enviarAudio(blob);
            };
            
            mediaRecorder.start();
        } catch (err) {
            console.error("Erro ao acessar o microfone: ", err);
        }
    }
});

// Função para enviar o áudio para o servidor
function enviarAudio(blob) {
    const formData = new FormData();
    formData.append('audio_data', blob, 'gravacao.webm');
    
    fetch('/processar_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.transcricao) {
            document.getElementById('textoTranscricao').innerText = data.transcricao;
        } else if(data.error) {
            document.getElementById('textoTranscricao').innerText = "Erro: " + data.error;
        }
    })
    .catch(error => {
        console.error("Erro na requisição:", error);
        document.getElementById('textoTranscricao').innerText = "Erro ao enviar áudio.";
    });
}
