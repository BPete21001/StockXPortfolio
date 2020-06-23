#
#STOCKX PORTFOLIO TRACKER
#
#Written By: Benjamin Petersen
#
#Date of last edit: 6/23/20
#
#This program serves as a graphical user interface powered by tkinter 
#that allows a user to keep track of certain items and track their prices on StockX
#through HTML scraping powered by selenium chromedriver
#
import tkinter as tk
from tkinter import *
from tkinter import ttk
from selenium import webdriver
import os
import traceback
import threading
from threading import Thread

#Declares class "Item" to help store and access information about
#portfolio items
class Item:
	
	def __init__(self, price, url, size, name):
		self.price = price
		self.url = url
		self.size = size
		self.name = name

	def __str__(self):
		return "Price = " + str(self.price) + " URL = " + str(self.url) + " Size = " + str(self.size) + " Name = " + str(self.name) 


#Function that creates a new thread and then runs the HTML scraping 
#function. This allows the gui to remain active while the stockX HTML
#is being scraped in the background
def updateThread(userInfo, updatingMark, needsUpdateMark, updateNumber):
		
	def updateItems(userInfo, updatingMark, needsUpdateMark, updateNumber):
	
		count = 0
		updatingMark[0] = True

		#create browser and hide off screen
		driver = webdriver.Chrome()
		driver.set_window_position(-1000, -1000)
		driverHidden = True
		items = loadItems(userInfo)
		for item in items:
			updateNumber[0] += 1
			oneSize = False
			#attempt to access URL
			try:
				driver.get(item.url)
			except:
				print("Invalid URL")
				traceback.print_exc()
				item.price = "Error"
				break
				#filter faulty URLs
			if(("404" in driver.current_url) or not("stockx.com" in driver.current_url)):
				print("Invalid URL")
				driver.quit()
				item.price = "Error"
				continue
			#display window if captcha 
			if("denied" in driver.title):
				driver.set_window_position(0,0)
				driverHidden = False

			#wait until captcha is solved
			while("denied" in driver.title):
				time.sleep(1)
				#filter faulty URLs
			if(("404" in driver.current_url) or not("stockx.com" in driver.current_url)):
				print("Invalid URL")
				item.price = "Error"
				continue

				#hide window again
			if(not driverHidden):
				driver.set_window_position(-1000, -1000)
				driverHidden = True

				#initialize size and price arrays
			size = [None]
			cost = [None]

			#if the item has no size options, return only price
			if(item.size == "OneSize"):
				elementC = driver.find_element_by_xpath('//*[@id="market-summary"]/div[2]/div[1]/a/div[1]/div')
				price = str(elementC.get_attribute('innerHTML')).strip('$')
				print(price)
				item.price = price
				oneSize = True


			if(not oneSize):
				#get sizes and prices and add to arrays
				try:
					for i in range(2,28):                        
						elementS = driver.find_element_by_xpath('//*[@id="mobile-header"]/div/div[1]/div/div/div[2]/div[2]/ul/li['+str(i)+ ']/div/div[1]')
						size.append(elementS.get_attribute('innerHTML'))
						elementC=driver.find_element_by_xpath('//*[@id="mobile-header"]/div/div[1]/div/div/div[2]/div[2]/ul/li['+str(i)+']/div/div[2]')
						cost.append(elementC.get_attribute('innerHTML'))
				except:
					print("end search")

		
				if(len(size) >= 2):
					#format size and cost arrays
					for i in range(0, len(size)):
						size[i] = str(size[i]).strip(" ")
						cost[i] = str(cost[i]).strip("$")
					size.pop(0)
					cost.pop(0)

					
					#search for given size and return appropriate cost
					for i in range(0, len(size)):
						if(item.size == size[i]):
							item.price = cost[i]
							break
						item.price = "None"	
				else:
					item.price = "None"
			updateFileItems(userInfo, items)
			
		driver.quit()
		updatingMark[0] = False 
		needsUpdateMark[0] = True

	t = threading.Thread(target = updateItems, kwargs=dict(userInfo = userInfo, updatingMark = updatingMark, needsUpdateMark = needsUpdateMark, updateNumber = updateNumber))
	t.start()

