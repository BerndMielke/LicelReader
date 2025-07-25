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

numDataSets = int(config['Reader']['numDataSets'])
ds = []
line = []
for i in range(numDataSets):
  ds.append(int(config['Reader']['ds' + str(i)]))


logPlot = bool(config['Reader']['logPlot'])


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

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
    print(filepath)
    
    ax.set_title(filename)
    ax.set_xlabel('m')
    if file.dataSet[0].dataType == 0 :
        ax.set_ylabel('mV')
    elif file.dataSet[0].dataType == 1 :
        axes.set_ylabel('MHz')
    else :             
        axes.set_ylabel('AU')
    if not isInitialized :
        isInitialized = True
        for i in range(numDataSets) :
            x = file.dataSet[ds[i]].x_axis_m()
            y = file.dataSet[ds[i]].physData

            if( logPlot) :
                (ll, )  = ax.semilogy(x,y)
                line.append(ll)
            else :
                (ll, ) = ax.plot(x,y)
                line.append(ll)
        
        fig.canvas.draw()
        fig.canvas.flush_events()

    else :
        for i in range(numDataSets) :
            line[i].set_ydata(file.dataSet[ds[i]].physData)

        fig.canvas.draw()
        fig.canvas.flush_events()




