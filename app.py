import serial
from datetime import datetime, timedelta
import requests
import json

# -------- CONFIGURAÇÃO --------
porta_serial = 'COM5'      # Substitua pela porta do seu Arduino
baud_rate = 9600           # Deve ser igual ao Serial.begin do Arduino
timeout = 1   
url_webapp = "https://script.google.com/macros/s/AKfycbzgRuSc0w-G9BGv3HOUKER6Vdos9QbvhTvMvsaXoxaofTJx-PHt9MDcTet33aBjYi-z/exec"    

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
                resumoJson={
                        "inicio": inicio_chuva.strftime('%d/%m/%Y %H:%M:%S'),
                        "fim": fim_chuva.strftime('%d/%m/%Y %H:%M:%S'),
                        "volume_mm": calcular_volume_mm(contador_passadas)
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








        ########################################################################
        ####################





# import serial
# import time
# import requests
# from datetime import datetime
# import math

# # ----------------------------
# # CONFIGURAÇÕES
# # ----------------------------
# porta_serial = "COM5"  # substitua pela sua porta
# baud_rate = 9600
# url_webapp = "https://script.google.com/macros/s/AKfycbzZKn1CWdYTgsJyOc_SwjfAeYRuGuekeNy-v8OPaTGtWgXArQ2unQortF5vanevH9W2/exec"  # URL do Apps Script

# # Cada passada equivale a 5 mL de água
# volume_por_passada_ml = 5

# # Área de coleta em metros (10 cm de raio = 0,1 m)
# raio_coleta_m = 0.1
# area_coleta_m2 = math.pi * raio_coleta_m ** 2

# # ----------------------------
# # INICIALIZAÇÃO
# # ----------------------------
# ser = serial.Serial(porta_serial, baud_rate, timeout=1)
# time.sleep(2)  # espera o Arduino reiniciar

# chuva_ativa = False
# contador_passadas = 0
# inicio_chuva = None

# def calcular_altura_mm(passadas):
#     # Volume total em litros
#     volume_l = passadas * volume_por_passada_ml / 1000
#     # Altura em metros: volume / área
#     altura_m = volume_l / area_coleta_m2
#     # Converte para mm
#     altura_mm = altura_m * 1000
#     return round(altura_mm, 2)

# try:
#     print("Aguardando eventos do Arduino...\n")
#     while True:
#         linha = ser.readline().decode("utf-8").strip()
#         if not linha:
#             continue

#         # Começo da chuva
#         if "Evento: Chuva começou!" in linha:
#             chuva_ativa = True
#             contador_passadas = 0
#             inicio_chuva = datetime.now()
#             print(f"[{inicio_chuva}] Chuva começou!")

#         # Contagem de passadas
#         elif "Passadas atuais:" in linha and chuva_ativa:
#             partes = linha.split(":")
#             contador_passadas = int(partes[-1].strip())
#             print(f"Passadas até agora: {contador_passadas}")

#         # Fim da chuva
#         elif ">>> Parou de chover." in linha and chuva_ativa:
#             fim_chuva = datetime.now()
#             altura_mm = calcular_altura_mm(contador_passadas)
#             print(f"[{fim_chuva}] Chuva parou! Altura: {altura_mm} mm")

#             # Envia para o Apps Script
#             dados = {
#                 "inicio": inicio_chuva.strftime("%d/%m/%Y %H:%M:%S"),
#                 "fim": fim_chuva.strftime("%d/%m/%Y %H:%M:%S"),
#                 "altura_mm": altura_mm
#             }

#             try:
#                 resposta = requests.post(url_webapp, json=dados)
#                 print("Dados enviados para a planilha:", resposta.json())
#             except Exception as e:
#                 print("Erro ao enviar dados:", e)

#             # Reseta estado
#             chuva_ativa = False
#             contador_passadas = 0
#             inicio_chuva = None

# except KeyboardInterrupt:
#     print("Programa finalizado pelo usuário.")
# finally:
#     ser.close()