#Replaces spaces in a string with underscores
def toUnderscores(word):
	return word.replace(" ", "_")

#Replaces underscores in a string with spaces
def toSpaces(word):
	return word.replace("_", " ")

#Taken a list of items and creates a list of their
#names and sizes for better readability
def createNamedList(items):
	namedItems = [None]
	for item in items:
		namedItems.append(item.name + " Size: " + item.size)
	namedItems.pop(0)
	return namedItems

#Function that spawns and executes when the "Remove Item" button
#on the main portfolio method is pressed
def removeWindow(userInfo, namedItems, items, needsUpdateMark):
	
	#create and place static window widgets
	grey = "#%02x%02x%02x" % (140, 140, 140)
	window = Toplevel()
	window.title("Remove Item")
	window.geometry("400x240")
	window.configure(bg = grey)
	removeLabel = Label(window, text = "Select Item",  font = "candara 14", bg = grey)
	
	#declare varable that reads from dropdown list 
	tkvar = StringVar(window)

	#create and place combobox and label
	removeOptions = ttk.Combobox(window, textvariable = tkvar, state = 'readonly', values = namedItems, width = 30)
	removeLabel.place(relx = .5, rely = .285, anchor = CENTER)
	removeOptions.place(relx = .5, rely = .5, anchor = CENTER)
	

	#declare variable that tells the "x" button in the top bar to not end the program
	end = [False]


	#method to remove selected item from active item list and save file
	def remove():
		count = -1
		for item in namedItems:
			count += 1
			if(str(tkvar.get()) == item):
				items.pop(count)
				updateFileItems(userInfo, items)
				needsUpdateMark[0] = True
				window.destroy()

	#declare and place button
	addButton = Button(window, text = "Remove", command= remove, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	addButton.place(relx = .5, rely = .815, anchor = CENTER)

	
	#add custom top bar and frame to window
	addTopBar(window, 2, False)
	addBorder(window)
	
	#place window in the center of the screen
	center(window)
	
	#force focus only on the popup
	window.grab_set()
	
	#display window
	window.mainloop()

#Function that spawns and executes when the "Edit Item" button
#on the main portfolio method is pressed
def editWindow(userInfo, namedItems, items, count, needsUpdateMark):
	
	#declare and place static widgets on top window
	grey = "#%02x%02x%02x" % (140, 140, 140)
	window = Toplevel()
	window.title("Select Item")
	window.geometry("400x240")
	window.configure(bg = grey)
	selectLabel = Label(window, text = "Select Item",  font = "candara 14", bg = grey)
	
	#declare varable that stores the dropdown information from combobox
	tkvar = StringVar(window)

	#create combobox and label
	selectOptions = ttk.Combobox(window, textvariable = tkvar, state = 'readonly', values = namedItems, width = 30)
	selectLabel.place(relx = .5, rely = .285, anchor = CENTER)
	selectOptions.place(relx = .5, rely = .5, anchor = CENTER)

	#declare variable that tells the "x" button not to end the program
	end = [False]


	#method that returns the index of the selected item in the items list 
	#then calls a new method to show an edit options window
	def edit():
		for item in namedItems:
			count[0] += 1
			if(str(tkvar.get()) == item):
				window.destroy()
				editWindow2(userInfo, count, items, needsUpdateMark)




	#declare and palce the "edit" button
	editButton = Button(window, text = "Edit", command= edit, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	editButton.place(relx = .5, rely = .815, anchor = CENTER)

	
	#adds custom top bar to window
	addTopBar(window, 2, False)
	
	#centers the window in the middle of the user's screen
	center(window)
	
	#adds a border to the window
	addBorder(window)
	
	#forces focus on to the main window
	window.grab_set()
	
	#displays window
	window.mainloop()

#Function that only spawns from within the editWindow substance
#that displays options to edit an item
def editWindow2(userInfo, count, items, needsUpdateMark):
	#declares variable to specify if closing the window ends the program
	end = [False]

	#declare and place static widgets
	grey = "#%02x%02x%02x" % (140, 140, 140)
	window = Toplevel()
	window.title("Edit Item")
	window.geometry("400x240")
	window.configure(bg = grey)
	Sizes = ["OneSize", "4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5",
	"10", "10.5", "11", "11.5", "12", "12.5", "13", "13.5", "14", "15", "16", "17", 
	"XS", "S", "M", "L", "XL", "3.5Y", "4Y", "4.5Y","5Y","5.5Y","6Y","6.5Y","7Y", 
	"2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "10.5C"]
	
	#declare a variable to read from combobox and set default value to current value
	#held by item
	tkvar = StringVar(window)
	tkvar.set(items[count[0]].size)
	
	#more static widgets
	nameLabel = Label(window, text = "Item Name",  font = "candara 14", bg = grey)
	urlLabel = Label(window, text = "StockX URL",  font = "candara 14", bg = grey)
	sizeLabel = Label(window, text = "Size",  font = "candara 14", bg = grey)
	nameEntry = Entry(window, width = 20)
	urlEntry = Entry(window, width = 20)
	sizeOptions = ttk.Combobox(window, textvariable = tkvar, state = 'readonly', values = Sizes, width = 10)
	nameLabel.place(relx = .35, rely = .225, anchor = CENTER)
	nameEntry.place(relx = .65, rely = .225, anchor = CENTER)
	urlLabel.place(relx = .35, rely = .4, anchor = CENTER)
	urlEntry.place(relx = .65, rely = .4, anchor = CENTER)
	sizeLabel.place(relx = .35, rely = .575, anchor = CENTER)
	sizeOptions.place(relx = .65, rely = .575, anchor = CENTER)
	
	#set default values on name and url entry fields to current value of item
	nameEntry.insert(END, items[count[0]].name)
	urlEntry.insert(END, items[count[0]].url)

	#method to update both the items list and items file with new information given
	def edit():
		if( ("stockx.com" in urlEntry.get()) and str(tkvar.get()) and nameEntry.get()):
			item = Item(None, urlEntry.get(), str(tkvar.get()), nameEntry.get())
			items[count[0]].size = str(tkvar.get())
			items[count[0]].url = str(urlEntry.get())
			items[count[0]].name = str(nameEntry.get())
			updateFileItems(userInfo, items)
			needsUpdateMark[0] = True
			window.destroy()
			
		else:
			addButton.config(text = "Invalid")

	#declare and place edit button
	editButton = Button(window, text = "Edit", command= edit, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	editButton.place(relx = .5, rely = .815, anchor = CENTER)

	
	#add a custom top bar to the window
	addTopBar(window, 2, False)
	
	#center the window in the middle of the screen
	center(window)
	
	#add a border to the window
	addBorder(window)
	
	#force focus on only the pop-up window
	window.grab_set()
	
	#display window
	window.mainloop()

#function to save a new item into the user's item file, or create a user's item file
#if there wasn't one, and add the item
def storeItem(userInfo, item):
	userName = str(userInfo[0]).strip()
	userItemFile = open( userName + "Items.txt", "a+")
	if(not (os.stat(userName + "Items.txt").st_size == 0)):
		userItemFile.write("\n")
	userItemFile.write(str(item.price) + " " + str(item.url) + " " + str(item.size) + " "+ toUnderscores(str(item.name)))

#function that displays the "updating" text onto the canvas once the update thread
#has launched and updates the user of the thread's progress
def updateToCanvas(canvas, updateNumber, length, count):
	canvas.delete('update')
	dots = ['.'] * (int(count/4)%4)
	if(updateNumber[0] == 0):
		canvas.create_text(150, 225, text = "Updating Item 1 of " + str(length) + str(" ".join(dots)), font = "candara 30 bold", anchor = "w", tag = 'update')
	else:
		canvas.create_text(150, 225, text = "Updating Item " + str(updateNumber[0]) + " of " + str(length)+ str(" ".join(dots)), font = "candara 30 bold", anchor = "w", tag = 'update')

#binds the invisible root object to the visible window, this is done to give the window a 
#taskbar presence
def bindRoot(root, window):
	def onRootIconify(event): window.withdraw()
	root.bind("<Unmap>", onRootIconify)
	def onRootDeiconify(event): window.deiconify()
	root.bind("<Map>", onRootDeiconify)

#saves contents of current "items" list to the user's items file
def updateFileItems(userInfo, items):
	userName = str(userInfo[0]).strip()
	count = 0
	#clears old item's file to send full updated contents from current list
	open( userName + "Items.txt", "w").close()

	userItemFile = open( userName + "Items.txt", "a+")
	
	for item in items:
		count += 1
		userItemFile.write(str(item.price) + " " + str(item.url) + " " + str(item.size) + " "+ toUnderscores(str(item.name)))
		if( not (count == len(items))):
			userItemFile.write("\n")

#centers the given window into the middle of the screen
def center(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

#takes a list of items and prints them to the active canvas
def itemsToCanvas(canvas, items):
	count = 0
	#deletes text from updateToCanvas 
	canvas.delete('update')
	for i in items :
		count += 1
		y = 12 + 25*count
		canvas.create_text(32, y, text = i.name, font = "candara 12 bold", anchor = "w", tag = 'update')
		canvas.create_text(625, y, text = i.price, font = "candara 12 bold", tag = 'update')
		canvas.create_text(475, y, text = i.size, font = "candara 12 bold", tag = 'update')

#draws a 2 pixel wide black border around full length of frame
def addBorder(window):
	borderLeftSide = Frame(window, width = 2, height = 1000, bg = 'black')
	borderLeftSide.place(x=0, y=25, anchor = 'nw')
	borderRightSide = Frame(window, width = 2, height = 1000, bg = 'black')
	borderRightSide.place(relx=1, y=25, anchor = 'ne')
	borderBottom = Frame(window, width = 1000, height = 2, bg = 'black')
	borderBottom.place(x=0, rely=1, anchor = 'sw')

#reads info from user's info file and returns it as a list of object "item"
def loadItems(userInfo):
	userName = str(userInfo[0]).strip()
	file = open( userName + "Items.txt", "r")
	items = []
	for line in file:
		words = line.split()
		words[3] = toSpaces(words[3])
		items.append(Item(words[0], words[1], words[2], words[3]))
	
	return items

#gets rid of the gross looking auto generated top bar generated by windows
#and adds one that includes an "x" button and the window title. Also enables the option
#to drag the window by its top bar
def addTopBar(window, size, end):
	grey = "#%02x%02x%02x" % (140, 140, 140)

	def SaveLastClickPos(event):
		lastClick[0] = event.x
		lastClick[1] = event.y

	def Dragging(event):
		x, y = event.x - lastClick[0] + window.winfo_x(), event.y - lastClick[1] + window.winfo_y()
		if(lastClick[1] <= 25 and lastClick[1] >= 0):
			window.geometry("+%s+%s" % (x , y))

	def close():
		if(end):
			os._exit(1)
		else:
			window.destroy()

	window.overrideredirect(True)
	window.bind('<Button-1>', SaveLastClickPos)
	window.bind('<B1-Motion>', Dragging)
	lastClick = [0,0]
	frame = Frame(window, width=window.winfo_reqwidth()*size, height=25, bg="black")
	frame.place(x = 0, y = 0, anchor = 'nw')
	title = Label(frame, text = window.title(),  font = "candara 12 bold", bg = 'black', fg = grey)
	title.place(x = 2, y = 12, anchor = 'w')
	exitButton =Button(frame, text = " X ", command=close,borderwidth = 1, 
		relief = "solid", font = "candara 14 bold", bg = 'black', fg = grey, 
		activeforeground = 'black', activebackground = 'red')
	
	exitButton.place(relx = 1, y = 12, anchor = 'e')

#spawns the pop up window that prompts the user to add an item to their portfolio
def addWindow(userInfo, items, needsUpdateMark):
	#Declares variable that determines if closing the window ends the program
	end = [False]
	
	#Declare windpw and static widgets
	grey = "#%02x%02x%02x" % (140, 140, 140)
	window = Toplevel()
	window.title("Add Item")
	window.geometry("400x240")
	window.configure(bg = grey)
	Sizes = ["OneSize", "4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5",
	"10", "10.5", "11", "11.5", "12", "12.5", "13", "13.5", "14", "15", "16", "17", 
	"XS", "S", "M", "L", "XL", "3.5Y", "4Y", "4.5Y","5Y","5.5Y","6Y","6.5Y","7Y", 
	"2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "10.5C"]
	
	#declare variable that reads from combobox
	tkvar = StringVar(window)
	
	#more static widget declaratino
	nameLabel = Label(window, text = "Item Name",  font = "candara 14", bg = grey)
	urlLabel = Label(window, text = "StockX URL",  font = "candara 14", bg = grey)
	sizeLabel = Label(window, text = "Size",  font = "candara 14", bg = grey)
	nameEntry = Entry(window, width = 20)
	urlEntry = Entry(window, width = 20)
	sizeOptions = ttk.Combobox(window, textvariable = tkvar, state = 'readonly', values = Sizes, width = 10)
	nameLabel.place(relx = .35, rely = .225, anchor = CENTER)
	nameEntry.place(relx = .65, rely = .225, anchor = CENTER)
	urlLabel.place(relx = .35, rely = .4, anchor = CENTER)
	urlEntry.place(relx = .65, rely = .4, anchor = CENTER)
	sizeLabel.place(relx = .35, rely = .575, anchor = CENTER)
	sizeOptions.place(relx = .65, rely = .575, anchor = CENTER)

	#function that adds an item to the items list if requirements are met
	def add():
		if( ("stockx.com" in urlEntry.get()) and str(tkvar.get()) and nameEntry.get()):
			item = Item(None, urlEntry.get(), str(tkvar.get()), nameEntry.get())
			storeItem(userInfo, item)
			needsUpdateMark[0] = True
			window.destroy()
			
		else:
			addButton.config( text = "Invalid")


	#declare and place the add button
	addButton = Button(window, text = "Add", command= add, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	addButton.place(relx = .5, rely = .815, anchor = CENTER)

	

	#add a custom top bar to the window
	addTopBar(window, 2, False)
	
	#center the window in the middle of the screen
	center(window)
	
	#add a border to the window
	addBorder(window)
	
	#force focus on only the pop-up window
	window.grab_set()
	
	#display window
	window.mainloop()

#function to check if a file contains a particular string	
def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        
        for line in read_obj:
            
            if string_to_search in line:
                return True
    return False

#reads a line of a file as a string at a given line number
def getFileLine(fileName, lineNumber):
	f =open(fileName)
	lines = f.readlines()
	return lines[lineNumber]

#returns the line number of a given string in a file
def find_keyword_line(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        num = -1
        for line in read_obj:
            num += 1
            if string_to_search in line:
                return num
    return -1

#spawns and executes the window that prompts a user for their login information
def loginWindow(userInfo, usernameFileName, passwordFileName):
	
	#declare window and static variables
	grey = "#%02x%02x%02x" % (140, 140, 140)
	root = Tk()
	root.attributes('-alpha', 0.0)
	window = Toplevel(root)
	window.title("Portfolio Login")
	window.geometry("400x240")
	window.configure(bg = grey)
	userLabel = Label(window, text = "Username",  font = "candara 14", bg = grey)
	passLabel = Label(window, text = "Password",  font = "candara 14", bg = grey)
	outputLabel = Label(window, text = "User Login",  font = "candara 20", bg = grey)
	userEntry = Entry(window, width = 20)
	passEntry = Entry(window, width = 20)
	userLabel.place(relx = .35, rely = .475, anchor = CENTER)
	userEntry.place(relx = .65, rely = .475, anchor = CENTER)
	passLabel.place(relx = .35, rely = .625, anchor = CENTER)
	passEntry.place(relx = .65, rely = .625, anchor = CENTER)
	outputLabel.place(relx = .5, rely = .275, anchor = CENTER)

	#verifies that the given username exists in the users file and matches 
	#the password at the same line in the passwords file
	def login():
		userInfo[0] = " " + userEntry.get() + " "
		userInfo[1] = " " + passEntry.get() + " "
		userValid = True
		passValid = True
		
		userLine = find_keyword_line(usernameFileName, userInfo[0])
		
		expectedPass = getFileLine(passwordFileName, userLine).strip()
		userPass = userInfo[1].strip()
		
		if(not check_if_string_in_file(usernameFileName, userInfo[0])):
			outputLabel.configure(text = "User not found")
			userValid = False
		elif( not (userPass == expectedPass)):
			
			print (userPass + expectedPass)

			outputLabel.configure(text = "Incorrect Password")
			passValid = False
		if(userValid and passValid):
			userInfo[2] = 'T'
			
			window.destroy()
			root.destroy()

	#declare and place the login button
	loginButton = Button(window, text = "Login", command= login, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	loginButton.place(relx = .5, rely = .825, anchor = CENTER)

	#link the window to an invisible root 
	bindRoot(root, window)
	
	#add a custom top bar to the window
	addTopBar(window, 2, True)
	
	#center the window in the middle of the screen
	center(window)
	
	#adds a border to the window
	addBorder(window)
	
	#displays the window
	window.mainloop()

#spawns a window that asks the user to sign-in or make new account
def selectionWindow(userChoice):
	
	#create window and static widgets
	grey = "#%02x%02x%02x" % (140, 140, 140)
	root = Tk()
	root.attributes('-alpha', 0.0)
	window = Toplevel(root)
	window.title("Welcome")
	window.geometry("400x240")
	window.configure(bg = grey)
	label = Label(window, text = "StockX Portfolio",  font = "candara 20", bg = grey)
	label.place(relx = .5, rely = .35, anchor = CENTER)

	#updates the user's choice as logging in
	def login():
		userChoice[0] = 1
		window.destroy()
		root.destroy()
		
	#updates the user's choice as making a new account
	def reg():
		userChoice[0] = 2
		window.destroy()
		root.destroy()

	#create and place the two buttons
	loginButton = Button(window, text = "Existing User", command=login, borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	loginButton.place(relx = .25, rely = .7, anchor = CENTER)

	regButton = Button(window, text = "Create Profile", command=reg,borderwidth = 1, 
		relief = "solid", font = "candara 14", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	regButton.place(relx = .75, rely = .7, anchor = CENTER)
	
	#bind window to invisible root
	bindRoot(root, window)

	#add a custom top bar to the window
	addTopBar(window, 2, True)
	
	#centers the window in the middle of the screen
	center(window)

	#adds a border ot the window
	addBorder(window)

	#displays the window
	window.mainloop()

#spawns and executes a window that prompts a user for their new account information
def regWindow(userInfo, usernameFileName):
	#declares and places window and static widgets
	grey = "#%02x%02x%02x" % (140, 140, 140)
	root = Tk()
	root.attributes('-alpha', 0.0)
	window = Toplevel(root)
	window.title("Portfolio Register")
	window.geometry("400x240")
	window.configure(bg = grey)
	userLabel = Label(window, text = "Username",  font = "candara 14", bg = grey)
	passLabel = Label(window, text = "Password",  font = "candara 14", bg = grey)
	outputLabel = Label(window, text = "New User",  font = "candara 20", bg = grey)
	userEntry = Entry(window, width = 20)
	passEntry = Entry(window, width = 20)
	userLabel.place(relx = .35, rely = .475, anchor = CENTER)
	userEntry.place(relx = .65, rely = .475, anchor = CENTER)
	passLabel.place(relx = .35, rely = .625, anchor = CENTER)
	passEntry.place(relx = .65, rely = .625, anchor = CENTER)
	outputLabel.place(relx = .5, rely = .275, anchor = CENTER)

	#creates an account if the username is not alredy taken and info
	#is at least 1 character long
	def reg():
		userInfo[0] = " " + userEntry.get() + " "
		userInfo[1] = " " + passEntry.get() + " "
		if(check_if_string_in_file(usernameFileName, userInfo[0])):
			outputLabel.configure(text = "Username Taken")
		elif(len(userEntry.get()) < 1 or len(passEntry.get()) < 1):
			outputLabel.configure(text = "Invalid Info")
		else: 
			userInfo[2] = 'T'
			window.destroy()
			root.destroy()


	#declare and palce button
	loginButton = Button(window, text = "Register", command= reg, borderwidth = 1, 
		relief = "solid", font = "candara 12", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	loginButton.place(relx = .5, rely = .825, anchor = CENTER)
	
	#bind window to an invisible root
	bindRoot(root, window)

	#add a custom top bar to the window
	addTopBar(window, 2, True)
	
	#center the window in the middle of the screen
	center(window)
	
	#add a border to the window
	addBorder(window)
	
	#display the window
	window.mainloop()

#adds new users info to the user and password files and creates their items file
def createProfile(userInfo):
	usernameFile = open("users.txt","a+")
	passwordFile = open("pass.txt","a+")
	usernameFile.write("\n" + userInfo[0])
	passwordFile.write("\n" + userInfo[1])
	userName = userInfo[0].strip()
	file = open( userName + "Items.txt", "a")
	file.close()

#displays primary window that contains the users portfolio items and
#contains buttons to access all of the methods that manipulate their
#portfolio's items
def portfolioWindow(userInfo):

	#create items list from the users items file
	items = loadItems(userInfo)

	#create refference variables, window, and static widgets 
	count = [-1]
	offset = [0]
	updatingNumber = [0]
	dotCounter = [0]
	root = Tk()
	root.attributes('-alpha', 0.0)
	activeItems = items[0:17] 
	needsUpdateMark = [False]
	scrollMark = [False]
	updatingMark = [False]
	grey = "#%02x%02x%02x" % (140, 140, 140)
	window = Toplevel(root)
	window.title(userInfo[0] + "'s Portfolio")
	window.geometry("800x600")
	window.configure(bg = grey)
	grey = "#%02x%02x%02x" % (140, 140, 140)
	canvas = Canvas(window, width = 700, height = 450, bg = grey, highlightbackground= "black")
	canvas.place(relx = .5, rely = .95, anchor = 's')
	

	#display items onto the canvas
	itemsToCanvas(canvas, items)
	
	#draw the header of the canvas
	canvas.create_text(32, 12, text = "Name", font = "candara 12 bold", anchor = "w")
	canvas.create_text(625, 12, text = "Price", font = "candara 12 bold")
	canvas.create_text(475, 12, text = "Size", font = "candara 12 bold")
	canvas.create_line(0, 25, 702, 25, width = 2)

	#increments the active items list by 1 to scroll down the list of given items
	def scrollDown():
		count[0] = -1
		items = loadItems(userInfo)
		if((offset[0]+17) < len(items)):
			offset[0] += 1
			for x in range(offset[0], (offset[0]+17)): 
				count[0] += 1
				activeItems[count[0]] = items[x]
			scrollMark[0] = True
	#decrements the active items list by 1 to scroll up the list of given items
	def scrollUp():
		count[0] = -1
		items = loadItems(userInfo)
		if(offset[0] > 0):
			offset[0] -= 1
			for x in range(offset[0], (offset[0]+17)): 
				count[0] += 1
				activeItems[count[0]] = items[x]
			scrollMark[0] = True
	#update items list and spawn the add window
	def add():	
		items = loadItems(userInfo)
		addWindow(userInfo, items, needsUpdateMark)
	#update items list, create list of item names, and spawn remove window
	def remove():
		items = loadItems(userInfo)
		namedItems = createNamedList(items)
		removeWindow(userInfo, namedItems, items, needsUpdateMark)	
	#update items list, declare count variable, generate a list of item names
	#and spawn edit window
	def edit():
		count[0] = -1
		items = loadItems(userInfo)
		namedItems = createNamedList(items)
		editWindow(userInfo, namedItems, items, count, needsUpdateMark)	
	#change the updating flag to show the window that the updating thread has begun,
	#then start the update thread
	def update():
		updatingMark[0] = True
		updateThread(userInfo, updatingMark, needsUpdateMark, updatingNumber)
	
	#constant loop that updates the window's display as background events happen
	def needsUpdate():
		
		#refreshes canvas with current items from file
		if(needsUpdateMark[0]):
			items = loadItems(userInfo)
			itemsToCanvas(canvas, items[0:17])
			offset[0] = 0
			needsUpdateMark[0] = False
			updatingNumber[0] = 0
		#refreshes canvas with current active items modified by scrolling
		if(scrollMark[0]):
			itemsToCanvas(canvas, activeItems)
			scrollMark[0] = False
		#shows updating screeen on canvas once the updating thread has started
		if(updatingMark[0]):
			dotCounter[0] += 1
			items = loadItems(userInfo)
			length = len(items)
			updateToCanvas(canvas, updatingNumber, length, dotCounter[0])
			window.update()

		#refresh after 30 milliseconds
		window.after(30, needsUpdate)
	
	#declare buttons
	addButton = Button(window, text = "Add Item", command= add, borderwidth = 2, 
		relief = "solid", font = "candara 12 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	removeButton = Button(window, text = "Remove Item", command= remove, borderwidth = 2, 
		relief = "solid", font = "candara 12 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	editButton = Button(window, text = "Edit Item", command= edit, borderwidth = 2, 
		relief = "solid", font = "candara 12 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	updateButton = Button(window, text = "Update All",  command = update, borderwidth = 2, 
		relief = "solid", font = "candara 12 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	scrollUpButton =Button(window, text = 	u"\u25B2", command= scrollUp, borderwidth = 2, 
		relief = "solid", font = "candara 10 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')
	scrollDownButton =Button(window, text = u"\u25BC", command= scrollDown, borderwidth = 2, 
		relief = "solid", font = "candara 10 bold", bg = grey, fg = 'black', 
		activeforeground = grey, activebackground = 'black')

	#draw scroll bar and place arrow buttons
	upButtonWindow = canvas.create_window(694, 33, anchor='ne', window=scrollUpButton)
	downButtonWindow = canvas.create_window(694, 444, anchor='se', window=scrollDownButton)
	canvas.create_line(683, 35, 683, 444, width = 2)

	#place buttons on the window
	addButton.place(relx = .108, rely = .1175, anchor = "center")
	removeButton.place(relx = .258, rely = .1175, anchor = 'center')
	editButton.place(relx = .408, rely = .1175, anchor = 'center')
	updateButton.place(relx = .94, rely = .1175, anchor = 'e')
	
	#bind the window to an invisible root
	bindRoot(root, window)
	
	#add a custon top bar to the window
	addTopBar(window, 4, True)
	
	#center the window in the middle of the screen
	center(window)
	
	#add a border to the window
	addBorder(window)
	
	#declare the constantly refreshing background loop
	window.after(50, needsUpdate)
	
	#display the window
	window.mainloop()

#assign gien names to user and pass files
usernameFileName = "users.txt"
passwordFileName = "pass.txt"

#declare navigating variables
userChoice = [None]
userInfo = [None] * 3

#open selection window
selectionWindow(userChoice)

#proceed to login window if chosen
if(userChoice[0] == 1):
	loginWindow(userInfo, usernameFileName, passwordFileName)
	
	#proceed to portfolio if login success
	if(userInfo[2] == 'T'):
		portfolioWindow(userInfo)

#proceed to registration page if selected
if(userChoice[0] == 2):
	regWindow(userInfo, usernameFileName)
	
	#create account and proceed to portfolio is registration successful
	if(userInfo[2] == 'T'):
		createProfile(userInfo)
		portfolioWindow(userInfo)
