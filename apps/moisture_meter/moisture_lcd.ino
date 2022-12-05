/*
  Soil Moisture Meter
  soil_meter.ino
  Measures percentage of moisture in soil
  Uses Capacitive sensor
  Requires calibration values
 
  Modified from DroneBot Workshop 2022
*/
 
// Include required libraries
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
 
// Set OLED size in pixels
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
 
// Set OLED parameters
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
 
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
 
// Sensor constants - replace with values from calibration sketch
 
// Constant for dry sensor
const int DryValue = 2590;
 
// Constant for wet sensor
const int WetValue = 1430;
 
// Variables for soil moisture
int soilMoistureValue;
int soilMoisturePercent;
 
// Analog input port
#define SENSOR_IN 0
 
void setup() {
 
  // Setup Serial Monitor
  Serial.begin(9600);
 
  // Initialize I2C display using 3.3-volts from VCC directly
  display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  display.clearDisplay();
 
  // Set ADC to use 12 bits
  analogReadResolution(12);
 
}
void loop() {
 
  // Get soil mositure value
  soilMoistureValue = analogRead(SENSOR_IN);
 
  // Print to serial monitor
  Serial.print(soilMoistureValue);
  Serial.print(" - ");
 
  // Determine soil moisture percentage value
  soilMoisturePercent = map(soilMoistureValue, DryValue, WetValue, 0, 100);
 
  // Keep values between 0 and 100
  soilMoisturePercent = constrain(soilMoisturePercent, 0, 100);
 
  // Print to serial monitor
  Serial.println(soilMoisturePercent);
 
  // Position and print text to OLED
  display.setCursor(20, 0);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.println("Moisture");
 
  display.setCursor(30, 12);
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.print(soilMoisturePercent);
  display.println("%");
  display.display();
 
  delay(250);
  display.clearDisplay();
 
  delay(100);
}
