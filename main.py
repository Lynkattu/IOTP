from machine import Pin, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep

INPUTCODE = ""
PASSWORD = "1234"
#------------------------------LCD-Init----------------------------------------
SCLPIN = Pin(9, Pin.OUT)
SDAPIN = Pin(8, Pin.OUT)

I2C_ADD = 0x27
I2C_ROWS = 2
I2C_COLUMNS = 16

i2c = I2C(id=0, sda=SDAPIN, scl=SCLPIN, freq=40000)
lcd = I2cLcd(i2c, I2C_ADD, I2C_ROWS, I2C_COLUMNS)

#------number of rows and columns in keypad------
ROWS = 4
COLUMNS = 3
#-------Keypad row and column key pins-----------
ROWPINS = [Pin(0, Pin.OUT), Pin(1, Pin.OUT), Pin(2, Pin.OUT), Pin(3, Pin.OUT)]
COLUMNPINS = [Pin(4, Pin.IN, Pin.PULL_DOWN), Pin(5, Pin.IN, Pin.PULL_DOWN), Pin(6, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN)]
#-------------------------------------------------
KEY_UP = 0
KEY_DOWN = 1
#Keypad
KEY_MATRIX =  [
                  ["1","2","3"],
                  ["4","5","6"],
                  ["7","8","9"],
                  ["<","0","="]
               ]

memoryCol = 0
memoryRow = 0

#Scan key status
def scanKeypad(row,col):
   ROWPINS[row].on()
   keyValue = None

   if COLUMNPINS[col].value() == KEY_DOWN:
      keyValue = KEY_DOWN
   elif COLUMNPINS[col].value() == KEY_UP:
      keyValue = KEY_UP
   
   ROWPINS[row].off()
   return keyValue

#Initialize program
def init():
   #set all row pins to 0
   for p in range(ROWS):
      ROWPINS[p].off()

def keyPad():
    global INPUTCODE
    userinput = ""
    isReleased = True

    for row in range(ROWS):
        for col in range(COLUMNS):
            if scanKeypad(row,col) == KEY_DOWN:
                userinput = KEY_MATRIX[row][col]
                if userinput == "<":
                    INPUTCODE = INPUTCODE[:-1]
                    lcd.clear()
                elif userinput == "=":
                    if INPUTCODE == PASSWORD:
                        print("Welcome")
                        INPUTCODE = ""
                        lcd.clear()
                    else:
                        print("Invalid password")
                else:
                    INPUTCODE += userinput

                print("Last input: " + userinput)
                print("Input Code: " + INPUTCODE)
                isReleased = False
                memoryCol = col
                memoryRow = row
    #Check when key is released
    while isReleased == False:
        if scanKeypad(memoryRow,memoryCol) == KEY_UP:
            isReleased = True
   
def lcdOutput():
    lcd.move_to(0,0)
    lcd.putstr(INPUTCODE)

init()

while True:
    keyPad()
    lcdOutput()
   
   

