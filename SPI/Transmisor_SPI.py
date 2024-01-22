from spi_master import SPI_Master
from machine import Pin, SPI, I2C
from sdcard import SDCard
from utime import sleep_ms
from uos import VfsFat, mount
from os import listdir
import array

#led
led = Pin("LED", Pin.OUT)
lt = False

def led_t():
    global lt
    if lt:
        led.value(0)
        lt = False
    else:
        led.value(1)
        lt = True

#SD
cs = Pin(13)
spi = SPI(1,
          baudrate=1000000,
          polarity=0,
          phase=0,
          sck = Pin(10),
          mosi = Pin(11),
          miso = Pin(12))

sd = SDCard(spi, cs)
vol = VfsFat(sd)
mount(vol, "/sd")

#SPI
master = SPI_Master(mosi_pin=3, miso_pin=4, sck_pin=2, csel_pin=5, spi_words=1, F_SPI=1_000_000)


datos = []
cont = 0

#Recopilar datos
for ruta in listdir("/sd"):
    if cont >= 14:
        break
    if ruta[:5] == "Datos":
        archivo = open("/sd/"+ruta, "r")
        aux = archivo.read()
        archivo.close()
        
        cruces = 0
        
        for linea in aux.split("\n"):
            if linea == "":
                continue
            cruces += int(linea[:2])
        
        datos.insert(0,cruces)
        cont += 1
#sync
inicio = Pin(18,Pin.IN)
while inicio.value() == 0:
    sleep_ms(1)

#eviar datos
for dato in datos:
    paquete = array.array("I", [int("0x"+"{:04d}".format(dato).encode("utf-8").hex())])
    master.write(paquete)
    print("Valor enviado:", dato)
    sleep_ms(100)
    led_t()

paquete = array.array("I", [int("0x"+"@Fin".encode("utf-8").hex())])
master.write(paquete)
led.value(0)

print("Terminar conexion")
print(datos)
