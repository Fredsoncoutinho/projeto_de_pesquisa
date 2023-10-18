#include <Wire.h>
#include <Adafruit_MLX90614.h>  // Biblioteca do Pirômetro
#include <max6675.h>            // Biblioteca do Módulo Max6675

int ktcSO = 5;
int ktcCS = 6;
int ktcCLK = 7;

MAX6675 ktc(ktcCLK, ktcCS, ktcSO);           // Cria um objeto Termopar do tipo MAX6675 com os pinos CLK, CS e SO já definidos previamente
Adafruit_MLX90614 mlx = Adafruit_MLX90614(); // Cria um objeto mlx
//double temp_amb;
double temp_obj;

void setup() {
  Serial.begin(9600);
  mlx.begin();           // Initializing the MLX90614 sensor
}
void loop() {
  String dados_termopar = String(ktc.readCelsius());
  String dados_pirometro = String(mlx.readObjectTempC());
  // temp_amb = mlx.readAmbientTempC();
  // temp_obj = mlx.readObjectTempC();
  if (dados_termopar.equals("nan") || dados_termopar.equals("NAN") ) {
    dados_termopar = "0.0";
    Serial.println(dados_termopar);
    Serial.println(temp_obj);
  }
  else {
    Serial.println(dados_termopar);
    Serial.println(temp_obj);
  }
  //Serial.print("Temperatura: "); //IMPRIME O TEXTO NO MONITOR SERIAL
  Serial.println(ktc.readCelsius()); //IMPRIME NO MONITOR SERIAL A TEMPERATURA MEDIDA
  delay(200);  //INTERVALO DE 200 MILISSEGUNDOS}
}