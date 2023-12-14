# !/usr/bin/python3
import sys

# import fcntl

connection_type = 'tty'
input_tty = 'COM4'

s = None
x = None
logfile_name = 'C:\\var\\log\\access2.in.log'
log = 1  # 0=disable anyother=enable
# output_folder='/root/yumizen_h500.data/' #remember ending/
output_folder = 'C:/root/access2.data/'  # remember ending/
alarm_time = 10

################################################

# ensure logging module is imported
try:
    import logging
except ModuleNotFoundError:
    exception_return = sys.exc_info()
    print(exception_return)
    print("Generally installed with all python installation. Refer to python documentation.")
    quit()

# ensure that log file is created/available
try:
    logging.basicConfig(filename=logfile_name, level=logging.DEBUG)
    print("See log at {}".format(logfile_name))
except FileNotFoundError:
    exception_return = sys.exc_info()
    print(exception_return)
    print("{} can not be created. Folder donot exist? No permission?".format(logfile_name))
    quit()

# import other modules
try:
    import signal
    import datetime
    import time
except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return)
    logging.debug("signal, datetime and serial modules are required. Install them")
    quit()

# import serial or socket
try:
    import serial
except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return)
    logging.debug("serial module (apt install python3-serial) is required. Install them")
    quit()


def signal_handler(signal, frame):
    global x  # global file open
    global byte_array  # global array of byte
    logging.debug('Alarm stopped')
    sgl = 'signal:' + str(signal)
    logging.debug(sgl)
    logging.debug(frame)

    try:
        if x != None:
            x.write(''.join(byte_array))  # write to file everytime LF received, to prevent big data memory problem
            x.close()
    except Exception as my_ex:
        logging.debug(my_ex)

    byte_array = []  # empty array
    logging.debug('Alarm.... <EOT> NOT received. data may be incomplate')


def get_filename():
    dt = datetime.datetime.now()
    return output_folder + dt.strftime("%Y-%m-%d-%H-%M-%S-%f")


def get_port():
    try:
        port = serial.Serial(port=input_tty, baudrate=9600, timeout=1)
        print(f"Serial port {input_tty} opened successfully")
        return port
    except:
        exception_return = sys.exc_info()
        logging.debug(exception_return)
        logging.debug('is tty really existing? Quiting')
        quit()



def my_read(port):
    print(str('received :' + str(port.read(1))))
    return port.read(1)


def my_write(port, byte):
    return port.write(byte)


# main loop##########################
if log == 0:
    logging.disable(logging.CRITICAL)

# signal.signal(signal.SIGALRM, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
port = get_port()
print('port: ' + str(port))
# byte=b'd'									#Just to enter the loop
byte_array = []  # initialized to ensure that first byte can be added
# while byte!=b'':							#removed, EOF should not exit program
while True:
    byte = my_read(port)
    # print('')
    if (byte == b''):
        logging.debug('<EOF> reached. Connection broken: details below')
        # <EOF> never reached with tty unless the device is not existing)

    else:
        byte_array = byte_array + [chr(ord(byte))]  # add everything read to array, if not EOF. EOF have no ord
        logging.debug(ord(byte))

    if (byte == b'\x05'):
        signal.alarm(0)
        logging.debug('Alarm stopped, ENQ received')
        byte_array = []  # empty array
        byte_array = byte_array + [chr(ord(byte))]  # add everything read to array required here to add first byte
        my_write(port, b'\x06')
        cur_file = get_filename()  # get name of file to open

        x = open(cur_file, 'w')  # open file
        # fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)   #lock file

        logging.debug('<ENQ> received. <ACK> Sent. Name of File opened to save data:' + str(cur_file))
        signal.alarm(alarm_time)
        logging.debug('post-enq-ack Alarm started to receive other data')
    elif (byte == b'\x0a'):
        signal.alarm(0)
        logging.debug('Alarm stopped. LF received')
        my_write(port, b'\x06')
        try:
            x.write(''.join(byte_array))  # write to file everytime LF received, to prevent big data memory problem
            byte_array = []  # empty array
        except Exception as my_ex:
            logging.debug(my_ex)
            logging.debug('Tried to write to a non-existant file??')
        logging.debug('<LF> received. <ACK> Sent. array written to file. byte_array zeroed')
        signal.alarm(alarm_time)
        logging.debug('post-lf-ack Alarm started to receive other data')
    elif (byte == b'\x04'):
        signal.alarm(0)
        logging.debug('Alarm stopped')

        try:
            if x != None:
                x.write(''.join(byte_array))  # write to file everytime LF received, to prevent big data memory problem
                # fcntl.flock(x, fcntl.LOCK_UN)   #unlock file not required, because we are closing it
                x.close()

        except Exception as my_ex:
            logging.debug(my_ex)

        byte_array = []  # empty array
        logging.debug('<EOT> received. array( only EOT remaining ) written to file. File closed:')
