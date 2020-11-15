#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <WiFi.h> //#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>    // Adafruit  sensor library
#include <Adafruit_ADXL345_U.h> // ADXL345 library
#include <String.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

const char *ssid = "MSR-Rout";
const char *password = "msujithr2020";

//-------------------------MQTT Setup Start----------------------------------
#include <PubSubClient.h>
const char *mqttServer = "192.168.1.3";
const int mqttPort = 1883;
const char *mqttUser = "mqtt2020";
const char *mqttPassword = "mqtt2020";
const char *mqttClientName = "esp32";

WiFiClient esp32_msr;
PubSubClient client(esp32_msr);

#define mqttTopic "esp32/topic"
//---------------------------MQTT Setup End-------------------------------------

#define DHTPIN 33
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(); // ADXL345 Object

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

float temperature, humidity, accX, accY, accZ;

String mqttData;

String formattedDate;
String dayStamp;
String timeStamp;

//---------------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial.println();

  connectWifi(); //connect to wifi

  client.setServer(mqttServer, mqttPort);

  if (!accel.begin()) // if ASXL345 sensor not found
  {
    Serial.println("ADXL345 not detected");
    while (1);
  }

  dht.begin();
  delay(5000);

  // Initialize a NTPClient to get time
  timeClient.begin();
  // Set offset time in seconds to adjust for your timezone, for example:
  // GMT +1 = 3600
  // GMT +8 = 28800
  // GMT -1 = -3600
  // GMT 0 = 0
  timeClient.setTimeOffset(19800); // GMT +5:30
}

void loop()
{
  while (!timeClient.update())
  {
    timeClient.forceUpdate();
  }

  if (!client.connected())
  {
    reconnect();
  }
  getValues();

  client.publish(mqttTopic, String(mqttData).c_str(), true);
  delay(5000);
}

void getValues()
{

  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  sensors_event_t event;
  accel.getEvent(&event);

  accX = event.acceleration.x;
  accY = event.acceleration.y;
  accZ = event.acceleration.z;

  Serial.print("Ext Temp = ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Ext Humidity = ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.println();

  Serial.print("X: ");
  Serial.print(accX);
  Serial.print("  ");
  Serial.print("Y: ");
  Serial.print(accY);
  Serial.print("  ");
  Serial.print("Z: ");
  Serial.print(accZ);
  Serial.print("  ");
  Serial.println("m/s^2 ");

  Serial.println();

  formattedDate = String(timeClient.getFormattedDate());
  Serial.println(formattedDate);
  //format in which date and time is returned 2018-04-30T16:00:13Z
  int splitT = formattedDate.indexOf("T");
  dayStamp = formattedDate.substring(0, splitT);
  timeStamp = formattedDate.substring(splitT + 1, formattedDate.length() - 1);

  String ts = dayStamp+ " " +timeStamp;

  mqttData = "{\"timestamp\":\"" +ts+ + "\",\"temperature\":" +String(temperature)+ ",\"humidity\":" +String(humidity)+ ",\"x\":" +String(accX)+ ",\"y\":" +String(accX)+ ",\"z\":" +String(accX)+ "}";
}

void reconnect()
{
  // Loop until we're reconnected

  int counter = 0;
  while (!client.connected())
  {
    if (counter == 5)
    {
      ESP.restart();
    }
    counter += 1;
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect

    if (client.connect(mqttClientName, mqttUser, mqttPassword))
    {
      Serial.println("connected");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

//------------------------wifi connect function----------------------------
void connectWifi()
{
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(2000);

  WiFi.begin(ssid, password);

  //wait untill wifi is connected

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  // wifi is connected

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
//-------------------------------------------------------------------------
