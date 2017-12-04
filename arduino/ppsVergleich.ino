#include <LiquidCrystal.h>
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

const int kanal1 = 31;
const int kanal2 = 33;

int state = LOW;
int laststate = LOW;
unsigned long time1 = 0, time2 = 0;

void setup() {
  // Display 2 Zeilen a 16 Zeichen
  lcd.begin(16, 2);
  // Schreibposition setzen
  lcd.setCursor(0, 0);
  // Schreibt Text
  lcd.print("Zeitdifferenz:");
  lcd.setCursor(0, 1);

  pinMode(kanal1, INPUT);
  pinMode(kanal2, INPUT);

  Serial.begin(9600);
}

void loop() {
  state = digitalRead(kanal1);
  time1 = micros();
  // erste Flanke
  if (laststate == LOW && state == HIGH) {
    laststate = LOW;
    state = LOW;
    // solange, bis 2. Flanke
    do {
      laststate = state;
      state = digitalRead(kanal2);
      time2 = micros();
    } while (!(laststate == LOW && state == HIGH));

    // Zeitdiff berechnen und ausgeben
    unsigned long diff = time2 - time1;
    String wert = String(diff);
    int pos = 16 - wert.length();
    if (pos <= 0) {
      pos = 0;
      wert = "zu lang";
    }
    lcd.setCursor(pos, 1);
    Serial.println(diff);
    lcd.print(diff);
    laststate = LOW;
    state = LOW;
    delay(50000);
    lcd.clear();
    lcd.setCursor(0, 0);
    // Schreibt Text
    lcd.print("Zeitdifferenz:");
    lcd.setCursor(0, 1);
  }
  laststate = state;
}
