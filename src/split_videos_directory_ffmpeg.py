import subprocess
import os
import time

def split_video(video_path, segment_duration, logOutput):
    base_dir = os.path.dirname(video_path)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_dir = os.path.join(base_dir, base_name)
    os.makedirs(video_dir, exist_ok=True)
    
    output_path = os.path.join(video_dir, f"{base_name}_segment_%03d.mp4")

    command = [
        'ffmpeg',
        '-i', video_path,
        '-c', 'copy',
        '-map', '0',
        '-segment_time', str(segment_duration),
        '-f', 'segment',
        '-reset_timestamps', '1',
        output_path
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    for line in process.stdout:
        logOutput.emit(line)

    process.stdout.close()

    segments_file_path = os.path.join(video_dir, 'video_segments.txt')
    with open(segments_file_path, 'w') as file_list:
        for segment in sorted(os.listdir(video_dir)):
            if segment.endswith('.mp4') and segment.startswith(base_name):
                file_list.write(f"file '{segment}'\n")

def process_directory(directory_path, segment_duration, update_progress, logOutput):
    """
    Processa todos os arquivos de vídeo em uma pasta, dividindo cada um em segmentos e atualiza o progresso.

    Args:
    - directory_path: Caminho para a pasta que contém os vídeos.
    - segment_duration: Duração de cada segmento em segundos.
    - update_progress: Método para emitir atualizações de progresso.
    """
    # Filtra e conta todos os arquivos de vídeo no diretório
    video_files = [file for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file)) and file.endswith(('.mp4', '.mkv', '.avi'))]
    total_videos = len(video_files)
    
    if total_videos == 0:
        print("Nenhum vídeo encontrado para processar.")
        return

    for index, file_name in enumerate(video_files, start=1):
        file_path = os.path.join(directory_path, file_name)
        print(f"Processando {file_name}...")
        split_video(file_path, segment_duration, logOutput)
        
        # Calcula o percentual de progresso e emite uma atualização
        progress_percent = int((index / total_videos) * 100)
        update_progress.emit(progress_percent)
        time.sleep(0.1)  # Remova isso se o processamento real do vídeo for suficientemente longo
