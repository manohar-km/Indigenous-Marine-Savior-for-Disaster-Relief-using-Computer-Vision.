#include <SPI.h>
#include <LoRa.h>

//define the pins used by the transceiver module
#define ss 10
#define rst 2
#define dio0 9

String LoRaMessage = "";
int rx_status = 0;

int in1 = 3;
int in2 = 4;
int in3 = 5;
int in4 = 6;

void setup() 
{
  //initialize Serial Monitor
  Serial.begin(9600);
  Serial.println("LoRa Sender"); 
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
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

void getLoRaData()
{
  Serial.print("Lora packet received: ");
  // Read packet
  if(LoRa.available()) 
  {
    String LoRaData = LoRa.readString();
    Serial.println(LoRaData);
    rx_status = LoRaData.toInt();
  }
  if(rx_status == 1)
  {
    rx_status = 1;
    fw();
  }
  else if(rx_status == 2)
  {
    rx_status = 2;
    bw();
  }
  else if(rx_status == 3)
  {
    rx_status = 3;
    lft();
  }
  else if(rx_status == 4)
  {
    rx_status = 4;
    rgt();
  }
  else
  {
    rx_status = 0;
    stp();
  }
}

void loop()
{
  int packetSize = LoRa.parsePacket();
  if (packetSize) 
  {
    getLoRaData();
  }
}

void bw()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  Serial.println("backward");
}

void fw()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  Serial.println("forward");
}

void lft()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  Serial.println("left");
}

void rgt()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  Serial.println("right");
}

void stp()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  Serial.println("stop");
}
