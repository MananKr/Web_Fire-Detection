// // ///            tested   with   IP-192.168.1.200/fire

// #include <Wire.h>
// #include <LiquidCrystal_I2C.h>
// #include <ESP8266WiFi.h>
// #include <ESP8266WiFiMulti.h>
// #define FLAME_SENSOR_PIN D3    // Digital input from flame sensor
// ESP8266WiFiMulti wifiMulti;
// WiFiServer server(80);

// const uint32_t connectTimeoutMs = 3000;

// // I2C address 0x27 is most common, 16 columns, 2 rows
// LiquidCrystal_I2C lcd(0x27, 16, 2);  // connected via SDA (D2/GPIO4) and SCL (D1/GPIO5)

// int value = 0;
// float volt;
// const int analogPin      = A0;   // Sensor 1 (0 – 1 V)

// // LED pins
// const int LED_FIRE = D5;
// const int LED_WIFI = D6;
// const int LED_SHORT = D7;
// const int LED_OK = D8; 


// unsigned long previousMillis = 0;
// const unsigned long statusInterval = 1000;
// bool showWiFiMessage = false;

// const int threshold=200;// sets threshold value for flame sensor
// int flamesensvalue=0; // initialize flamesensor reading


// void setup() 
// {
//   // Initialize LCD
//   Serial.begin(115200);
//   lcd.init();
//   lcd.backlight();

//   WiFi.persistent(false);
//   WiFi.mode(WIFI_STA);
//   // WiFi.config(staticIP, gateway, subnet); // Set static IP
//   wifiMulti.addAP("Moto_Manan", "1111222233334");
//   wifiMulti.addAP("Airtel_mana_5881", "air59236");

//   pinMode(LED_BUILTIN, OUTPUT);
//   server.begin();
//   Serial.println("Server started.");
//   lcd.setCursor(0, 0); lcd.print("   Manan Kumar  ");
//   lcd.setCursor(0, 1); lcd.print(" Fire Detection ");
//   delay(2000); 
//   lcd.clear();

//   pinMode(LED_FIRE, OUTPUT);
//   pinMode(LED_WIFI, OUTPUT);
//   pinMode(LED_SHORT, OUTPUT);
//   pinMode(LED_OK, OUTPUT);
//   pinMode(LED_BUILTIN, OUTPUT);
//   digitalWrite(LED_BUILTIN, HIGH); // off

//   pinMode(FLAME_SENSOR_PIN, INPUT);

//   lcd.clear();
//   lcd.setCursor(0, 0);
//   lcd.print("Please Wait We're");
//   lcd.setCursor(0, 1);
//   lcd.print("finding Internet.");
// }


// void loop() 
//  { 
//   // WiFi Connection Check
//   if (wifiMulti.run(connectTimeoutMs) == WL_CONNECTED) 
//   {
//     Serial.print("WiFi connected to ");
//     Serial.println(WiFi.SSID());
//     Serial.println(WiFi.localIP());
//     lcd.clear();
//     lcd.setCursor(0, 0);
//     lcd.print(WiFi.localIP());
//     lcd.setCursor(0, 1);
//     lcd.print(WiFi.SSID());
//     digitalWrite(LED_BUILTIN, LOW);  // LED on
//     delay(500);                     // Keep it on for 5 seconds
//     digitalWrite(LED_BUILTIN, HIGH);  // LED on

//   } 
//   else 
//   {
//     Serial.println("WiFi not connected!");
//     lcd.clear();
//     lcd.setCursor(0, 0);
//     lcd.print("WiFi NOT Conncted");
//     digitalWrite(LED_WIFI, LOW);
//     delay(500);
//   }


//    value = analogRead(A0);
//    volt = value * 5.0/1023;
//    ("Volt= ");

