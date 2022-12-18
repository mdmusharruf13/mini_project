import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime,date
import tkinter as tk
from tkinter import *
from tkinter import filedialog,messagebox, ttk
import pandas as pd

def File_dialog():
    """This Function will open the file explorer and assign the chosen file path to label_file"""
    filename = filedialog.askopenfilename(title="Select A File",filetype=(("csv files", "*.csv"),("All Files", "*.*")))
    label_file["text"] = filename
    return None

def Load_excel_data():
    """If the file selected is valid this will load the file into the Treeview"""
    file_path = label_file["text"]
    try:
        excel_filename = r"{}".format(file_path)
        if excel_filename[-4:] == ".csv":
            df = pd.read_csv(excel_filename)
        else:
            df = pd.read_excel(excel_filename)

    except ValueError:
        tk.messagebox.showerror("Information", "The file you have chosen is invalid")
        return None
    except FileNotFoundError:
        tk.messagebox.showerror("Information", f"No such file as {file_path}")
        return None

    clear_data()
    tv1["column"] = list(df.columns)
    tv1["show"] = "headings"
    for column in tv1["columns"]:
        tv1.heading(column, text=column) # let the column heading = column name

    df_rows = df.to_numpy().tolist() # turns the dataframe into a list of lists
    for row in df_rows:
        tv1.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
    return None


def clear_data():
    tv1.delete(*tv1.get_children())
    return None

def startCamera():
    path = 'images'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)

    for cls in myList:
        crntImg = cv2.imread(f'{path}/{cls}')
        images.append(crntImg)
        classNames.append(os.path.splitext(cls)[0])
    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList
    encodeListKnown = findEncodings(images)
    print("Enocding Complete...")

    def markAttendance(name):
        with open('Attendance.csv','r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                today=date.today()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString},{today}')
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
        faceCrntFrme = face_recognition.face_locations(imgS)
        encodeCrntFrme = face_recognition.face_encodings(imgS,faceCrntFrme)
        for encodeFace,faceLoc in zip(encodeCrntFrme,faceCrntFrme):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1,x2,y2,x1 = faceLoc
                y1,x2,y2,x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,225,0),3)
                cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
                markAttendance(name)
        cv2.imshow('webcam',img) 
        if cv2.waitKey(1) & 0xFF == ord('m'):
            break

window = Tk()  
window.geometry("750x750")  
window.title("Home Page")
mainFrame = Frame(window,bg='orange')

def NewUser():
    win = Tk()
    win.geometry('400x200')

    def take():
        cam=cv2.VideoCapture(0)
        cv2.namedWindow('test')
        pth="images/"
        name=nameE.get()
        print(name)
        while True:
            res,frame = cam.read()
            if not res:
                print("failed to open camera..")
                break
            cv2.imshow('test',frame)

            k=cv2.waitKey(1)
            if k%256==27:
                print("closing...")
                break
            if k%256==32:
                if name:
                    img=os.path.join(pth,name+".jpeg")
                    cv2.imwrite(img,frame)
                else:
                    name='default'
                    img=os.path.join(pth,name+".jpeg")
                    cv2.imwrite(img,frame)
        cam.release()
        win.destroy()

    win.title('Registration form')
    point1=Label(win,text="Name is required befor capturing the image",font=('bold',13),fg='red').pack(side=TOP)
    nameL = Label(win,text="Name",font=('bold',13)).place(x=5,y=40)
    nameE = Entry(win)
    nameE.place(x=70,y=40)

    point1=Label(win,text="Space button - For capturing image.",font=('bold',13),fg='red').pack(side=BOTTOM)
    point2=Label(win,text="ESC key - For exiting the window.",font=('bold',13),fg='red').pack(side=BOTTOM)
    capB = Button(win,text="Take Picture",font=('bold',13),command=take).pack(side=BOTTOM)

    win.mainloop()

page1 = tk.Frame(mainFrame)
p1_lb = tk.Label(page1,text="FACE RECOGNITION ATTENDENCE \n SYSTEM\n\n\n\n", font=("Bold",30)).pack(pady=50)
p1_btn = tk.Button(page1,text="Register",font=('Bold',20),bg='green',fg='white',command=NewUser).pack(side=tk.LEFT,padx=100,pady=20)
p1_btn = tk.Button(page1,text="start camera",font=('Bold',20),bg='green',fg='white',command=startCamera).pack(side=tk.RIGHT,padx=100,pady=20)
page1.pack(pady=100)

page2 = tk.Frame(mainFrame)
p2_lb = tk.Label(page2,text="Attendance Sheet", font=("Bold",30))
p2_lb.pack(side=tk.TOP)
frame1 = Frame(page2,bg="white",width=700,height=300)
frame1.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
frame1.pack()

frame2 = Frame(page2,bg="skyblue",width=700,height=130).pack(side=BOTTOM)

file_frame = tk.LabelFrame(page2, text="Open File")
file_frame.place(height=140, width=700, rely=0.72, relx=0)

# Buttons
button1 = tk.Button(file_frame, text="Browse A File",font=("Bold",15),bg='green',fg='white', command=File_dialog)
button1.place(rely=0.65, relx=0.50)

button2 = tk.Button(file_frame, text="Load File",font=("Bold",15),bg='green',fg='white', command=Load_excel_data)
button2.place(rely=0.65, relx=0.30)

# The file/file path text
label_file = ttk.Label(file_frame, text="No File Selected")
label_file.place(rely=0, relx=0)

## Treeview Widget
tv1 = ttk.Treeview(frame1)
tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

mainFrame.pack(fill=tk.BOTH,expand=True)

pages = [page1,page2]
count=0

def moveNextPage():
    global count
    if not count>len(pages)-2:
        for p in pages:
            p.pack_forget()
        count +=1
        page = pages[count]
        page.pack(pady=100)

def moveBackPage():
    global count
    if not count == 0:
        for p in pages:
            p.pack_forget()
        count -=1
        page = pages[count]
        page.pack(pady=100)

bottomframe = Frame(window) 
back_btn = tk.Button(bottomframe,text="Home",font=('Bold',18),bg='red',fg="white",width=10,command=moveBackPage)
back_btn.pack(side=tk.LEFT,padx=40)
next_btn = tk.Button(bottomframe,text="Attendence",font=('Bold',18),bg='red',fg="white",width=10, command=moveNextPage)
next_btn.pack(side=tk.LEFT,padx=40)
exit = tk.Button(bottomframe,text="Exit",font=('Bold',18),bg='red',fg="white",width=8, command=window.destroy)
exit.pack(side=tk.RIGHT,padx=40)
bottomframe.pack(side=tk.BOTTOM,pady=10)

window.mainloop()
