// ----------------------- LIBRERÍAS  -----------------------
#include <ESP8266WiFi.h>
#include "FirebaseESP8266.h"
// ----------------------- PIN  -----------------------
const int trig   = D1;
const int echo   = D2;
const int buzzer = D5;
const int relay  = D6;
const int reed   = D7;
// Definición de variables
long distance;
long tiempo;
String doorState;
int camaraState = 0;
int lockState;
int alarmState;
// ----------------------- WiFi  -----------------------
#define ssid "IoT"
#define password "Lock-It-15"
// ----------------------- Firebase  -----------------------
#define API_KEY "AIzaSyA5Ok0ZAenmcds4H8BsoOtii0chhavTDNY"

const char *FIREBASE_HOST="https://lockit-a8bd0-default-rtdb.firebaseio.com/";
const char *FIREBASE_AUTH="6T0VXv0KLpVdvFwdvFYLMVs4r3FP4cWbq29vHFzp"; 

// Firebase Data object in the global scope
FirebaseData fireDB;

void setup() {
  Serial.begin(115200);
  pinMode(reed, INPUT_PULLUP);
  pinMode(relay, OUTPUT);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(buzzer,OUTPUT);
  digitalWrite(relay, HIGH);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED){
    Serial.print("Conectando...\n");
    delay(250);
  }
  Serial.print("\nConexión exitosa");
  Serial.println();
  
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);

}

void loop() {
  delay(1000);
  Firebase.getInt(fireDB,"Puerta/lock");
  lockState = fireDB.intData();

  Firebase.getInt(fireDB,"Puerta/alarm");
  alarmState = fireDB.intData();
  // ----------------------- Detección de visitantes  -----------------------
  digitalWrite(trig, LOW);
  delayMicroseconds(4);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  
  tiempo = pulseIn(echo, HIGH);
  tiempo = tiempo/2;
  distance = tiempo* 0.000001 * 34300; //Fórmula para calcular la distancia 
  
  //Mostrar distancia en el monitor serial
  Serial.print (distance);
  Serial.println (" cm");

  if(distance <= 65){ 
    camaraState = 1;
  }else{
    camaraState = 0;

  }
  // ----------------------- Estado de puerta  -----------------------
  
  if(alarmState == 0){
    digitalWrite(buzzer,LOW);
  }
  if(digitalRead(reed) == HIGH){
    //Serial.println("Door Open!");
    if(alarmState== 1){
      digitalWrite(buzzer,HIGH);
    }
     doorState = "Abierta";
  }else{
    digitalWrite(buzzer,LOW);
    //Serial.println("Door Closed!");
    doorState = "Cerrada";

  }
  // ----------------------- Estado de candado -----------------------
  //if(lockState==1){
    //digitalWrite(relay, LOW);
  //}
  //if(lockState == 0){
    //digitalWrite(relay, LOW);
  //}
  digitalWrite(relay, lockState);
  Firebase.setString(fireDB,"Puerta/status",doorState);
  Firebase.setInt(fireDB,"Puerta/isCamera", camaraState);
  delay(1000);
  
}