//   if (volt <=1.5 && volt >=1.0)
//   {
//     Serial.print("SMOKE DETECTED");
//     Serial.print("  volts: ");
//     Serial.println(volt);
//     // FIRE DETECTED
//     digitalWrite(LED_FIRE, HIGH);
//     digitalWrite(LED_OK, LOW);
//     lcd.clear();
//     lcd.setCursor(0, 0);
//     lcd.print("SMOKE DETECTED");
//     delay(500); // Pause briefly to avoid LCD flicker
//   } 
//   else
//   {
//     // NO FIRE DETECTED
//     digitalWrite(LED_FIRE, LOW);
//     lcd.clear();
//     lcd.setCursor(0, 0);
//     lcd.print(" SYSTEM HEALTHY ");
//     digitalWrite(LED_OK, HIGH);
//     delay(500); 
//   }

//   int flameState = digitalRead(FLAME_SENSOR_PIN);

//   if (flameState == LOW) 
//   {  // LOW = Flame detected (depends on sensor type)
//     Serial.println("🔥 Flame Detected!");
//     digitalWrite(LED_FIRE, HIGH);

//   } else {
//     Serial.println("✅ No Flame.");
//     digitalWrite(LED_FIRE, LOW);
//     Serial.println(F(" SYSTEM HEALTHY "));

//   }

//   delay(250); 

//   // Web client handler
//   WiFiClient client = server.available();
//   if (client) 
//   {
//     Serial.println("Client connected");
//     while (!client.available()) 
//     {
//       delay(10);
//     }

//     String request = client.readStringUntil('\r');
//     Serial.println("Request: " + request);
//     client.flush();

//     if (request.indexOf("/fire") != -1) 
//     {
//       digitalWrite(LED_FIRE, HIGH);
//       lcd.clear();
//       lcd.setCursor(0, 0);
//       lcd.print("Web_Fire Detect");
//       delay(1000);
//       digitalWrite(LED_FIRE, LOW);
//     }

//     client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
//     client.print("<!DOCTYPE html><html><body><h1>ESP8266 Fire Detector</h1><p>Status OK</p></body></html>");
//     client.stop();
//     Serial.println("Client disconnected");
//   }

//   delay(100);
// }







///////////////////////////////////////////////////////////////////
/*
   ESP8266 Fire & Smoke Detector
   Tested from browser at: http://<board‑IP>/fire
*/

// #include <Wire.h>
// #include <LiquidCrystal_I2C.h>
// #include <ESP8266WiFi.h>
// #include <ESP8266WiFiMulti.h>

// /* ---------------- Pin Definitions ---------------- */
// #define FLAME_SENSOR_PIN D4      // Use D4 instead of D3 (avoid boot problems)
// #define LED_FIRE         D5
// #define LED_WIFI         D6
// #define LED_SHORT        D7
// #define LED_OK           D8
// #define ANALOG_PIN       A0      // Smoke sensor input

// /* ---------------- WiFi & LCD Setup ---------------- */
// ESP8266WiFiMulti wifiMulti;
// WiFiServer server(80);
// LiquidCrystal_I2C lcd(0x27, 16, 2);

// /* ---------------- Constants ---------------- */
// const uint32_t CONNECT_TIMEOUT_MS = 3000;
// const float SMOKE_VOLTAGE_MIN = 0.9;   // Adjust as per sensor
// const float SMOKE_VOLTAGE_MAX = 1.5;   // Adjust as per sensor

// /* ---------------- Variables ---------------- */
// bool fireDetected = false;

// /* ---------------- Setup Function ---------------- */
// void setup() {
//   Serial.begin(115200);
//   lcd.init();
//   lcd.backlight();

//   // Pin Modes
//   pinMode(FLAME_SENSOR_PIN, INPUT);
//   pinMode(LED_FIRE, OUTPUT);
//   pinMode(LED_WIFI, OUTPUT);
//   pinMode(LED_SHORT, OUTPUT);
//   pinMode(LED_OK, OUTPUT);
//   pinMode(LED_BUILTIN, OUTPUT);

