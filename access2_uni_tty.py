import sys
import logging
import signal
import datetime
import serial

connection_type = 'tty'
input_tty = 'COM3'
s = None
x = None
logfile_name = 'C:\\var\\log\\access2.in.log'
log = 1
output_folder = 'C:/root/access2.data/'
alarm_time = 10

# Configure logging
logging.basicConfig(filename=logfile_name, level=logging.DEBUG)

def signal_handler(signal, frame):
    global x
    global byte_array
    try:
        if x:
            x.write(''.join(byte_array))
            x.close()
    except Exception as e:
        logging.exception("Error while handling signal: {}".format(e))
    byte_array = []
    logging.warning('Alarm: <EOT> NOT received. Data may be incomplete.')

def get_filename():
    dt = datetime.datetime.now()
    return output_folder + dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

def get_port():
    try:
        port = serial.Serial(port=input_tty, baudrate=9600, timeout=1)
        logging.info(f"Serial port {input_tty} opened successfully")
        return port
    except serial.SerialException as se:
        logging.exception(f"Error opening serial port: {se}")
        sys.exit(1)

def my_read(port):
    data = port.read(1)
    logging.debug(f"Received: {data}")
    return data

def my_write(port, byte):
    port.write(byte)

if log == 0:
    logging.disable(logging.CRITICAL)

signal.signal(signal.SIGTERM, signal_handler)
port = get_port()
logging.info(f"Connected to port: {port}")

byte_array = []
while True:
    byte = my_read(port)
    if not byte:
        logging.warning('<EOF> reached. Connection broken')
    else:
        byte_array.append(chr(ord(byte)))
        logging.debug(f"Received byte: {ord(byte)}")

    if byte == b'\x05':
        signal.alarm(0)
        byte_array = [chr(ord(byte))]
        my_write(port, b'\x06')
        cur_file = get_filename()
        try:
            x = open(cur_file, 'w')
            logging.info(f'<ENQ> received. <ACK> Sent. File opened: {cur_file}')
            signal.alarm(alarm_time)
        except IOError as ioe:
            logging.exception(f"Error opening file {cur_file}: {ioe}")

    elif byte == b'\x0a':
        signal.alarm(0)
        my_write(port, b'\x06')
        try:
            x.write(''.join(byte_array))
            byte_array = []
            logging.info('<LF> received. <ACK> Sent. Data written to file.')
            signal.alarm(alarm_time)
        except Exception as e:
            logging.exception(f"Error writing to file: {e}")

    elif byte == b'\x04':
        signal.alarm(0)
        try:
            if x:
                x.write(''.join(byte_array))
                x.close()
                logging.info('File closed.')
        except Exception as e:
            logging.exception(f"Error closing file: {e}")
        byte_array = []
        logging.info('<EOT> received. File written and closed.')
