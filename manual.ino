#include <Servo.h>
#include <Arduino.h>
#include "DRV8825.h"

#define MOTOR_STEPS 200
#define DIR 16
#define STEP 17
#define SWITCH_PIN 2

// Rack
const int R_W1 = 8;   // Rack - Wire 1
const int R_W2 = 7 ;  // Rack - Wire 2
int R_HEIGHT = 2900;

// Claw
const int C_W1 = 5;     // Claw - Wire 1
const int C_W2 = 6;     // Claw - Wire 2
const int C_INT = 1100;

Servo servo;
DRV8825 stepper(MOTOR_STEPS, DIR, STEP);

float SRVO_POS;
float STPR_POS;

float SAVED_SRVO_POS;
float SAVED_STPR_POS;

int incoming[8];  // FIX ME


// Stepper

void homeStepper() {
  pinMode(SWITCH_PIN, OUTPUT);

  while (digitalRead(SWITCH_PIN) == LOW) {    // While switch is not triggered
    stepper.rotate(-3);
    delay(120);
  }
  stepper.rotate(50);
  STPR_POS = 0;
}

void moveStepper(float angle) {
  if (angle > 120) {
    return;
  }
  stepper.rotate(angle - STPR_POS);
  STPR_POS = angle;
}


// Servo

void moveServo(float angle, bool reset) {
  if (angle > 180) {
    return;
  }
  if (not reset) {
    if (abs(SRVO_POS - angle) <= 10) {    // Difference b/w Current pos and Next pos <= 30
      moveServo(0, true);
      delay(500);
    }
  }
  if (angle < SRVO_POS) {
    servoReverse(angle);
  }
  else if (angle > SRVO_POS) {
    servoForward(angle);
  }
  SRVO_POS = angle;
}

void servoForward(float angle) {
  for (int i = SRVO_POS; i <= angle; ++i) {
    servo.write(i);
    delay(15);
  }
}

void servoReverse(float angle) {
  for (int i = SRVO_POS; i >= angle; --i) {
    servo.write(i);
    delay(15);
  }
}


// Rack

void up(int interval) {
  digitalWrite(R_W1, HIGH) ;
  digitalWrite(R_W2, LOW) ;
  delay(interval);
  digitalWrite(R_W1, LOW) ;
  digitalWrite(R_W2, LOW) ;
}

void down(int interval) {
  digitalWrite(R_W2, HIGH) ;
  digitalWrite(R_W1, LOW) ;
  delay(interval);
  digitalWrite(R_W2, LOW) ;
  digitalWrite(R_W1, LOW) ;
}


// Claw

void open(int interval) {
  digitalWrite(C_W1, HIGH) ;
  delay(interval);
  digitalWrite(C_W1, LOW) ;
}

void close(int interval) {
  digitalWrite(C_W2, HIGH) ;
  delay(interval);
  digitalWrite(C_W2, LOW) ;
}


// Miscellaneous

void moveDegrees(int stepper, int servo) {
  moveStepper(stepper);
  delay(500);
  moveServo(servo, false);
}

void zeroing() {
  moveStepper(0);
  delay(500);
  moveServo(90, true);
}


void setup() {
  Serial.begin(9600);

  // Move Servo to its default position
  servo.attach(3);
  servo.write(90);
  SRVO_POS = 90;

  stepper.begin(4, 1);

  // Rack
  pinMode(R_W1, OUTPUT) ;
  pinMode(R_W2, OUTPUT) ;

  // Claw
  pinMode(C_W1, OUTPUT) ;
  pinMode(C_W2, OUTPUT) ;
}


void loop() {

    while (Serial.available() >= 2) {
      char cmd = Serial.read();
  
      if (cmd == 'h') {                 // Home Stepper
        Serial.println("Homing stepper!");
        moveServo(90, false);
        delay(500);
        moveStepper(0);
      }
      else if (cmd == 'f') {            // Full Reset
        moveServo(90, false);
        delay(500);
        homeStepper();
      }
      else if (cmd == 's') {             // Servo
        float angle = Serial.parseFloat();
        Serial.print("Servo angle: ");
        Serial.println(angle);
        moveServo(angle, false);
      }
      else if (cmd == 't') {             // Stepper
        float angle = Serial.parseFloat();
        Serial.print("Stepper angle: ");
        Serial.println(angle);
        moveStepper(angle);
      }
      else if (cmd == 'c') {             // Claw
        char followUpCmd = Serial.read();
        int interval = Serial.parseInt();

        if (interval > 1500) {
          return;
        }
  
        if (followUpCmd == 'o') {
          open(interval);
        }
        else if (followUpCmd == 'c') {
          close(interval);
        }
      }
      else if (cmd == 'r') {             // Rack
        char followUpCmd = Serial.read();
        int interval = Serial.parseInt();
        char confirmation = Serial.read();
  
        if (followUpCmd == 'u' && confirmation == 'u') {
          up(interval);
        }
        else if (followUpCmd == 'd' && confirmation == 'd') {
          down(interval);
        }
      }
      else if (cmd == 'p') {            // Position
          Serial.print("Stepper: ");
          Serial.println(STPR_POS);
          SAVED_STPR_POS = STPR_POS;
  
          Serial.print("Servo: ");
          Serial.println(SRVO_POS);
          SAVED_SRVO_POS = SRVO_POS;
  
          char followUpCmd = Serial.read();
  
          if (followUpCmd == 'g') {
            moveServo(90, false);
            delay(500);
            homeStepper();
            delay(1000);
            moveStepper(SAVED_STPR_POS);
            delay(1000);
            moveServo(SAVED_SRVO_POS, false);
          }
      } 
      else if (cmd == 'm') {        // Move -> m90p90 or m90d90
        int stpr = Serial.parseInt();
        char followUpCmd = Serial.read();
        int srvo = Serial.parseInt();
  
        moveStepper(stpr);
        delay(500);
  
        moveServo(srvo, false);
        delay(1000);
  
        if (followUpCmd == 'p') {
  
          down(R_HEIGHT);
          delay(500);
  
          close(C_INT);
          delay(500);
  
          up(R_HEIGHT);
          delay(500);
        }
        else if (followUpCmd == 'd') {
          down(R_HEIGHT);
          delay(1000);
  
          open(C_INT);
          delay(500);
  
          up(R_HEIGHT);
          delay(1000);
        }
      }

      else if (cmd == 'x') {
        int angle = Serial.parseInt();
        servo.write(angle);
      }
    }
}
