#include <printf.h>
#include <SPI.h>
#include <RF24.h>
#include <SoftwareSerial.h>


RF24 radio(9, 10); // CE, CSN         

// Setting up the SDS
int rxPin = 2;
int txPin = 3;
SoftwareSerial sds(rxPin, txPin);

// 00001=base, 00002=node
const byte address[][6] = {"00001", "00002"};


void setup() {
  Serial.begin(9600);

	// Set up the SDS011
  sds.begin(9600);

	// Starting the wireless communication
	radio.begin();
	radio.setDataRate(RF24_250KBPS);
  //radio.setAutoAck(false);
  // Setting the address where we will send the data
	radio.openWritingPipe(address[0]);
  radio.openReadingPipe(0, address[1]);
  // You can set it as a minimum or maximum depending on the distance
  // between the transmitter and the reciever
	radio.setPALevel(RF24_PA_MIN);

  radio.startListening();

	Serial.println(radio.getDataRate());
	printf_begin();
	radio.printPrettyDetails();
}

#define SDS_RX_MSG_SIZE 10
#define SDS_TX_MSG_SIZE 19

byte received[SDS_RX_MSG_SIZE];
byte command[SDS_TX_MSG_SIZE];

void printWaiting() {
	Serial.print("No command, waiting");
  delay(250);
  Serial.print(".");
	delay(250);
	Serial.print(".");
	delay(250);
	Serial.print(".");
	delay(250);
	Serial.println();
}

void loop() {
	radio.startListening();
	if (!radio.available()) {
		printWaiting();
		return;
	} else {
    Serial.println("Found something!");
		radio.read(&command, SDS_TX_MSG_SIZE);
    for ( int i=0; i<SDS_TX_MSG_SIZE; i++) {
      Serial.print(command[i]);
//     command[i] = radio.read()
		}
    Serial.println();
	}
	Serial.println("Down here");
  radio.stopListening();
  byte b = sds.read();
	if (b != 0xAA) return;

	received[0] = b;

	for (int i=1; i<SDS_RX_MSG_SIZE; i++) {
		received[i]= sds.read();
  }

	for (int j=0; j<SDS_RX_MSG_SIZE; j++) {
		Serial.print(received[j], HEX);
  }
  Serial.println();
 
	bool written = radio.write(&received, SDS_RX_MSG_SIZE);
	delay(1000);
}
