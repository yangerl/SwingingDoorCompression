# methods
def init_Snap(archived_pnt, value, trade_date, time,POSITIVE_DEV,NEGATIVE_DEV):
    prev_val = float(archived_pnt['value'])
    prev_time = int(archived_pnt['time_value'])
    time = int(time)
    value = float(value)
    Smax = (value+POSITIVE_DEV*value-prev_val)/(time-prev_time)
    Smin = (value-NEGATIVE_DEV*value-prev_val)/(time-prev_time)
    slope = (value-prev_val)/(time-prev_time)
    return {
        'value' : value,
        'trade_date' : trade_date,
        'time': time,
        'Smax': Smax,
        'Smin': Smin,
        'Slope' : slope
    }

def snap2archive(snapshot, bool):
    return {
        'value' : snapshot['value'],
        'trade_date' : snapshot['trade_date'],
        'time_value' : snapshot['time'],
        'is_snap' : bool,
    }

# SETUP STAGE

path = raw_input("Enter the path of the textfile: ")
filename = raw_input("Enter the filename of the textfile: ")
POSITIVE_DEV = float(raw_input("Enter the maximum positive deviation (in %): "))/100
NEGATIVE_DEV = float(raw_input("Enter the maximum negative deviation (in %): "))/100
metric = raw_input("Enter the metric (open, close, high, low, volume): ")
output = '\nStarting Compression using the '+ metric \
        + ' price \nwith positive deviation '+ str(POSITIVE_DEV) \
        +'\nwith negative deviation '+ str(NEGATIVE_DEV) \
        +'\nfor the file '+ path + filename
print output

CONVERSION = {
    'symbol' : 0,
    'date' : 1,
    'open' : 2,
    'high' : 3,
    'low' : 4,
    'close' : 5,
    'volume' : 6,
}
SYMBOL = CONVERSION['symbol']
METRIC = CONVERSION[metric]
DATE = CONVERSION['date']
# ARCHIVE array object format = [{value: value, date: trade_date, time_value: counter,},]
ARCHIVE = [
]
# Array index of the next archive value
archive_count = 0

# SNAPSHOT format = {value: value, date: trade_date, time_value: counter, Smax: smax, Smin: Smin, slope: slope}
SNAPSHOT = {
    'value' : None,
    'trade_date' : None,
    'time': None,
    'Smax': None,
    'Smin': None,
    'Slope' : None
}
# INCOMING format = {value: value, date: trade_date, time_value: counter, Smax: smax, Smin: Smin}
INCOMING = {
    'value' : None,
    'trade_date' : None,
    'time': None,
    'Smax': None,
    'Smin': None,
    'Slope' : None
}



f=open(path + filename,'r')
counter = 0

# NOTE THIS ASSUMES THAT EVERY NEW LINE IN THE FILE IS 1 TRADE DAY AFTER THE PREVIOUS LINE
for line in f.readlines():
    data = line.split(',')
    value = data[METRIC]
    trade_date = data[DATE]

    if counter == 0:
        # This is the header so we skip this iteration
        pass
    elif counter == 1:
        # This is the first data point, always added into archive
        SYMBOL = data[SYMBOL]
        ARCHIVE = [{
            'value' : value,
            'trade_date' : trade_date,
            'time_value' : counter,
            'is_snap'   : False,
        }]
        archive_count += 1
    elif counter == 2:
        # This is the first snapshot that we will recieved
        SNAPSHOT = init_Snap(
            ARCHIVE[archive_count-1],
            value,
            trade_date,
            counter,
            POSITIVE_DEV,
            NEGATIVE_DEV,
        )

    else:
        # Set up incoming value
        INCOMING = init_Snap(
            ARCHIVE[archive_count-1],
            value,
            trade_date,
            counter,
            POSITIVE_DEV,
            NEGATIVE_DEV,
        )
        if SNAPSHOT['Smin'] <= INCOMING['Slope'] <= SNAPSHOT['Smax']:
            # It is within the filtration bounds, edit the INCOMING and 
            # set the SNAP. When editing INCOMING, make sure that the incoming
            # slopes are not bigger than the current SNAPSHOT's slopes
            INCOMING['Smax'] = min(SNAPSHOT['Smax'],INCOMING['Smax'])
            INCOMING['Smin'] = max(SNAPSHOT['Smin'],INCOMING['Smin'])
            SNAPSHOT = INCOMING
        else:
            # It is outside the bounds so we must archive the current SNAP
            # and init a new snap using this new archived point and INCOMING
            ARCHIVE.append(snap2archive(SNAPSHOT, False))
            archive_count += 1
            SNAPSHOT = init_Snap(
                ARCHIVE[archive_count-1],
                value,
                trade_date,
                counter,
                POSITIVE_DEV,
                NEGATIVE_DEV,
            )
    counter += 1
# Always add the latest point into the archive
ARCHIVE.append(snap2archive(SNAPSHOT, True))
temp = filename.split('.csv')
target = open(path+temp[0]+'_compressed.csv', 'w')
target.truncate()
# Create Header
target.write('SYMBOL,TRADE_DATE,'+metric.upper()+',IS_SNAP' )
target.write("\n")

line_count = 1
for obj in ARCHIVE:
    line = SYMBOL+','+obj['trade_date']+','+str(obj['value'])+','+str(obj['is_snap'])
    target.write(line)
    target.write("\n")
    line_count += 1

print "Completed Compression of " + str(counter) + "lines to " + str(line_count) +"lines."







