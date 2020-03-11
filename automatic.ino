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
const int RACK_MOVEMENT = 2700;

// Claw
const int C_W1 = 5;     // Claw - Wire 1
const int C_W2 = 6;     // Claw - Wire 2
const int C_INT = 900;

Servo servo;
DRV8825 stepper(MOTOR_STEPS, DIR, STEP);

float SRVO_POS;
float STPR_POS;

float SAVED_SRVO_POS;
float SAVED_STPR_POS;
int GLOBAL_MOVES = 0;

int incoming[8];  // FIX ME
int DELAY = 100;
int SERVO_DELAY = 12;

// Stepper

void homeStepper() {
  pinMode(SWITCH_PIN, OUTPUT);

  while (digitalRead(SWITCH_PIN) == LOW) {    // While switch is not triggered
    stepper.rotate(-3);
    delay(120);   // Special for backing...
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
    if (abs(SRVO_POS - angle) <= 30) {
      delay(DELAY);    // Difference b/w Current pos and Next pos <= 30
      moveServo(0, true);
    }
  }
  
  if (angle < SRVO_POS) {
    servoReverse(angle);
  }
  else if (angle > SRVO_POS) {
    servoForward(angle);
  }
  SRVO_POS = angle;
  delay(DELAY);
}

void servoForward(float angle) {
  for (int i = SRVO_POS; i <= angle; ++i) {
    servo.write(i);
    delay(SERVO_DELAY);
  }
}

void servoReverse(float angle) {
  for (int i = SRVO_POS; i >= angle; --i) {
    servo.write(i);
    delay(SERVO_DELAY);
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
  delay(DELAY);
  moveServo(servo, false);
}

void zeroing() {
  moveStepper(0);
  delay(DELAY);
  moveServo(90, true);
}

void pickup() {
//  open(C_INT);
//  delay(DELAY);
  down(RACK_MOVEMENT);
  delay(DELAY);
  close(C_INT);
  delay(DELAY);
  up(RACK_MOVEMENT);
  delay(DELAY);
}

void drop() {
  down(RACK_MOVEMENT);
  delay(DELAY);
  open(C_INT);
  delay(DELAY);
  up(RACK_MOVEMENT);
  delay(DELAY);
//  close(C_INT);
//  delay(DELAY);
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

  homeStepper();
}


void loop() {
    
    while (Serial.available() >= 9){

      for (int i = 0; i < 9; i++){
        incoming[i] = Serial.read();
        
        if (incoming[i] > 200) {
          incoming[i] = 200 - incoming[i];
        }
      }
      if (GLOBAL_MOVES == 2) {
        homeStepper();
        GLOBAL_MOVES = 0;
      }
    
      if (incoming[0] == 0) {   // Piece Movement
          moveDegrees(incoming[1], incoming[2]);
          delay(DELAY);
          pickup();
          delay(DELAY);
          moveDegrees(incoming[3], incoming[4]);
          delay(DELAY);
          drop();
          Serial.write(0);
          GLOBAL_MOVES++;
      }
      else if (incoming[0] == 1) {  // Piece Capture
          moveDegrees(incoming[3], incoming[4]);
          delay(DELAY);
          pickup();
          zeroing();
          delay(DELAY);
          open(C_INT);
//          close(C_INT);
  
          moveDegrees(incoming[1], incoming[2]);
          delay(DELAY);
          pickup();
          delay(DELAY);
          
          moveDegrees(incoming[3], incoming[4]);
          delay(DELAY);
          drop();
          Serial.write(1);
          GLOBAL_MOVES++;
      }
      else if (incoming[0] == 2) {  // Castling
        Serial.write(6);
        GLOBAL_MOVES++;
      }
      else {
        Serial.write(3);
      }
      zeroing();
      delay(DELAY);
    } 
}
