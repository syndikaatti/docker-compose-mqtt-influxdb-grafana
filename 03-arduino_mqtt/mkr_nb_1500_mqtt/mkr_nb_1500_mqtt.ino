/**

    This is the MKR NB 1500 MQTT sketch, configured
    to work with the IoThon 2019 VMs.

    Required libraries:
      - MKRNB
      - PubSubClient
**/

/**
  Team:
  Tuomo Kivekäs
  Antti Paananen
  Joonas Maanonen
  Paavo Pärssinen
**/

/**************************************************
 * At minimum do change the following.
 *
 * If you don't change them, you will be sending your
 * data to the example server, at the example topic
 */
#define MQTT_TOPIC_TEMPERATURE "iothon/myteam/temperature"
#define MQTT_TOPIC_RSSI        "iothon/myteam/rssi"
#define MQTT_TOPIC_STATE       "iothon/myteam/status"
#define MY_SERVER  "10.200.1.1"
/****************************************************/

// #include <Adafruit_Sensor.h>
// #include <Adafruit_BME280.h>

#include <MKRNB.h>
#include <PubSubClient.h>

// If you are not using the default PIN, consider using "arduino_secrets.h"
// See https://www.hackster.io/Arduino_Genuino/store-your-sensitive-data-safely-when-sharing-a-sketch-e7d0f0
const char PIN_NUMBER[] = "1234";
const char APN[] = ""; // "iot";

#define MQTT_PUBLISH_DELAY        60000 // 60 seconds
#define MQTT_CLIENT_ID           "mkrnb1500iothon"

const char *MQTT_SERVER   = MY_SERVER;
const char *MQTT_USER     = "mqttuser";     // NULL for no authentication
const char *MQTT_PASSWORD = "mqttpassword"; // NULL for no authentication

NB           nbAccess(true); // NB access: use a 'true' parameter to enable debugging
GPRS         gprsAccess;     // GPRS access
NBClient     tcpSocket;
PubSubClient mqttClient(tcpSocket);

void setup() {
  Serial.begin(115200);
  while (! Serial)
    ;

  Serial.println("MKR NB 1500 MQTT client starting.");

  Serial.println("Connect: NB-IoT / LTE Cat M1 network (may take several minutes)...");
  while (nbAccess.begin(PIN_NUMBER, APN) != NB_READY) {
    Serial.println("Connect: NB-IoT: failed.  Retrying in 10 seconds.");
    delay(10000);
  }
  Serial.println("Connect: NB-IoT: connected.");

  Serial.println("Acquire: PDP context...");
  while (gprsAccess.attachGPRS() != GPRS_READY) {
    Serial.println("Acquire: PDP context: failed.  Retrying in 10 seconds.");
    delay(10000);
  }
  Serial.println("Acquire: PDP context: acquired.");
#if 1 /* Using newer version of the library */
  Serial.print("Acquire: PDP Context: ");
  Serial.println(nbAccess.readPDPparameters());
#endif

  mqttClient.setServer(MQTT_SERVER, 1883);
}

long lastMsgTime = 0;

void loop() {
  Serial.println("Looping: start...");
  if (!mqttClient.loop()) {
    mqttConnectIfNeeded();
  }

  long now = millis();
  if (now - lastMsgTime > MQTT_PUBLISH_DELAY) {
    lastMsgTime = now;

    float temperature = readTemperature();
    mqttPublish(MQTT_TOPIC_TEMPERATURE, temperature);
    float rssi = readRSSI();
    mqttPublish(MQTT_TOPIC_RSSI, rssi);
  }
  Serial.println("Looping: delay...");
  delay(1000);
  Serial.println("Looping: done.");
}

float readTemperature() {
  String temp;

  // Read the NB-IoT modem's internal temperature; does not work on all boards
  MODEM.send("AT+UTEMP?");
  MODEM.waitForResponse(100, &temp);

  if (temp.startsWith("+UTEMP: ")) {
    temp.remove(0, 8);
    return temp.toFloat();
  }
  return NAN;
}

float readRSSI() {
  String rssi;

  MODEM.send("AT+CESQ");
  MODEM.waitForResponse(100, &rssi);
  Serial.print("RSSI=");
  Serial.println(rssi);

  if (rssi.startsWith("+CESQ: ")) {
    rssi.remove(0, 7);
    return rssi.toFloat();
  }
  return NAN;
}

void mqttConnectIfNeeded() {
  while (!mqttClient.connected()) {
    Serial.println("Connect: starting...");

    // Attempt to connect
    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD, MQTT_TOPIC_STATE, 1, true, "disconnected", false)) {
      Serial.println("Connect: connected.");

      // Once connected, publish an announcement...
      mqttClient.publish(MQTT_TOPIC_STATE, "connected", true);
    } else {
      Serial.print("Connect: failed, state=");
      Serial.print(mqttClient.state());
      Serial.println(". Trying again in 5 seconds.");
      delay(5000);
    }
  }
}

void mqttPublish(String topic, float payload) {
  Serial.print("Publish: ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(payload);

  mqttClient.publish(topic.c_str(), String(payload).c_str(), true);
}
