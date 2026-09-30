/*
  This script demonstrates TCP connection between client and server with this
  script acting as both.  

  As of 2026 July 23, the MUSTANG network allows this type of traffic.

  Seth McNeill
  2026 July 22
*/


#include <WiFi.h>
#include "secrets.h"

// Wi-Fi Credentials
const char* ssid = SSID;
const char* password = WIFI_PWD;

// Remote Server Details (for TCP Client)
const char* remoteServerIP = SERVER_IP;
const uint16_t remoteServerPort = REMOTE_PORT;
const uint16_t localServerPort = LOCAL_PORT;

// TCP Server setup on port 1234
WiFiServer tcpServer(localServerPort);
WiFiClient clientList[4]; // Handle up to 4 concurrent client connections

bool curLED = LOW;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, curLED);
  delay(3000);
  Serial.println("Starting " + String(MOD_NAME) + " TCP Server/Client");

  Serial.println();
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  // Wait for connection to your local network
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected!");
  Serial.print("ESP32-C6 IP Address: ");
  Serial.println(WiFi.localIP());

  // Broadcasts a direct Wi-Fi network from the ESP32-C6
  // WiFi.softAP("ESP32-C6-TestNet", "12345678");

  // IPAddress myIP = WiFi.softAPIP();
  // Serial.print("Connect your computer to Wi-Fi: ESP32-C6-TestNet\n");
  // Serial.print("ESP32-C6 Server IP Address: ");
  // Serial.println(myIP); // This will default to 192.168.4.1

  // Start the TCP Server
  tcpServer.begin();
  Serial.print("TCP Server started on port ");
  Serial.println(localServerPort);
}

void loop() {
  // blink the LED to show life
  curLED = !curLED;
  digitalWrite(LED_BUILTIN, curLED);

  // --- 1. TCP SERVER: Check for new incoming client connections ---
  if (tcpServer.hasClient()) {
    bool foundSlot = false;
    for (int i = 0; i < 4; i++) {
      if (!clientList[i] || !clientList[i].connected()) {
        // clientList[i] = tcpServer.available();
        clientList[i] = tcpServer.accept();
        Serial.print("New client connected to server at slot ");
        Serial.println(i);
        foundSlot = true;
        break;
      }
    }
    // If no slots are available, immediately reject the incoming connection
    if (!foundSlot) {
      // WiFiClient reject = tcpServer.available();
      WiFiClient reject = tcpServer.accept();
      reject.stop();
      Serial.println("Server connection rejected - too many clients");
    }
  }

  // --- 2. TCP SERVER: Receive and Send data from connected clients ---
  for (int i = 0; i < 4; i++) {
    if (clientList[i] && clientList[i].connected()) {
      if (clientList[i].available()) {
        String request = clientList[i].readStringUntil('\n');
        request.trim();
        Serial.print("Server received from client [");
        Serial.print(i);
        Serial.print("]: ");
        Serial.println(request);

        // Echo response back to the client
        clientList[i].println("Nesso acknowledged: " + request);
      }
    }
  }

  // --- 3. TCP CLIENT: Connect to a remote server and send/receive data ---
  static unsigned long lastConnectAttempt = 0;
  unsigned long now = millis();

  // Try to connect to the remote server every 5 seconds
  // if (false) {
  if (now - lastConnectAttempt > SEND_DELAY) {
    // This creates a new TCP connection every time rather than reusing the old one
    lastConnectAttempt = now;

    WiFiClient client;
    Serial.print("\n[Client] Connecting to ");
    Serial.print(remoteServerIP);
    Serial.print(":");
    Serial.println(remoteServerPort);

    if (client.connect(remoteServerIP, remoteServerPort)) {
      Serial.println("[Client] Connected to server!");

      // Send data to the remote server
      client.println("Hello from " +  String(MOD_NAME) + "!");

      // Wait for a response from the remote server
      unsigned long timeout = millis();
      while (client.connected() && !client.available()) {
        if (millis() - timeout > 3000) { // 3-second timeout
          Serial.println("[Client] Read timeout!");
          break;
        }
      }

      // Read response
      if (client.available()) {
        String response = client.readStringUntil('\n');
        Serial.print("[Client] Received from Server: ");
        Serial.println(response);
      }

      client.stop();  // closes connection every time
      Serial.println("[Client] Disconnected.");
    } else {
      Serial.println("[Client] Connection failed.");
    }
  }
}
