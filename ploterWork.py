import matplotlib.pyplot as plt
from datetime import datetime

# use matplotlib

def getCoordinates(needNormal):
    f = open('coordinatesXY', 'r')
    coordinates = f.read().split('\n')
    coordinates.pop()
    y = []
    x = []
    for i in coordinates:
        y.append(float(i.split(',')[1]))
        x.append(i.split(',')[0].replace('.', '\n').replace('(', '\n('))
    if(len(x)>=34 and needNormal):
        x,y=coordinateNormalization(x,y)
    return x, y #34

def coordinateNormalization(x,y):
    nx=[]
    ny=[]
    for i in range(0,len(x)):
        if((i%2!=0) and (i-1!=len(x))):
            ny.append((int(y[i])+int(y[i-1]))/2)
            nx.append(x[i])
        elif(i+1==len(x)):
            ny.append(int(y[i]))
            nx.append(x[i])
    return nx,ny

def getRangeForGraphic(x, range):
    s = 0
    e = len(x)
    if (range.count(',') != 0):
        firstDate = datetime.strptime(range.split(',')[0], "%d.%m.%y")
        secondDate = datetime.strptime(range.split(',')[1], "%d.%m.%y")
        for i in x:
            currentDate = datetime.strptime(i.split('(')[0].replace('\n', '.').strip('.'), "%d.%m.%y")
            if (currentDate >= firstDate):
                s = x.index(i)
                break
        newX = list(x)
        newX.reverse()
        for i in newX:
            currentDate = datetime.strptime(i.split('(')[0].replace('\n', '.').strip('.'), "%d.%m.%y")
            if (currentDate <= secondDate):
                e = x.index(i) + 1
                break
    else:
        firstDate = datetime.strptime(range, "%d.%m.%y")
        for i in x:
            currentDate = datetime.strptime(i.split('(')[0].replace('\n', '.').strip('.'), "%d.%m.%y")
            if (currentDate >= firstDate):
                s = x.index(i)
                break
    return s, e


def getStrRangeForGraphic(x):
    return str(x[0].replace('\n', '.').split('(')[0].strip('.')
               + ',' +
               x[-1].replace('\n', '.').split('(')[0].strip('.'))


def createAndSaveGraphic(dateRange='',needNormal=False):
    plt.style.use('seaborn-whitegrid')
    fig, ax = plt.subplots()
    x, y = getCoordinates(needNormal)
    if (dateRange == ''):
        dateRange = getStrRangeForGraphic(x)
    start, end = getRangeForGraphic(x, dateRange)
    newY = y[start:end]
    ax.plot(x[start:end], y[start:end], marker="o")
    for i in range(len(newY)):
        plt.text(i + 0.05, newY[i], newY[i])
    plt.savefig('{0}.{1}'.format("graphic", 'png'))
# createAndSaveGraphic()
# sys.exit()
