from machine import Pin, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep
from wifiesp import ESP

#-----------------------------wifi-init--------------------------------------
debug = True
device_id = 8266 # Device ID
poll_rate = 30 # Polling cloud with new data
# See "private" area from https://standards-oui.ieee.org/oui/oui.txt
mac = "00:00:6C:00:00:01" # ESP MAC
hostname = "beginner" # ESP hostname
target = "dinosaurus.switzerlandnorth.cloudapp.azure.com" # IP or FQDN of the backend (in the cloud)
ssid="Wokwi-GUEST" # WiFi network name
password = "" # WiFi password

wifi_conn = ESP(uart=0, baud=115200, txPin=0, rxPin=1, debug=debug)
wifi_conn.setMAC(mac) # set the ESP mac
wifi_conn.setHostname(hostname) # set the ESP hostname
wifi_conn.connectAP(ssid=ssid, pwd=password)

#-----------------------------keypad-input--system-password--------------------
INPUTCODE = ""
PASSWORD = "1234"
#------------------------------LCD-Init---------------------------------------- dinosaurus.switzerlandnorth.cloudapp.azure.com 
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
ROWPINS = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(19, Pin.OUT)]
COLUMNPINS = [Pin(20, Pin.IN, Pin.PULL_DOWN), Pin(21, Pin.IN, Pin.PULL_DOWN), Pin(22, Pin.IN, Pin.PULL_DOWN)]
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
                        lcdMessage("Door open",3)
                    else:
                        lcdMessage("Try again",1)
                    INPUTCODE = ""
                    getPassword()
                    lcd.clear()
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
   
def lcdMessage(msg, duration):
    pos = int(8-(len(msg)/2))
    lcd.clear()
    lcd.move_to(pos,0)
    lcd.putstr(msg)
    sleep(duration)

def lcdOutput():
    lcd.move_to(0,0)
    lcd.putstr(INPUTCODE)

def decodePin(recv):
    pin = ""
    for i in reversed(range(len(recv))):
        if recv[i] == ",":
            break
        if recv[i] >= "0" and recv[i] <= "9":
            pin = ''.join((recv[i],pin))
    return pin

def getPassword():
    global PASSWORD
    pin = str(wifi_conn.httpGET(host=target, path=":3000/current-pin"))
    PASSWORD = decodePin(str(pin))
    print("password: " + PASSWORD)

def main():
    #--initialize program--
    getPassword()
    for p in range(ROWS):
        ROWPINS[p].off()
    #----------------------
    while True:
        keyPad()
        lcdOutput()

main()