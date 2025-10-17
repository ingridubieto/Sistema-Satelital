import serial
device = 'COM6'
mySerial = serial.Serial(device, 9600)
print ("Empezamos")
while True:
    if mySerial.in_waiting > 0:
        linea = mySerial.readline().decode('utf-8').rstrip()
        trozos = linea.split (':')
        print(trozos)