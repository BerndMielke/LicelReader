import socket
import configparser
import os
import matplotlib
import matplotlib.pyplot as plt
from LicelReader import *
from LicelUtil import *



config = configparser.ConfigParser()
config.read('LicelUDP.ini')
data_path = config['Reader']['dataDir']
ds0 = int(config['Reader']['ds0'])
logPlot = bool(config['Reader']['logPLot'])
print(data_path)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).


# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client.bind(("", 2088))
isInitialized = False
plt.ion()
fig, ax = plt.subplots()


while True:
    # Thanks @seym45 for a fix
    data, addr = client.recvfrom(1024)
    
    filename = str(data).split('\\')[-1]
    if filename.find('START') > 0 or filename.find('STOP') > 0 :
        continue 
    filename = filename.split('\'')[0]
    filepath = os.path.join(data_path, filename)
    file = LicelFileReader(filepath)
    print("file read")
    if not isInitialized :
        isInitialized = True
        print("initialized")
        x = file.dataSet[ds0].x_axis_m()
        y = file.dataSet[ds0].physData
        x2 = file.dataSet[ds0].x_axis_m()
        y2 = file.dataSet[ds1].physData
        if( logPLot) :
            (line1, ) = ax.semilogy(x,y)
            (line2, ) = ax.semilogy(x2,y2)
        else : 
            (line1, ) = ax.plot(x,y)
            (line2, ) = ax.plot(x2,y2)
        fig.canvas.draw()
        fig.canvas.flush_events()
        print("plotted")
    else :
        line1.set_ydata(file.dataSet[ds0].physData)
        line1.set_ydata(file.dataSet[ds1].physData)
        fig.canvas.draw()
        fig.canvas.flush_events()
        print("udpate") 
     
    

    