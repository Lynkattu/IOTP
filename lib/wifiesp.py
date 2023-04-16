import machine
import time

Tx_BUF_SIZE = 1024
Rx_BUF_SIZE = 1024 * 4

END = "\r\n"

# AT Response
ATR_OK = "OK" + END
ATR_ERROR = "ERROR" + END
ATR_FAIL = "FAIL" + END
ATR_WIFI_CONNECTED = "WIFI CONNECTED" + END
ATR_WIFI_GOT_IP = "WIFI GOT IP" + END
ATR_WIFI_DISCONNECTED = "WIFI DISCONNECTED" + END
ATR_WIFI_AP_NOT_FOUND = "WIFI AP NOT FOUND" + END
ATR_WIFI_AP_WRONG_PWD = "WIFI AP WRONG PASSWORD" + END

class ESP:
  def __init__(self, uart=0, baud=115200, txPin=0, rxPin=1, debug=False):
    self._RxData = bytes()
    self._uartnum = uart
    self._baudrate = baud
    self._rxPin = machine.Pin(rxPin)
    self._txPin = machine.Pin(txPin)
    self._debug = debug
    # self._cuart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
    self._uart = machine.UART(self._uartnum, baudrate=self._baudrate, tx=self._txPin, rx=self._rxPin, bits=8, parity=None, stop=1, rxbuf=Rx_BUF_SIZE)
    # self._uart.init(uart=self._uartnum, baud=self._baudrate, tx=self._txPin, rx=self._rxPin)

  def _transmit(self, atData, delay=1):
    time.sleep(delay)
    self.dmsg("TRANSMIT: " + atData)
    self._RxData = b""
    try:
      self._uart.write(atData + END)
      time.sleep(delay)
      while self._uart.any() > 0:
        self._RxData += self._uart.read(Rx_BUF_SIZE)
      # self.dmsg(self._RxData)
      # self._cuart.write(self._RxData)
      # if ATR_OK in self._RxData:
      #   return self._RxData
      return self._RxData
    except Exception as e:
      self.dmsg(e)
      return ""
  
  # GET rid of this functionality and all that are depending on it
  def dmsg(self, data, decode=False):
    if self._debug is True:
      if decode is False:
        print(data)
      else:
        print(data.decode())

  def setWiFiMode(self, mode=3):
    TxData = "AT+CWMODE_CUR="+str(mode)+END
    recv = self._transmit(TxData)

  def testESP(self):
    atData = "AT"
    recv = self._transmit(atData)
    self.dmsg("ESP_TEST: ")
    self.dmsg(recv, decode=True)
  
  def checkESPVersion(self):
    atData = "AT+GMR"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def listCmds(self):
    atData = "AT+CMD?"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def availableRAM(self):
    atData = "AT+USERRAM?"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def querySysRAM(self):
    atData = "AT+SYSRAM?"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def querySysFLASH(self):
    atData = "AT+SYSFLASH?"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  # AT+FS=<type>,<operation>,<filename>,<offset>,<length>
  # type - 0: FATFS
  # operations - 0: delete, 1: write, 2: read, 3: query_file_size, 4: list_files
  # offset: apply number to read/write
  # length: amount of stored bits

  # list files in root dir
  def listFiles(self):
    atData = 'AT+FS=0,4,"."'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def readFile(self, filename, foffset, fsize):
    atData = 'AT+FS=0,2,"' + filename + '",' + str(foffset) + ',' + str(fsize)
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  # WIFI related AT-CMDs
  def queryWiFiMode(self):
    atData = "AT+CWMODE?"
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  # AT+CWMODE=<mode>[,<auto_connect>]
  # mode - 0: disabled, 1: station, 2: SoftAP, 3: SoftAP+Station
  # auto_connect - 0: no, 1: yes
  def setWiFiMode(self, mode=0, auto_connect=0):
    atData = 'AT+CWMODE=' + str(mode) + ',' + str(auto_connect)
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def queryWiFiStatus(self):
    atData = 'AT+CWSTATE?'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def queryAPList(self, ssid):
    atData = 'AT+CWLAP'
    atData += '="' + ssid + '"'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def queryMAC(self):
    atData = 'AT+CIPSTAMAC?'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def setMAC(self, mac):
    atData = 'AT+CIPSTAMAC="' + mac + '"'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def queryHostname(self):
    atData = 'AT+CWHOSTNAME?'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def setHostname(self, hostname):
    atData = 'AT+CWHOSTNAME="' + hostname + '"'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  # <ssid>],[<pwd>][,<bssid>][,<pci_en>][,<reconn_interval>][,<listen_interval>][,<scan_mode>][,<jap_timeout>][,<pmf>]
  def connectAP(self, ssid, pwd=''):
    atData = 'AT+CWJAP="' + ssid + '","' + pwd + '"'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  def queryNetworkDetails(self):
    atData = 'AT+CIPAP?'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  def queryCountryCode(self):
    atData = 'AT+CWCOUNTRY?'
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)
  
  # AT+CWCOUNTRY=<country_policy>,<country_code>,<start_channel>,<total_channel_count>
  # <country_policy>:
  #   0: will change the county code to be the same as the AP that the ESP device is connected to.
  #   1: the country code will not change, always be the one set by command.
  # <country_code>: country code. Maximum length: 3 characters.
  # <start_channel>: the channel number to start. Range: [1,14].
  # <total_channel_count>: total number of channels.
  def setCountryCode(self, cp, cn, start_channel, total_channel_count):
    atData = 'AT+CWCOUNTRY='
    atData += str(cp) + ','
    atData += '"' + cn + '",'
    atData += str(start_channel) + ','
    atData += str(total_channel_count)
    recv = self._transmit(atData)
    self.dmsg(recv, decode=True)

  # AT+HTTPCLIENT=<opt>,<content-type>,<"url">,[<"host">],[<"path">],<transport_type>[,<"data">][,<"http_req_header">][,<"http_req_header">][...]
  # <opt> - 1: HEAD, 2: GET, 3: POST, 4: PUT, 5: DELETE
  # <content-type>: 0: application/x-www-form-urlencoded, 1: application/json, 2: multipart/form-data, 3: text/xml
  # <”host”>: domain name or IP address.
  # <”path”>: HTTP Path.
  # transport_type> - 1: HTTP_TRANSPORT_OVER_TCP, 2: HTTP_TRANSPORT_OVER_SSL
  # query parameter implementation missing
  def httpGET(self, host, path, tp_type=1, ct=1, tp=1):
    # atData = 'AT+HTTPCLIENT=2,0,"http://httpbin.org/get","httpbin.org","/get",1'
    atData = 'AT+HTTPCLIENT=2,' + str(ct) # opt & content-type
    atData += ',"http://' if tp == 1 else ',"https://' # url-protocol
    atData += host + path + '"' # url
    atData += ',"' + host + '"' # host
    atData += ',"' + path + '"' # path
    atData += ',' + str(tp) # transport-type
    print(atData)
    recv = self._transmit(atData, delay=2)
    self.dmsg(recv, decode=True)
    return recv
  
  # Posting data in x-www-form-urlencoded format
  def httpPOST(self, host, path, data, tp_type=1, tp=1):
    # data format "id=1&pot=3"
    # atData = 'AT+HTTPCLIENT=3,0,"http://httpbin.org/post","httpbin.org","/post",1,"field1=value1&field2=value2"'
    atData = 'AT+HTTPCLIENT=3,0'
    atData += ',"http://' if tp == 1 else ',"https://' # url-protocol
    atData += host + path + '"' # url
    atData += ',"' + host + '"' # host
    atData += ',"' + path + '"' # path
    atData += ',' + str(tp) # transport-type
    atData += ',"' + data + '"' # data

    recv = self._transmit(atData, delay=2)
    self.dmsg(recv, decode=True)

