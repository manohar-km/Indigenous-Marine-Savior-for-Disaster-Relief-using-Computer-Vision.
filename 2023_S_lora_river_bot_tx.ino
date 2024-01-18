#include <SPI.h>
#include <LoRa.h>

//define the pins used by the transceiver module
#define ss 10
#define rst 2
#define dio0 9

String LoRaMessage = "";
String status = "0";

int sw1 = 3;
int sw2 = 4;
int sw3 = 5;
int sw4 = 6;

void setup() 
{
  //initialize Serial Monitor
  Serial.begin(9600);
  Serial.println("LoRa Sender"); 
  pinMode(sw1, INPUT_PULLUP);
  pinMode(sw2, INPUT_PULLUP);
  pinMode(sw3, INPUT_PULLUP);
  pinMode(sw4, INPUT_PULLUP);
  //setup LoRa transceiver module
  LoRa.setPins(ss, rst, dio0);
  //replace the LoRa.begin(---E-) argument with your location's frequency 
  //433E6 for Asia
  //866E6 for Europe
  //915E6 for North America

  while (!LoRa.begin(433E6)) 
  {
    Serial.println("Initializing.");
    delay(500);
  }
  LoRa.setSyncWord(0xF3);
  Serial.println("LoRa Initializing OK!");
  delay(2000);
}

void read_buttons()
{
  if(digitalRead(sw1) == 0)
  {
    Serial.println("sw1 Pressed");
    status = "1";
  }
  else if(digitalRead(sw2) == 0)
  {
    Serial.println("sw2 Pressed");
    status = "2";
  }
  else if(digitalRead(sw3) == 0)
  {
    Serial.println("sw3 Pressed");
    status = "3";
  }
  else if(digitalRead(sw4) == 0)
  {
    Serial.println("sw4 Pressed");
    status = "4";
  }
  else
  {
   Serial.println("waiting."); 
   status = "0";
  }
}

void push_update() 
{
  read_buttons();
  LoRaMessage = String(status);
  LoRa.beginPacket();
  LoRa.print(LoRaMessage);
  LoRa.endPacket();
}

void loop()
{
  push_update();
  delay(1000);
}
