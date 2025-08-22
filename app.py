import serial
from datetime import datetime, timedelta
import requests
import json

# -------- CONFIGURAÇÃO --------
porta_serial = 'COM5'      # Substitua pela porta do seu Arduino
baud_rate = 9600           # Deve ser igual ao Serial.begin do Arduino
timeout = 1   
url_webapp = "https://script.google.com/macros/s/AKfycbz_xI2lVPwKEbzKurk4Y5k7lk3UUYljqUauaI-MjONmlchQ1j0PAQe1rq9r4AY6-a7l/exec"  

# -------- CONEXÃO SERIAL --------
try:
    arduino = serial.Serial(porta_serial, baud_rate, timeout=timeout)
    print(f"Conectado ao Arduino na porta {porta_serial}")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit()

chuva_ativa = False
inicio_chuva = None
fim_chuva = None
duracao=None
contador_passadas = 0

volume_por_passada_ml = 5            # 5 mL por passada
raio_cm = 5                          # raio do pluviômetro
area_cm2 = 3.1416 * raio_cm**2       # área de coleta

# Conversão para altura de chuva em mm
volume_mm_por_passada = (volume_por_passada_ml / area_cm2) * 10  # mm
print(f"Cada passada equivale a {volume_mm_por_passada:.3f} mm de chuva")

def calcular_volume_mm(passadas):
    """Calcula o volume total de chuva em mm baseado no número de passadas."""
    mm=  round(passadas * volume_mm_por_passada, 2)
    return str(mm)+' mm³'

def postar_dados(dados):
    try:
        resposta = requests.post(url_webapp,data=json.dumps(dados),headers={"Content-Type": "application/json"})
        resposta.raise_for_status()  # levanta erro se não for 2xx
        print("atualizou planilha")
    except requests.RequestException as e:
        print("Erro ao enviar dados:", e)

 
print("Aguardando eventos do Arduino...\n")



while True:
    try:
        linha = arduino.readline().decode('utf-8').strip()
        if not linha:
            continue

        # Detecta início da chuva
        if "Evento: Chuva começou!" in linha:
            chuva_ativa = True
            inicio_chuva = datetime.now()
            print(f"[{inicio_chuva.strftime('%H:%M:%S')}] Chuva começou!")

        # Detecta fim da chuva e quantidade de passadas
        elif "Evento: Chuva parou!" in linha:
            fim_chuva = datetime.now() 
            chuva_ativa = False
            print(f"[{fim_chuva.strftime('%H:%M:%S')}] Chuva parou!")

        elif "Quantidade de passadas ->" in linha:
            contador_passadas = int(linha.split("->")[-1].strip())
            print(f"Total de passadas nesta chuva: {contador_passadas}")
            print(contador_passadas)

            if (contador_passadas!= 0) and (fim_chuva - inicio_chuva) >= timedelta(seconds=30) :
                duracao = fim_chuva - inicio_chuva
                total_segundos = int(duracao.total_seconds())
                duracao_str = f"{total_segundos//3600:02d}:{(total_segundos%3600)//60:02d}:{total_segundos%60:02d}"
                resumoJson={
                        "inicio": inicio_chuva.strftime('%d/%m/%Y %H:%M:%S'),
                        "fim": fim_chuva.strftime('%d/%m/%Y %H:%M:%S'),
                        "volume_mm": calcular_volume_mm(contador_passadas),
                        "duracao": duracao_str
                }
                postar_dados(resumoJson)
            
            
            print("-" * 40)

        # Mensagens de debug ou status durante a chuva
        else:
            if chuva_ativa:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {linha}")

    except KeyboardInterrupt:
        print("Encerrando leitura serial...")
        arduino.close()
        break
    except Exception as e:
        print(f"Erro durante a leitura: {e}")



