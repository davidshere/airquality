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

  // Setting the address where we will send the data
	radio.openWritingPipe(address[0]);
  // radio.openReadingPipe(0, address[1]);
  // You can set it as a minimum or maximum depending on the distance
  // between the transmitter and the reciever
	radio.setPALevel(RF24_PA_MIN);

  // Set the module as a transmitter
	radio.stopListening();

}

#define SDS_RX_MSG_SIZE 10
#define SDS_TX_MSG_SIZE 19

byte received[SDS_RX_MSG_SIZE];

void loop() {

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