//   digitalWrite(LED_FIRE, LOW);
//   digitalWrite(LED_OK, LOW);
//   digitalWrite(LED_WIFI, LOW);
//   digitalWrite(LED_BUILTIN, HIGH); // OFF (active low)

//   // LCD Welcome
//   lcd.setCursor(0, 0); lcd.print("   Manan Kumar  ");
//   lcd.setCursor(0, 1); lcd.print(" Fire Detection ");
//   delay(2000);
//   lcd.clear();
//   lcd.print("Connecting WiFi");

//   // WiFi Config
//   WiFi.persistent(false);
//   WiFi.mode(WIFI_STA);
//   wifiMulti.addAP("Moto_Manan", "1111222233334");
//   wifiMulti.addAP("Airtel_mana_5881", "air59236");

//   server.begin();
//   Serial.println("Server started.");
// }

// /* ---------------- Main Loop ---------------- */
// void loop() {
//   fireDetected = false;

//   keepWiFiAlive();

//   fireDetected |= readSmokeSensor();
//   fireDetected |= readFlameSensor();

//   if (!fireDetected) {
//     digitalWrite(LED_OK, HIGH);
//     digitalWrite(LED_FIRE, LOW);
//     lcd.clear();
//     lcd.setCursor(0, 0); lcd.print(" SYSTEM HEALTHY ");
//   } else {
//     digitalWrite(LED_OK, LOW);
//     digitalWrite(LED_FIRE, HIGH);
//   }

//   handleWebClient();

//   delay(200);
// }

// /* ---------------- Check WiFi ---------------- */
// void keepWiFiAlive() {
//   if (wifiMulti.run(CONNECT_TIMEOUT_MS) == WL_CONNECTED) {
//     digitalWrite(LED_WIFI, HIGH);
//     digitalWrite(LED_BUILTIN, LOW); // ON
//     lcd.setCursor(0, 0);
//     lcd.print(WiFi.localIP());
//     lcd.setCursor(0, 1);
//     lcd.print(WiFi.SSID() + String("        "));
//   } else {
//     digitalWrite(LED_WIFI, LOW);
//     digitalWrite(LED_BUILTIN, HIGH); // OFF
//     lcd.setCursor(0, 0); lcd.print("WiFi NOT Connected");
//     lcd.setCursor(0, 1); lcd.print("Retrying...       ");
//   }
// }

// /* ---------------- Smoke Sensor Read ---------------- */
// bool readSmokeSensor() {
//   int analogValue = analogRead(ANALOG_PIN);
//   float voltage = analogValue * (1.2 / 1023.0); // Voltage range is 1.0 to 1.5V

//   Serial.printf("Smoke: %d => %.2f V\n", analogValue, voltage);

//   if (voltage >= SMOKE_VOLTAGE_MIN) {
//     Serial.println(" SMOKE DETECTED");
//     lcd.clear();
//     lcd.setCursor(0, 0); lcd.print("SMOKE DETECTED");
//     lcd.setCursor(0, 1); lcd.print("Take Action..!");
//     return true;
//   }
//   return false;
// }

// /* ---------------- Flame Sensor Read ---------------- */
// bool readFlameSensor() {
//   int flameState = digitalRead(FLAME_SENSOR_PIN);

//   if (flameState == LOW) { // Flame detected (LOW)
//     Serial.println("🔥 FLAME DETECTED");
//     lcd.clear();
//     lcd.setCursor(0, 0); lcd.print("FLAME DETECTED");
//     lcd.setCursor(0, 1); lcd.print("Take Action..!");
//     return true;
//   }
//   return false;
// }

// /* ---------------- Handle Web Request ---------------- */
// void handleWebClient() {
//   WiFiClient client = server.available();
//   if (!client) return;

//   Serial.println("Client connected");
//   while (!client.available()) delay(1);

//   String request = client.readStringUntil('\r');
//   Serial.println("Request: " + request);
//   client.flush();

