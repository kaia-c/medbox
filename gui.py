#!/usr/bin/python
# A gui app for a medical dispensation unit
# By: Us
# Each screen is a class by itself
# along with the class that tracks the number of drugs in the unit

from Tkinter import *
import Tkinter as tk
#import mysql.connector

# the first screen of the gui
class Gui:
	def __init__(self, master):
		self.master = master
		self.initialize()
	def initialize(self):
		# puts the parent widget on a grid. basically centers all of the buttons
		self.master.grid()
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		# sets the frame on the grid. trying to get bigger buttons...
		self.frame = tk.Frame(self.master)
		self.frame.grid(row=0, column=0)
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=1)
		self.frame.rowconfigure(0, weight=2)
		self.frame.rowconfigure(1, weight=1)
		# declaration and configuring widgets
		btnAddDrugs = tk.Button(self.frame, text='Add Drugs to Box', command=self.addDrugs)
		btnAddDrugs.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnTakeDrugs = tk.Button(self.frame, text='Take Drugs from Box', command=self.takeDrugs)
		btnTakeDrugs.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnQuit = tk.Button(self.frame, text="Quit", command=self.quit)
		btnQuit.configure(height=2, wraplength=2, font='Arial 20 bold')
		# setting the widgets on the grid
		btnAddDrugs.grid(row=0, column=0, sticky='NSEW')
		btnTakeDrugs.grid(row=0, column=1, sticky='NSEW')
		btnQuit.grid(row=1, column=0, columnspan=2, rowspan=2, sticky='NSEW')
	def addDrugs(self):
		# opens a new window for adding drugs
		self.newWindow = tk.Toplevel(self.master)
		self.newWindow.overrideredirect(True)
		self.newWindow.geometry('%dx%d+0+0' % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
		self.app = AddDrugs(self.newWindow)
	def takeDrugs(self):
		# opens a new window for withdrawing drugs
		self.newWindow = tk.Toplevel(self.master)
		self.newWindow.overrideredirect(True)
		self.newWindow.geometry('%dx%d+0+0' % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
		self.app = TakeDrugs(self.newWindow)
	def quit(self):
		self.master.destroy()

# one potential second screen for adding drugs to the collection
class AddDrugs:
	def __init__(self, master):
		self.master = master
		self.initialize()
	def initialize(self):
		# puts the parent widget on a grid. basically centers all of the buttons
		self.master.grid()
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		self.frame = tk.Frame(self.master)
		self.frame.grid()
		# declaration and configuring widgets
		btnAdd1 = tk.Button(self.frame, text=dc.returnKey(0), command=lambda: self.add(dc.returnKey(0)))
		btnAdd1.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnAdd2 = tk.Button(self.frame, text=dc.returnKey(1), command=lambda: self.add(dc.returnKey(1)))
		btnAdd2.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnAdd3 = tk.Button(self.frame, text=dc.returnKey(2), command=lambda: self.add(dc.returnKey(2)))
		btnAdd3.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnAdd4 = tk.Button(self.frame, text=dc.returnKey(3), command=lambda: self.add(dc.returnKey(3)))
		btnAdd4.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnQuit = tk.Button(self.frame, text="Done", command=self.quit)
		btnQuit.configure(height=2, wraplength=2, font='Arial 20 bold')
		# setting the widgets on the grid
		btnAdd1.grid(row=0, column=0)
		btnAdd2.grid(row=0, column=1)
		btnAdd3.grid(row=1, column=0)
		btnAdd4.grid(row=1, column=1)
		btnQuit.grid(row=2, column=0, columnspan=2, sticky='NSEW')
	def add(self, drug):
		# opens new window to choose the amount of drugs to be added
		self.newWindow = tk.Toplevel(self.master)
		self.newWindow.overrideredirect(True)
		self.newWindow.geometry('%dx%d+0+0' % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
		self.app = AddDrugsAmount(self.newWindow, drug)
	def quit(self):
		dc.printAmounts()
		self.master.destroy()

# one potential second screen for taking drugs from the collection
class TakeDrugs:
	def __init__(self, master):
		self.master = master
		self.initialize()
	def initialize(self):
		# puts the parent widget on a grid. basically centers all of the buttons
		self.master.grid()
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		self.frame = tk.Frame(self.master)
		self.frame.grid()
		# declaration and configuring widgets
		btnTake1 = tk.Button(self.frame, text=dc.returnKey(0), command=lambda: self.take(dc.returnKey(0)))
		btnTake1.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnTake2 = tk.Button(self.frame, text=dc.returnKey(1), command=lambda: self.take(dc.returnKey(1)))
		btnTake2.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnTake3 = tk.Button(self.frame, text=dc.returnKey(2), command=lambda: self.take(dc.returnKey(2)))
		btnTake3.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnTake4 = tk.Button(self.frame, text=dc.returnKey(3), command=lambda: self.take(dc.returnKey(3)))
		btnTake4.configure(height=4, width=25, wraplength=4, font='Arial 20 bold')
		btnQuit = tk.Button(self.frame, text="Done", command=self.quit)
		btnQuit.configure(height=2, wraplength=2, font='Arial 20 bold')
		# setting the widgets on the grid
		btnTake1.grid(row=0, column=0)
		btnTake2.grid(row=0, column=1)
		btnTake3.grid(row=1, column=0)
		btnTake4.grid(row=1, column=1)
		btnQuit.grid(row=2, column=0, columnspan=2, sticky='NSEW')
	def take(self, drug):
		# opens new window to choose amount to drugs to be taken
		self.newWindow = tk.Toplevel(self.master)
		self.newWindow.overrideredirect(True)
		self.newWindow.geometry('%dx%d+0+0' % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
		self.app = TakeDrugsAmount(self.newWindow, drug)
	def quit(self):
		dc.printAmounts()
		self.master.destroy()

# a class for choosing the amount of drugs to be taken
class TakeDrugsAmount:
	def __init__(self, master, drug):
		self.master = master
		# declares amount var and the StringVar that will fill label
		self.amount = 1
		self.var = StringVar()
		self.var.set(str(self.amount))
		self.initialize(drug)
	def initialize(self, drug):
		# puts the parent widget on a grid. basically centers all of the buttons
		self.master.grid()
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		self.frame = tk.Frame(self.master)
		self.frame.grid()
		# declaration and configuring widgets
		# quick choices
		btnQuick1 = tk.Button(self.frame, text='Take 1', command=lambda: self.take(drug, self.amount))
		btnQuick1.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick2 = tk.Button(self.frame, text='Take 2', command=lambda: self.take(drug, self.amount))
		btnQuick2.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick3 = tk.Button(self.frame, text='Take 3', command=lambda: self.take(drug, self.amount))
		btnQuick3.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick4 = tk.Button(self.frame, text='Take 4', command=lambda: self.take(drug, self.amount))
		btnQuick4.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		# spinner for different amounts
		lblAmt = tk.Label(self.frame, textvariable=self.var)
		lblAmt.configure(height=2, width=10, font='Arial 20 bold')
		btnIncrease = tk.Button(self.frame, text='Up', command=self.increase)
		btnIncrease.configure(height=2, width=10, wraplength=2, font='Arial 20 bold')
		btnDecrease = tk.Button(self.frame, text='Down', command=self.decrease)
		btnDecrease.configure(height=2, width=10, wraplength=2, font='Arial 20 bold')
		btnAccept = tk.Button(self.frame, text='Submit', command=lambda: self.take(drug, self.amount))
		btnAccept.configure(height=3, width=25, wraplength=3, font='Arial 20 bold')
		btnCancel = tk.Button(self.frame, text='Cancel', command=self.cancel)
		btnCancel.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		# setting the widgets on the grid
		btnQuick1.grid(row=0, column=0, rowspan=3, columnspan=2)
		btnQuick2.grid(row=0, column=2, rowspan=3, columnspan=2)
		btnQuick3.grid(row=3, column=0, rowspan=3, columnspan=2)
		btnQuick4.grid(row=3, column=2, rowspan=3, columnspan=2)
		lblAmt.grid(row=0, column=4, rowspan=2)
		btnIncrease.grid(row=2, column=4, rowspan=2)
		btnDecrease.grid(row=4, column=4, rowspan=2)
		btnAccept.grid(row=6, column=0, rowspan=3, columnspan=3)
		btnCancel.grid(row=6, column=3, rowspan=3, columnspan=2)
	def take(self, drug, amount):
		dc.take(drug, amount)
		self.master.destroy()
	def cancel(self):
		self.master.destroy()
	# definitions to operate spinner
	def increase(self):
		if self.amount == 10:
			self.amount = 0
		else:
			self.amount += 1
		self.var.set(str(self.amount))
	def decrease(self):
		if self.amount == 1:
			self.amount = 10
		else:
			self.amount -= 1
		self.var.set(str(self.amount))

# a class for choosing the amount of drugs to add.
class AddDrugsAmount:
	def __init__(self, master, drug):
		self.master = master
		# declares amount var and StringVar that will fill label
		self.amount = 1
		self.var = StringVar()
		self.var.set(str(self.amount))
		self.initialize(drug)
	def initialize(self, drug):
		# puts the parent widget on a grid. basically centers all of the buttons
		self.master.grid()
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		self.frame = tk.Frame(self.master)
		self.frame.grid()
		# declaration and configuring widgets
		# quick choices
		btnQuick1 = tk.Button(self.frame, text='Add 1', command=lambda: self.add(drug, self.amount))
		btnQuick1.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick2 = tk.Button(self.frame, text='Add 2', command=lambda: self.add(drug, self.amount))
		btnQuick2.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick3 = tk.Button(self.frame, text='Add 3', command=lambda: self.add(drug, self.amount))
		btnQuick3.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		btnQuick4 = tk.Button(self.frame, text='Add 4', command=lambda: self.add(drug, self.amount))
		btnQuick4.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		# spinner for different amounts
		lblAmt = tk.Label(self.frame, textvariable=self.var)
		lblAmt.configure(height=2, width=10, font='Arial 20 bold')
		btnIncrease = tk.Button(self.frame, text='Up', command=self.increase)
		btnIncrease.configure(height=2, width=10, wraplength=2, font='Arial 20 bold')
		btnDecrease = tk.Button(self.frame, text='Down', command=self.decrease)
		btnDecrease.configure(height=2, width=10, wraplength=2, font='Arial 20 bold')
		btnAccept = tk.Button(self.frame, text='Submit', command=lambda: self.add(drug, self.amount))
		btnAccept.configure(height=3, width=30, wraplength=3, font='Arial 20 bold')
		btnCancel = tk.Button(self.frame, text='Cancel', command=self.cancel)
		btnCancel.configure(height=3, width=20, wraplength=3, font='Arial 20 bold')
		# setting the widgets on the grid
		btnQuick1.grid(row=0, column=0, rowspan=3, columnspan=2)
		btnQuick2.grid(row=0, column=2, rowspan=3, columnspan=2)
		btnQuick3.grid(row=3, column=0, rowspan=3, columnspan=2)
		btnQuick4.grid(row=3, column=2, rowspan=3, columnspan=2)
		lblAmt.grid(row=0, column=4, rowspan=2)
		btnIncrease.grid(row=2, column=4, rowspan=2)
		btnDecrease.grid(row=4, column=4, rowspan=2)
		btnAccept.grid(row=6, column=0, rowspan=3, columnspan=3)
		btnCancel.grid(row=6, column=3, rowspan=3, columnspan=2)
	def add(self, drug, amount):
		dc.add(drug, amount)
		self.master.destroy()
	def cancel(self):
		self.master.destroy()
	# definitions to operate spinner
	def increase(self):
		if self.amount == 10:
			self.amount = 1
		else:
			self.amount += 1
		self.var.set(str(self.amount))
	def decrease(self):
		if self.amount == 1:
			self.amount = 10
		else:
			self.amount -= 1
		self.var.set(str(self.amount))

# a collection to stored and manipulate the amount of drugs
# most likely will be changed to operate on sql queries
class DrugsCollection:
	def __init__(self):
		# rough-draft of sql code
		# self.drugs = {}
		# con = mysql.connector.connect(user='gui', password='raspberry', host='127.0.0.1', database='medicine')
		# cursor = con.cursor()
		# query = ("SELECT MEDS.Name, SUM(MEDS_has_BOX.Amount) "
		#		   "FROM MEDS "
		#		   "JOIN MEDS_has_BOX ON MEDS.MedID = MEDS_has_BOX.MedID "
		#		   "GROUP BY Meds.Name")
		# cursor.execute(query)
		# for (Meds.Name, SUM(MEDS_has_BOX.Amount)) in cursor:
		#	self.drugs.append(Meds.Name: int(SUM(MEDS_has_BOX.Amount)))
		# cursor.close()
		# con.close()
		self.drugs = {'vicodin': 0, 'percoset': 0, 'robetussin': 0, 'lithium': 0}
	def add(self, drug, amt):
		self.drugs[drug] = self.drugs[drug] + int(amt)
	def take(self, drug, amt):
		self.drugs[drug] = self.drugs[drug] - int(amt)
	def printAmounts(self):
		for keys, values in self.drugs.items():
			print(keys)
			print(values)
	def returnKey(self, pos):
		keys = self.drugs.keys()
		return keys[int(pos)]

# the main loop for the gui
def main():
	root = tk.Tk()
	root.overrideredirect(True)
	root.geometry('%dx%d+0+0' % (root.winfo_screenwidth(), root.winfo_screenheight()))
	root.title('Medical Dispensation')
	app = Gui(root)
	root.mainloop()

dc = DrugsCollection()

if __name__ == '__main__':
	main()