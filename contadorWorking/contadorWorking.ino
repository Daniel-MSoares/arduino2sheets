// ----- PINOS -----
int pinoPenduloAnalogico = A0;  // Sensor infravermelho do pêndulo
int pinoChuva = A1;             // Sensor de rain drops

// ----- VARIÁVEIS PENDULO -----
int leituraPenduloAtual;
int leituraPenduloAnterior = 0;
int limiteVariacaoPendulo = 100;        // diferença mínima para contar uma passada
int contadorPassadas = 0;                // contador atual
unsigned long tempoUltimaPassada = 0;   // tempo da última passada
unsigned long intervaloMinimoPassada = 500; // 500ms entre passadas



// ----- VARIÁVEIS CHUVA -----
int leituraChuvaAtual;
int leituraChuvaAnterior = 940;        // sensor inicial seco
int sensibilidadeGota = 20;             // mínima variação para detectar nova gota
bool chuvaAtiva = false;                
unsigned long tempoUltimaGota = 0;      
unsigned long tempoLimiteSemGota = 30000; // 30 segundos sem gotas -> chuva acabou


void setup() {
  Serial.begin(9600);
}

void loop() {
  // ----------------------
  // 1. SENSOR DE CHUVA
  // ----------------------
  leituraChuvaAtual = analogRead(pinoChuva);
  

  // Se houver variação suficiente indicando uma nova gota
  if ((leituraChuvaAnterior - leituraChuvaAtual) > sensibilidadeGota) {
    tempoUltimaGota = millis();  // atualiza momento da última gota
    if (!chuvaAtiva) {
      chuvaAtiva = true;
      
      Serial.println(">>> Evento: Chuva começou!");
    }
  }

  // Se não caiu nenhuma gota por tempoLimiteSemGota, considera chuva parada
  if (chuvaAtiva && (millis() - tempoUltimaGota > tempoLimiteSemGota)) {
    chuvaAtiva = false;
    Serial.println(">>> Evento: Chuva parou!");
    Serial.print(">>> Quantidade de passadas -> ");
    Serial.println(contadorPassadas);
    

     

    contadorPassadas = 0; // reseta para próxima chuva
  }

  // Atualiza leitura anterior do sensor de chuva
  leituraChuvaAnterior = leituraChuvaAtual;

  // ----------------------
  // 2. SENSOR PÊNDULO
  // ----------------------
  if (chuvaAtiva) { // só conta passadas durante chuva
    leituraPenduloAtual = analogRead(pinoPenduloAnalogico);
    int diferencaPendulo = abs(leituraPenduloAtual - leituraPenduloAnterior);

    // Só conta se passou intervalo mínimo
    if (diferencaPendulo > limiteVariacaoPendulo 
        && (millis() - tempoUltimaPassada > intervaloMinimoPassada)) {
      contadorPassadas++;
      tempoUltimaPassada = millis();
    }

    leituraPenduloAnterior = leituraPenduloAtual;
  }

  delay(20); // loop rápido para não perder gotas ou passadas rápidas
}


