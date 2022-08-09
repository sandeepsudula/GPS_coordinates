import serial
from datetime import datetime
from time import time,sleep
import csv
import timeit
from time import perf_counter

def parse_gprmc(data):
#Getting Time stamp
	time=data[1]
	time_hr=time[:2]
	time_min=time[2:4]
	time_sec=time[4:6]
#print(time_hr,time_misleep(60 - time() % 60)sleen,time_sec)
#convert NMEA coordinates into decimal coordinates
	lat_nmea=data[3]
	lat_degree=lat_nmea[:2]
	if data[4] == 'S':
		latitude_degree=float(lat_degree)*-1
	else:
		latitude_degree=float(lat_degree)
#change it back to a strange and remove the .0
	latitude_degree=str(latitude_degree).strip('.0')
	lat_ddd=lat_nmea[2:10]
	lat_mmm=float(lat_ddd)/60
	lat_mmm=str(lat_mmm).strip('0.')[:8]
	latitude=latitude_degree+"."+lat_mmm
#convert longitudes into coordinates
	long_nmea=data[5]
	long_degrees=long_nmea[:3]
	if data[6] == 'W':
		longitude_degree=float(long_degrees)*-1
	else:
		longitude_degree=float(long_degrees)
#change it back to a strange and remove the .0
	longitude_degree=str(longitude_degree).strip('.0')
	long_ddd=long_nmea[3:10]
	long_mmm=float(long_ddd)/60
	long_mmm=str(long_mmm).strip('0.')[:8]
	longitude=longitude_degree+"."+long_mmm
	utc_time=time_hr+"hrs"+" "+time_min+"min"+" "+time_sec+"sec"
	return ({"gprmc": {"longitude": longitude, "latitude":latitude, "utc_time":utc_time, "no_of_sat":None}})
#	print ({"gprmc": {"Longitude": longitude, "latitude":latitude, "utc_time":utc_time, }})

def creat_file(list):
	now=datetime.now()
	file_name=f"/home/sandeep/GIT/Logs/{now.year}-{now.month}-{now.day}--{now.hour}-{now.minute}-{now.second}.csv"
	file= open(file_name, 'a+', newline='', encoding='utf-8')
	header = [ 'Longitude', 'Latitude', "UTC-Time", 'No of satellites']
	with file:
		write=csv.writer(file)
		write.writerow(header)
		write.writerows(list)


def parse_gpgga(data):
	no_of_sat=data[7]
	return {"gpgga":{"longitude":None, "latitude":None, "utc_time":None,"no_of_sat":no_of_sat}}


def parse_gps_nmea(nmea_string):
	if  "$GPRMC" in nmea_string:
		result = parse_gprmc(nmea_string) 
#		print(result)
	elif "$GPGGA" in nmea_string:
		result = parse_gpgga(nmea_string) 
	else:
		return {}
#	print(result)
	return result

if __name__ == "__main__":
        # setup serial connection
	gps=serial.Serial("/dev/ttyACM0",baudrate=9600)
	ser_bytes=gps.readline()
	list =[]
        # gps global state
	latitude = 0.0
	longitude = 0.0
	utc_time = 0
	no_of_sat = 0
	start=end=0
	start1=perf_counter()
#	valid_fix = False
	while True:
#		start1=timeit.timeit()
		ser_bytes=gps.readline()
		decoded_bytes=ser_bytes.decode("utf-8")
		raw_gps_string=decoded_bytes.split(",")
		result=parse_gps_nmea(raw_gps_string)
#		print(result)
		if "gprmc" in result.keys():
			start = timeit.timeit()
			longitude=result["gprmc"]['longitude']
			latitude=result["gprmc"]['latitude']
			utc_time=result["gprmc"]['utc_time']
		elif "gpgga" in result.keys():
			no_of_sat=result["gpgga"]['no_of_sat']
		else:
			end = timeit.timeit()
			if (end-start >= 2):
				no_of_sat=0
				longitude=0.0
				latitude=0.0
				utc_time=0
		list1=[longitude, latitude, utc_time, no_of_sat]
		list.append(list1)
		start2=perf_counter()
		if (start2-start1 >= 60):
			creat_file(list)
			list =[]
			start1= start2
