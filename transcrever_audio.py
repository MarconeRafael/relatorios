import openai
import subprocess
import os
from keys import chave_openai

def transcrever_audio(audio_webm):
    """Converte um arquivo de áudio WEBM para WAV e transcreve o áudio usando a API da OpenAI, sempre em português."""
    openai.api_key = chave_openai  # Substitua pela sua chave real
    
    if not os.path.exists(audio_webm):
        print(f"Arquivo {audio_webm} não encontrado!")
        return None
    
    audio_wav = audio_webm.replace(".webm", ".wav")
    
    try:
        # Converter WEBM para WAV usando FFmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", audio_webm, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_wav
        ], check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao converter áudio: {e}")
        return None
    
    if not os.path.exists(audio_wav):
        print(f"Erro na conversão! Arquivo {audio_wav} não foi gerado.")
        return None
    
    try:
        # Transcrever o áudio WAV para texto utilizando a API da OpenAI (Whisper) sempre em português
        with open(audio_wav, "rb") as audio_file:
            transcription = openai.Audio.transcribe("whisper-1", audio_file, language="pt")
        
        # Exibir resposta completa para depuração
        print("Resposta completa da API:", transcription)
        
        transcricao_texto = transcription.get("text", "")
        if not transcricao_texto:
            print("Erro: A transcrição não retornou texto.")
            return None
        
        print(f"Transcrição: {transcricao_texto}")
        return transcricao_texto
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return None
