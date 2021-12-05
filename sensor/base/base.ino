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
  
  // Setting the address at which we will recieve the data
	radio.openReadingPipe(0, address[0]);
	radio.openWritingPipe(address[1]);
  // You can set this as minimum or maximum depending on the distance between the transmitter and receiver
	radio.setPALevel(RF24_PA_MIN);

  // This sets the module as receiver
	radio.startListening();
}


byte *get_message() {
	static byte msg[NODE_RX_MSG_SIZE];
  radio.read(&msg, NODE_RX_MSG_SIZE);
	return msg;
}

void *request_reading() {
//  srand (time());
  int val = rand() % 100;
	Serial.print("Requesting ");
	Serial.println(val);
	bool sent=radio.write(&val, sizeof(int));
	Serial.println(sent, DEC);
}
// Send a message to the node
// Wait for a response from the node
// Print the response
void loop()	{
	delay(5);
	radio.stopListening();
	request_reading();
	delay(5);

	radio.startListening();
	while(!radio.available()) delay(10);
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