//   if (request.indexOf("/fire") != -1) {
//     fireDetected = true;
//     digitalWrite(LED_FIRE, HIGH);
//     lcd.clear();
//     lcd.setCursor(0, 0); lcd.print("Web Fire Trigger");
//     lcd.setCursor(0, 1); lcd.print("LED ON Alert!");
//     delay(1000);
//   }

//   client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
//   client.print("<!DOCTYPE html><html><body>");
//   client.print("<h1>ESP8266 Fire Detector</h1><p>Status OK</p>");
//   client.print("</body></html>");

//   client.stop();
//   Serial.println("Client disconnected");
// }

////////////////////////////////////////////////////////////////////////////



#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#define FLAME_SENSOR_PIN D3
#define LED_FIRE         D5
#define LED_RELAY        D6
#define LED_OK           D8
#define ANALOG_PIN       A0      // Smoke sensor input
// int FLAME = HIGH;

ESP8266WiFiMulti wifiMulti;
WiFiServer server(80);

const uint32_t connectTimeoutMs = 5000;
const float SMOKE_VOLTAGE_MIN = 0.9;   // Adjust as per sensor
LiquidCrystal_I2C lcd(0x27, 16, 2);  


String scrollText = "";
int scrollPos = 0;
unsigned long previousMillis = 0;
const unsigned long scrollInterval = 400;
bool wifiConnectedOnce = false;

void setup() 
{
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  // WiFi.config(staticIP, gateway, subnet); 
  wifiMulti.addAP("Moto_Manan", "1111222233334");
  wifiMulti.addAP("Airtel_mana_5881", "air59236");

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED_FIRE, OUTPUT);
  pinMode(FLAME_SENSOR_PIN, INPUT);
  pinMode(LED_RELAY , OUTPUT);   
  pinMode(LED_OK, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 


  digitalWrite(LED_FIRE, LOW); 
  digitalWrite(LED_RELAY, LOW); 
  digitalWrite(LED_OK, LOW); 

  server.begin();
  Serial.println("Server started.");

  lcd.setCursor(0, 0); lcd.print("   Manan Kumar  ");
  lcd.setCursor(0, 1); lcd.print(" Fire Detection ");
  delay(2000); 
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Please Wait We're");
  lcd.setCursor(0, 1);
  lcd.print("finding Internet.");
}

