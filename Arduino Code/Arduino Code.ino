
#define left_motors_1 12
#define left_motors_2 8
#define right_motors_1 4
#define right_motors_2 2
#define r_speed 3
#define l_speed 5
#define buzzer 7

#define dir_pin1 A0
#define dir_pin2 A1
#define dir_pin3 A2


int dir1;
int dir2;
int dir3;

#define trig_pin 10
#define echo_pin 11
long duration;
int distance,dist;




void forward(int l , int r, int wait = 150){
Serial.println("F");
analogWrite(r_speed,map(r,0,5,0,255));
analogWrite(l_speed,map(l,0,5,0,255));  
digitalWrite(left_motors_1,HIGH);
digitalWrite(left_motors_2,LOW);
digitalWrite(right_motors_1,HIGH);
digitalWrite(right_motors_2,LOW);
delay(wait);
stop_motors();

  
}

void backward(int l , int r){
Serial.println("B");
analogWrite(r_speed,map(r,0,5,0,255));
analogWrite(l_speed,map(l,0,5,0,255));  
digitalWrite(left_motors_1,LOW);
digitalWrite(left_motors_2,HIGH);
digitalWrite(right_motors_1,LOW);
digitalWrite(right_motors_2,HIGH);
delay(50);
stop_motors();
}


void left(int l , int r, int wait = 150){
//Serial.println("L");
analogWrite(r_speed,map(r,0,5,0,255));
analogWrite(l_speed,map(l,0,5,0,255));  
digitalWrite(left_motors_1,HIGH);
digitalWrite(left_motors_2,HIGH);
digitalWrite(right_motors_1,HIGH);
digitalWrite(right_motors_2,LOW);
/*
 digitalWrite(left_motors_1,LOW);
digitalWrite(left_motors_2,HIGH);
digitalWrite(right_motors_1,HIGH);
digitalWrite(right_motors_2,LOW);
 */
 Serial.print("wait : ");
 Serial.println(wait);
delay(wait);
stop_motors(); 
}
void right(int l , int r, int wait = 150){
Serial.println("R");
analogWrite(r_speed,map(r,0,5,0,255));
analogWrite(l_speed,map(l,0,5,0,255)); 
digitalWrite(left_motors_1,HIGH);
digitalWrite(left_motors_2,LOW);
digitalWrite(right_motors_1,HIGH);
digitalWrite(right_motors_2,HIGH); 
/*
 digitalWrite(left_motors_1,HIGH);
digitalWrite(left_motors_2,LOW);
digitalWrite(right_motors_1,LOW);
digitalWrite(right_motors_2,HIGH);
 */
delay(wait);
stop_motors();
}

void stop_motors(){
Serial.println("S");
digitalWrite(left_motors_1,LOW);
digitalWrite(left_motors_2,LOW);
digitalWrite(right_motors_1,LOW);
digitalWrite(right_motors_2,LOW);
}

int radar(){
  digitalWrite(trig_pin, LOW);
delayMicroseconds(2);
digitalWrite(trig_pin, HIGH);
delayMicroseconds(10);
digitalWrite(trig_pin, LOW);
duration = pulseIn(echo_pin, HIGH);
distance= duration*0.034/2;
return distance;
}

void setup() {
// put your setup code here, to run once:
Serial.begin(115200);

pinMode(left_motors_1,OUTPUT);
pinMode(left_motors_2,OUTPUT);
pinMode(right_motors_1,OUTPUT);
pinMode(right_motors_2,OUTPUT);
pinMode(r_speed,OUTPUT);
pinMode(l_speed,OUTPUT);
pinMode(dir_pin1,INPUT);
pinMode(dir_pin2,INPUT); 
pinMode(dir_pin3,INPUT); 
pinMode(trig_pin, OUTPUT); 
pinMode(echo_pin, INPUT); 
pinMode(buzzer, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
dir1=analogRead(dir_pin1) > 150 ? HIGH : LOW;
dir2=analogRead(dir_pin2)> 150 ? HIGH : LOW;
dir3=analogRead(dir_pin3)> 150 ? HIGH : LOW;
dist =radar();
Serial.println(dist);
/*
if (dist >=15){
  //forward(2,2);
  Serial.println("F");
}
else {
  digitalWrite(buzzer,HIGH);
  delay(250);
  left(3,3, 500);
  forward(3,3,500);
  right(3,3,500);
  digitalWrite(buzzer,LOW);
  
}
*/
if(dir1 == 0 & dir2 ==1 & dir3 ==1 ){
//  Serial.println("F");
dist =radar();
Serial.println(dist);
if (dist >=15){
  forward(2,2);
}
else {
  digitalWrite(buzzer,HIGH);
  delay(250);
  left(3,3, 350);
  //forward(1,1,20);
  right(3,3,350);
  digitalWrite(buzzer,LOW);
}
  
} else if(dir1 == 1 & dir2 ==0 & dir3 ==1){
//   Serial.println("R");
   backward(3,3);
   
}else if(dir1 == 1 & dir2 ==0 & dir3 ==0){
//  Serial.println("L");
  left(3,3);
}else if(dir1 == 0 & dir2 ==1 & dir3 ==0){
//  Serial.println("B");
  right(3,3);
}


}
