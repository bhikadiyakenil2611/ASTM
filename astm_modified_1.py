import serial

def send_ack(serial_port):
    # Assuming ACK is a single byte, you can modify this based on your requirement
    ack_byte = b'\x06'  # ASCII value for ACK
    
    try:
        # Send ACK
        serial_port.write(ack_byte)
        print("ACK sent successfully")
    except Exception as e:
        print(f"Error sending ACK: {e}")

def main():
    # Adjust these settings based on your setup
    serial_port_name = 'COM1'  # Change to the appropriate serial port
    baud_rate = 9600  # Change to the appropriate baud rate
    
    try:
        # Open serial port
        serial_port = serial.Serial(port=serial_port_name, baudrate=baud_rate, timeout=1)
        print(f"Serial port {serial_port_name} opened successfully")

        while True:
            # Read data from the serial port
            data = serial_port.read(1)  # Adjust the number of bytes to read based on your data format
            
            if data:
                print(f"Received data: {data}")

                # Process the received data

                # Send acknowledgment
                send_ack(serial_port)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the serial port when done
        if serial_port.is_open:
            serial_port.close()
            print("Serial port closed")

if _name_ == "__main__":
    main()
    
    
    
    
    
    
    
###################################################################################################################################################################################################################################
###################################################################################################################################################################################################################################




#!/usr/bin/python3
import sys

# import fcntl

# defaults###############

############################
##########Start of (tty vs tcp)######
############################

# tty -> uncoment as needed
connection_type = 'tty'
input_tty = 'COM4'

# tcp ->uncomment as needed
# connection_type = 'tcp'
# # host_address='10.206.10.26'
# # host_address='11.207.1.1'
# # host_address='12.207.3.240'
# host_address = '0.0.0.0'
host_port = '2575'

############################
##########END of (tty vs tcp)######
############################

####################################################################################*********
# #!/usr/bin/python3
# astm_log_filename='C:\\var\log\\vitros_read.log'  #for windows
# file2mysql_log_filename='C:\\var\log\\vitros_write.log'   #for Windows
# #if you wish to be specific
# #host_address='12.207.3.240'
# #host_address='11.207.1.1'
# #if you wish general declaration
# host_address='127.0.0.1'
# host_port='2577'
# select_timeout=1
# alarm_time=10
# #trailing slash is must to reconstruct path
#
# # inbox_data='/root/vitros.inbox.data/'
# # outbox_data='/root/vitros.outbox.data/'
# inbox_arch='C:\\root\\vitros.inbox.data\\'     #for Windows
# outbox_arch='C:\\root\\vitros.outbox.data\\'   #for Windows
# equipment='VITROS3600'
####################################################################################*********


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
if (connection_type == 'tty'):
    try:
        import serial
    except ModuleNotFoundError:
        exception_return = sys.exc_info()
        logging.debug(exception_return)
        logging.debug("serial module (apt install python3-serial) is required. Install them")
        quit()
elif (connection_type == 'tcp'):
    try:
        import socket
    except ModuleNotFoundError:
        exception_return = sys.exc_info()
        logging.debug(exception_return)
        logging.debug("socket module is required. Generally installed with basic python installation.")
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
    if (connection_type == 'tty'):
        try:
            port = serial.Serial(input_tty, baudrate=9600, stopbits=serial.STOPBITS_ONE)
            print(port)
            return port
        except:
            exception_return = sys.exc_info()
            logging.debug(exception_return)
            logging.debug('is tty really existing? Quiting')
            quit()

    elif (connection_type == 'tcp'):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        """Set TCP keepalive on an open socket.
    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

        try:
            s.bind((host_address, int(host_port)))  # it is a tuple
        except:
            exception_return = sys.exc_info()
            logging.debug(exception_return)
            logging.debug('Some problem in bind. is ip and port correct? Quiting')
            quit()
        logging.debug('post-bind pre-listen')
        s.listen(1)

        logging.debug('Listening Socket (s) details below:')
        logging.debug(s)

        logging.debug('Waiting for connection from a client....')
        conn_tuple = s.accept()  # This waits till connected

        logging.debug('Client request received. Listening+ Accepting Socket (conn_tuple) details below:')
        logging.debug(conn_tuple)

        return conn_tuple[0]


def my_read(port):
    if (connection_type == 'tty'):
        print(str('data:' + str(port.read(1))));
        return port.read(1)
    elif (connection_type == 'tcp'):
        try:
            return port.recv(1)
        except Exception as my_ex:
            logging.debug(my_ex)
            logging.debug('Network disconnection??')
            return b''


def my_write(port, byte):
    if (connection_type == 'tty'):
        return port.write(byte)
    elif (connection_type == 'tcp'):
        return port.send(byte)


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
        if (connection_type == 'tcp'):
            logging.debug('(Broken) Listening Socket (s) details below:')
            logging.debug(s)
            logging.debug('(From While)Waiting for connection from a client....')
            conn_tuple = s.accept()  # This waits till connected
            logging.debug(
                '(From While) Client request received. Listening+ Accepting Socket (conn_tuple) details below:')
            logging.debug(conn_tuple)
            port = conn_tuple[0]

    else:
        byte_array = byte_array + [chr(ord(byte))]  # add everything read to array, if not EOF. EOF have no ord
        logging.debug(ord(byte))

    if (byte == b'\x05'):
        signal.alarm(0)
        logging.debug('Alarm stopped')
        byte_array = []  # empty array
        byte_array = byte_array + [chr(ord(byte))]  # add everything read to array requred here to add first byte
        print("sending ACK...")
        my_write(port, b'\x06');
        print("sent ACK...!")
        cur_file = get_filename()  # get name of file to open

        x = open(cur_file, 'w')  # open file
        # fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)   #lock file

        logging.debug('<ENQ> received. <ACK> Sent. Name of File opened to save data:' + str(cur_file))
        signal.alarm(alarm_time)
        logging.debug('post-enq-ack Alarm started to receive other data')
    elif (byte == b'\x0a'):
        signal.alarm(0)
        logging.debug('Alarm stopped. LF received')
        my_write(port, b'\x06');
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
