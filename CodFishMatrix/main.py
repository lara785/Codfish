import board
import analogio
from adafruit_matrixportal.matrix import Matrix
import time

# Inicialize a entrada do microfone (substitua pelo pino analógico correto)
mic = analogio.AnalogIn(board.A0)  # Supondo que A0 seja o pino de entrada analógica


# Inicialize a matriz de LED para 128x64
matrix = Matrix(width=128, height=64)
display = matrix.display

# Parâmetros para suavização
SAMPLES = 10  # Número de amostras em média
sound_history = [0] * 128  # Inicialize um buffer para armazenar valores de som para a forma de onda

def get_smoothed_sound_level():
    # Execute uma média móvel simples sobre as leituras de SAMPLES para suavizar o nível de som
    total = 0
    for _ in range(SAMPLES):
        total += mic.value  # Lê a voltagem do microfone
        time.sleep(0.01)  # Pequeno atraso entre amostras
    # Dimensione o valor médio para ajustar a altura da exibição (0 a 64)
    return int((total / SAMPLES) / 65535 * 64)

def update_waveform(new_level):
   # Desloca os dados anteriores no buffer do histórico para a esquerda
    for i in range(127):
        sound_history[i] = sound_history[i + 1]
    # Adiciona o novo nível de som ao final do buffer
    sound_history[127] = new_level

while True:
    # Obtenha um nível de som suavizado
    sound_level = get_smoothed_sound_level()

    # Atualize a forma de onda com novo nível de som
    update_waveform(sound_level)

    # Limpe a tela
    display.fill(0)

    # Desenhe a forma de onda como uma linha através da matriz
    for x in range(128):
        # Trace a história do som como posições verticais
        y = 63 - sound_history[x]  # Inverter para corresponder às coordenadas de exibição
        display.pixel(x, y, (0, 255, 255))  # Cor ciano para a forma de onda

    # Mostrar a exibição atualizada
    display.show()