void loop() 
{
  // Try connecting to WiFi
  if (wifiMulti.run(connectTimeoutMs) == WL_CONNECTED) 
  {
    if (!wifiConnectedOnce) {
      Serial.print("WiFi connected to ");
      Serial.println(WiFi.SSID());
      scrollText = "WiFi Connected..! " + String(WiFi.SSID()) + " " + WiFi.localIP().toString() + "   ";
      lcd.clear();
      lcd.setCursor(0, 1);
      lcd.print(" System Healthy");
      wifiConnectedOnce = true;
    }

    // Scroll top row
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= scrollInterval) {
      previousMillis = currentMillis;

      lcd.setCursor(0, 0);
      lcd.print(scrollText.substring(scrollPos, scrollPos + 16));
      scrollPos++;
      if (scrollPos > scrollText.length() - 16) scrollPos = 0;
    }

    digitalWrite(LED_BUILTIN, LOW);  // LED on (connected)
    delay(700);
    digitalWrite(LED_BUILTIN, HIGH);  // LED OFF (connected)
  } 
  else 
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No WiFi..! found");
    lcd.setCursor(0, 1);
    lcd.print("Check SSID/Pass ");
    digitalWrite(LED_BUILTIN, HIGH);;
    wifiConnectedOnce = false;
    delay(1000);
    return;
  }

  // Flame sensor check

  Serial.print("WiFi connected to ");
  Serial.println(WiFi.SSID());
  Serial.print(" ");
  Serial.println(WiFi.localIP());

  int FLAME = digitalRead(FLAME_SENSOR_PIN);  //  Rain sensor output pin connected
   if (FLAME == HIGH)
   {
    digitalWrite(LED_FIRE , HIGH); // Relay
    digitalWrite(LED_RELAY  , HIGH);  
    digitalWrite(LED_OK  , LOW);
    Serial.println("Flame Detected.!");   
    scrollText = "";  // Stop scrolling
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Flame Detected.!");
    lcd.setCursor(0, 1);
    lcd.print("Take Action Now!");
    delay(500);
   }
   else
   {
    digitalWrite(LED_FIRE , LOW); // Relay
    digitalWrite(LED_OK  , HIGH);
    digitalWrite(LED_RELAY  , LOW);  
    Serial.println(" Not FD detected");
   }

       /* ---------------- Smoke Sensor Read ---------------- */
  int analogValue = analogRead(ANALOG_PIN);
  float voltage = analogValue * (1.2 / 1023.0); // Voltage range is 1.0 to 1.5V

  Serial.printf("Smoke: %d => %.2f V\n", analogValue, voltage);
  delay(500);
  if (voltage >= SMOKE_VOLTAGE_MIN) 
  {
    Serial.println(" SMOKE DETECTED");
    digitalWrite(LED_FIRE , HIGH); // Relay
    digitalWrite(LED_RELAY  , HIGH);  
    digitalWrite(LED_OK  , LOW);
  
    scrollText = " ";  // Stop scrolling
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(" SMOKE DETECTED  ");
    lcd.setCursor(0, 1);
    lcd.print("Take Action Now!");
    delay(500);
  }
  else
  {
    digitalWrite(LED_FIRE , LOW); // Relay
    digitalWrite(LED_OK  , HIGH);
    digitalWrite(LED_RELAY  , LOW);  
    Serial.println("  No SMOKE ");
  }



  // Handle web request
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");

    while (!client.available()) {
      delay(10);
    }

    String request = client.readStringUntil('\r');
    Serial.println("Request: " + request);
    client.flush();

    if (request.indexOf("/fire") != -1) {
      digitalWrite(LED_FIRE, HIGH);
      scrollText = "";  // Stop scrolling
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Web_Fire Detect");
      lcd.setCursor(0, 1);
      lcd.print("Take Action Now!");
      delay(700);

    }

    client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
    client.print("<!DOCTYPE html><html><body><h1>ESP8266 Fire Detector</h1><p>Status OK</p></body></html>");
    client.stop();
    Serial.println("Client disconnected");
  }

  delay(50);
}


















// #include <Wire.h>
// #include <LiquidCrystal_I2C.h>
// #include <ESP8266WiFi.h>
// #include <ESP8266WiFiMulti.h>

// LiquidCrystal_I2C lcd(0x27, 16, 2);

// ESP8266WiFiMulti wifiMulti;
// WiFiServer       server(80);

// const uint32_t CONNECT_TIMEOUT_MS = 5000;

// const int LED_FIRE  = D5;
// const int LED_WIFI  = D6;
// const int LED_SHORT = D7;
// const int LED_OK    = D8;
// int  analogPin      = A0;
// int  flamesensvalue = 0;
// const int THRESHOLD = 200;

// /* ── non‑blocking blink state ───────────── */
// const uint32_t ALERT_BLINK_MS = 700;
// uint32_t       lastBlinkMs    = 0;
// bool           alertActive    = false;

// /* ── scrolling text ─────────────────────── */
// String scrollText   = "";
// int    scrollPos    = 0;
// uint32_t prevScroll = 0;
// const uint32_t SCROLL_INTERVAL = 400;
// bool wifiConnectedOnce = false;

// /* ───────────────────────────────────────── */
// void setup() {
//   Serial.begin(115200);
//   lcd.init(); lcd.backlight();

//   WiFi.persistent(false);
//   WiFi.mode(WIFI_STA);
//   wifiMulti.addAP("Moto_Manan", "1111222233334");
//   wifiMulti.addAP("Airtel_mana_5881","air59236");

