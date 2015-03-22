'''
When you export data in Vistrian, often times there will be many gaps in the data, and the gaps are
not consistent between the columns.  This python code prompts the user for a data file to fix, then interpolates 
the data so that there are no more gaps in any columns.  It then saves the file with an appended ' - fixed' at the end."
'''


import numpy as np
import pylab as plt
from Tkinter import Tk
import Tkinter,tkFileDialog,csv,datetime

def vistrian_dates_to_epoch(dates):
	"Converts input dates from vistrian (in string format) to time since epoch in seconds."
	"Time is sorted before returning."
	totaltimes=[]
	for each in dates:
		each=str(each)
		
		#sometimes vistrian outputs the datetime in different formats, which is why the try/except block is here
		try:
			temptime=datetime.datetime.strptime(each,'%m/%d/%Y %I:%M:%S %p')
		except ValueError:
			temptime=datetime.datetime.strptime(each,'%m/%d/%Y %H:%M')
			
		totaltimes.append((temptime-datetime.datetime(1970,1,1)).total_seconds())
	totaltimes=sorted(totaltimes)
	return totaltimes
	
def epoch_to_vistrian_dates(dates):
	"Converts seconds since epoch to dates in vistrian format."
	for count in len(range(dates)):
		dates[count]=time.strftime('%m/%d/%Y %I:%M:%S %p', time.gmtime(dates[count]))
	return dates
	
def fix_vistrian_data(files):
	"Takes one or more input files, which is/are downloaded vistrian data.  Interpolates the data so that at each timestamp there "
	"is data in each column."
	
	for file in files:
		raw_data=[]
		rowcounter=0
		#import data from csv file to raw_data as list
		with open(file, 'rb') as csvfile:
			filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in filereader:
				# store the data not in the first row
				if rowcounter!=0:
					raw_data.append(row)
				# if it is the first row, use those values as labels in the dictionary for storing the data
				if rowcounter==0:
					rowLabels=row
					rowcounter+=1
		
		report_data={}
		#may need to change the 'TimeStamp' key if your specific vistrian implementation uses a different column title
		report_data['TimeStamp']=[]
		
		#populate timestamp array
		for row in raw_data: 
			report_data[rowLabels[0]].append(row[0])
		allDTs=vistrian_dates_to_epoch(report_data['TimeStamp'])
		
		for columnCount in range(len(rowLabels)):
			if rowLabels[columnCount]!='TimeStamp':
				report_data[rowLabels[columnCount]]=[]
				timeCounter=0
				tempDataArray=[]
				tempTimeArray=[]
				for dataRow in raw_data:
					if dataRow[columnCount]: #ensure there is data at this particular column and row in the imported data, add data and time to temp arrays if so
						tempDataArray.append(dataRow[columnCount])
						tempTimeArray.append(allDTs[timeCounter])
					timeCounter+=1
				tempDataArray=np.array(tempDataArray,dtype='float64') #you may need to alter this if all your data is not numbers
				#tempDataArray=tempDataArray.astype(np.float)
				#interpolate data so there is data at each timestamp in the file
				report_data[rowLabels[columnCount]]=np.interp(allDTs,tempTimeArray,tempDataArray)
				
		file=file.rstrip('.csv')
		file=file+' - fixed.csv'
		with open(file, 'wb') as csvfile:
			spamwriter = csv.writer(csvfile, delimiter=',')
			#writes data with seconds since the epoch instead of vistrian dateTimes
			columnsToWrite = sorted(report_data.keys())#sorts dictionary keys alphabetically
			spamwriter.writerow(['seconds since epoch']+columnsToWrite) 
			for each in range(len(report_data['TimeStamp'])):
				writedata=[]
				writedata.append(allDTs[each])
				for key in columnsToWrite:
					writedata.append(report_data[key][each])
				spamwriter.writerow(writedata)
	return

	
def choose_files():
	root = Tkinter.Tk()
	root.withdraw() #hides Tkinter base window
	files = tkFileDialog.askopenfilenames(parent=root,title='Choose file(s)') #allows choosing multiple files
	files = root.tk.splitlist(files) #returns a string of files, so the string has to be split
	fix_vistrian_data(files)

if __name__=='__main__':
	choose_files()