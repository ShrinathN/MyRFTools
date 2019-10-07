#!/bin/python
import tkinter
import serial
import time
import threading

FONT_SIZE = 75
DATA_FONT_SIZE = 100

prt = serial.Serial('/dev/ttyUSB0', baudrate=115200)

def serial_data_reader():
	while(True):
		data_read = prt.read(10)
		label_0x1_d['text'] = str(hex(data_read[0]))
		label_irq_d['text'] = str(hex(data_read[1]))
		label_payload_bytes_d['text'] = str(int(data_read[2]))
		label_last_updated_d['text'] = time.ctime()
		label_rssi_d['text'] = str(-137 + data_read[4]) + 'dBm'
		try:
			label_data['text'] = data_read[5:]
		except:
			continue


root = tkinter.Tk()
#opmode
label_0x1 = tkinter.Label(root, fg='red', text="RegOpMode (0x01)", font=('',FONT_SIZE))
label_0x1.grid(row=0,column=0)
label_0x1_d = tkinter.Label(root, text="", font=('',FONT_SIZE))
label_0x1_d.grid(row=0,column=1)
#irqflags
label_irq = tkinter.Label(root,fg='red', text="RegIrqFlags (0x12)", font=('',FONT_SIZE))
label_irq.grid(row=1, column=0)
label_irq_d = tkinter.Label(root, text="", font=('',FONT_SIZE))
label_irq_d.grid(row=1,column=1)
#payload bytes
label_payload_bytes = tkinter.Label(root,fg='red', text="Payload Bytes", font=('',FONT_SIZE))
label_payload_bytes.grid(row=2, column=0)
label_payload_bytes_d = tkinter.Label(root, text="", font=('',FONT_SIZE))
label_payload_bytes_d.grid(row=2, column=1)
#RSSI
label_rssi = tkinter.Label(root,fg='red', text="RSSI", font=('',FONT_SIZE))
label_rssi.grid(row=3, column=0)
label_rssi_d = tkinter.Label(root, text="", font=('',FONT_SIZE))
label_rssi_d.grid(row=3, column=1)
#payload data
label_data = tkinter.Label(root,fg='green', text='', font=('', DATA_FONT_SIZE))
label_data.grid(row=4, column=0, columnspan=2)
#last updated
label_last_updated = tkinter.Label(root, text="Last Updated")
label_last_updated.grid(row=5, column=0)
label_last_updated_d = tkinter.Label(root, text="")
label_last_updated_d.grid(row=5, column=1)

#starting thread to update data
refresh_thread = threading.Thread(target=serial_data_reader, args=())
refresh_thread.start()

root.mainloop()
