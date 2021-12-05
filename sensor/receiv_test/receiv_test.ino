#include <printf.h>
#include <stdlib.h>
#include <time.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN

// 00001=base, 00002=node
const byte address[][6] = {"00001", "00002"};

#define NODE_RX_MSG_SIZE 10
#define NODE_TX_MSG_SIZE 19

//byte rx_message[NODE_RX_MSG_SIZE];

void setup() {

	Serial.begin(9600);
	radio.begin();
  radio.setAutoAck(false);  
  // Setting the address at which we will recieve the data
	radio.openReadingPipe(0, address[0]);
  // You can set this as minimum or maximum depending on the distance between the transmitter and receiver
	radio.setPALevel(RF24_PA_MIN);

  // This sets the module as receiver
	radio.startListening();
	Serial.println(radio.getDataRate());
	printf_begin();
	radio.printPrettyDetails();
}


byte *get_message() {
	static byte msg[NODE_RX_MSG_SIZE];
  radio.read(&msg, NODE_RX_MSG_SIZE);
	return msg;
}

void loop()	{
	while(!radio.available()) {
		Serial.print("Nothing available");
		delay(500);
    Serial.println("...");
		delay(500);
	}

//	if (radio.available()) {
  byte *rx_message;
	rx_message = get_message();
//		radio.read(&rx_message, NODE_RX_MSG_SIZE);
	for (int i=0; i<NODE_RX_MSG_SIZE; i++) {
		Serial.print(rx_message[i], HEX);
	}
	Serial.println();
	delay(1000);
}