//   pinMode(LED_BUILTIN, OUTPUT);
//   pinMode(LED_FIRE,    OUTPUT);
//   pinMode(LED_WIFI,    OUTPUT);
//   pinMode(LED_SHORT,   OUTPUT);
//   pinMode(LED_OK,      OUTPUT);
//   digitalWrite(LED_BUILTIN, HIGH);

//   server.begin();

//   lcd.setCursor(0,0); lcd.print("   Manan Kumar  ");
//   lcd.setCursor(0,1); lcd.print(" Fire Detection ");
//   delay(2000); lcd.clear();
//   lcd.setCursor(0,0); lcd.print("Please Wait We're");
//   lcd.setCursor(0,1); lcd.print("finding Internet.");
// }

// void loop() {
//   /* ── Wi‑Fi connect / scroll banner ───────────── */
//   if (wifiMulti.run(CONNECT_TIMEOUT_MS) == WL_CONNECTED) {
//     if (!wifiConnectedOnce) {
//       scrollText = "WiFi Connected..! " + WiFi.SSID() + " " +
//                    WiFi.localIP().toString() + "   ";
//       Serial.print("WiFi Connected..!");
//       Serial.print("  ");
//       Serial.print(WiFi.SSID());
//       Serial.println("  ");
//       Serial.println(WiFi.localIP());
//       lcd.clear();
//       lcd.setCursor(0,1); lcd.print(" System Healthy");
//       wifiConnectedOnce = true;
//       digitalWrite(LED_WIFI, LOW);
//       digitalWrite(LED_OK, LOW);
//       delay(200);
//       digitalWrite(LED_OK, HIGH);
//       digitalWrite(LED_WIFI, HIGH);
//       delay(200);
      
//     }

//     if (millis() - prevScroll >= SCROLL_INTERVAL) {
//       prevScroll = millis();
//       lcd.setCursor(0,0);
//       lcd.print(scrollText.substring(scrollPos, scrollPos + 16));
//       scrollPos = (scrollPos + 1) % (scrollText.length() - 15);
//     }
//   } else {
//     lcd.clear();
//     lcd.setCursor(0,0); lcd.print("No WiFi..! found");
//     lcd.setCursor(0,1); lcd.print("Check SSID/Pass ");
//     digitalWrite(LED_BUILTIN, LOW);
//     wifiConnectedOnce = false;
//     delay(1000);
//     return;
//   }

//   /* ── Flame sensor (local) ────────────────────── */
//   flamesensvalue = analogRead(analogPin);
//   if (flamesensvalue <= THRESHOLD) 
//   {
//     alertActive = true;                              // start alert
//     lcd.clear();
//     lcd.setCursor(0,0); lcd.print("FD-FIRE DETECTED");
//     lcd.setCursor(0,1); lcd.print("Take Action Now!");
//     Serial.println("FD-FIRE DETECTED");
//     digitalWrite(LED_FIRE, LOW);
//     digitalWrite(LED_OK,   HIGH);
//   } 

//   // /* ── Blink FIRE LED non‑blocking ─────────────── */
//   // if (alertActive && millis() - lastBlinkMs >= ALERT_BLINK_MS) {
//   //   lastBlinkMs = millis();
//   //   digitalWrite(LED_FIRE, !digitalRead(LED_FIRE));
//   // }

//   /* ── HTTP handler (/fire) ────────────────────── */
//   WiFiClient client = server.available();
//   if (client) {
//     while (!client.available()) delay(1);
//     String req = client.readStringUntil('\r'); client.flush();

//     if (req.indexOf("/fire") != -1) {
//       alertActive = true;                            // trigger same alert
//       lcd.clear();
//       lcd.setCursor(0,0); lcd.print("Web_FIRE Detect");
//       lcd.setCursor(0,1); lcd.print("Take Action Now!");
//       digitalWrite(LED_FIRE, LOW);
//       Serial.println("Web_FIRE Detect");
//       delay(2000);
//     }

//     client.print(
//       "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK\r\n");
//     client.stop();
//   }
// }



