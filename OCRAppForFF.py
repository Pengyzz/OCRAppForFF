# -*- coding: utf-8 -*-
"""
OCRAppForFF is a Python based application that uses Tesseract-OCR to convert
two columns of text in an image into spreadsheet format.
"""

from PIL import Image, ImageTk
import tkinter as tk
from mss import mss
import pytesseract
import PIL.ImageOps


class OCRApp(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master=None)
        self.master = master
        self.pack()
        self.fullscreen = False #full screenstate
        
        #actual coordinates on the screen
        self.startX = 0
        self.startY = 0
        self.endX = 0
        self.endY = 0
        
        self.results = {}
        
        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="left")

        self.createOverlay = tk.Button(self, text="Select Region", command=self.createOverlay)
        self.createOverlay.pack(side="left")
        
        #for testing purposes
#        self.printCoords = tk.Button(self, text="PrintCoords", command=self.printCoords)
#        self.printCoords.pack(side="left")
#        
#        self.takeScreenshot = tk.Button(self, text="Take Screenshot", command=self.takeScreenshot)
#        self.takeScreenshot.pack(side="bottom")
#        
#        self.showScreenshot = tk.Button(self, text="Show Screenshot", command=self.showScreenshot)
#        self.showScreenshot.pack(side="bottom")
        
        self.isRecording = False
        self.stopRec = tk.Button(self, text="Stop Recording", command=self.stopRec)
        self.stopRec.pack(side="bottom")
        self.startRec = tk.Button(self, text="Start Recording", command=self.startRec)
        self.startRec.pack(side="bottom")
        
    
    def createOverlay(self):
#        print("overlay created")
        
        self.overlay = tk.Toplevel(self)
        self.instruct = tk.Toplevel(self)
        self.instructText = tk.Label(self.instruct, text="test")
        self.x = self.y = 0
        
        self.canvas = tk.Canvas(self.overlay, cursor="cross")
        self.canvas.pack(expand='YES', fill='both')
        
        self.fullscreen = not self.fullscreen
        self.overlay.attributes("-fullscreen", self.fullscreen)
        
        
        with mss() as sct:
            self.im = sct.grab(sct.monitors[1])

        self.canvas.bind("<ButtonPress-1>", self.onLeftClick)
        self.canvas.bind("<B1-Motion>", self.onLeftDrag)
        self.canvas.bind("<ButtonRelease-1>", self.onLeftRelease)
        self.overlay.bind("<Escape>", self.close_overlay)

        self.selection = None
        
        self.img = Image.frombytes("RGB", self.im.size, self.im.bgra, "raw", "BGRX")
        self.imgLighter = self.img.point(lambda p: p*1.3)
        #img.show()

        self.tk_im = ImageTk.PhotoImage(self.imgLighter)
        self.canvas.create_image(0,0,anchor="nw",image=self.tk_im)   
        
        self.instruct.lift()

    def onLeftClick(self, event):
        #save starting coordinates
        self.startX = self.canvas.canvasx(event.x)
        self.startY = self.canvas.canvasy(event.y)

        #create a red rectangle if it doesn't already exist
        if not self.selection:
            self.selection = self.canvas.create_rectangle(self.x, self.y, 5, 5, outline='red', fill='red')

    def onLeftDrag(self, event):
        #current XY coordinates of the mouse while dragging
        currX = self.canvas.canvasx(event.x)
        currY = self.canvas.canvasy(event.y)

        #expand rectangle to follow the mouse while dragging
        self.canvas.coords(self.selection, self.startX, self.startY, currX, currY)    

    def onLeftRelease(self, event):
        #save end coordinates
        self.endX = self.canvas.canvasx(event.x)
        self.endY = self.canvas.canvasy(event.y)
    
    #for testing purposes    
#    def printCoords(self):
#        print(self.startX,self.startY,self.endX,self.endY)
    
    def close_overlay(self, event):
#        print("closemethod")
        self.state = False
        self.overlay.destroy()
        self.instruct.destroy()
    
    #for testing purposes        
#    def takeScreenshot(self):
#        portion = {"top": int(self.startY), "left": int(self.startX), 
#                   "width": int(self.endX-self.startX), "height": int(self.endY-self.startY)}
#        with mss() as sct:
#            self.ss = sct.grab(portion)
    #for testing purposes
#    def showScreenshot(self):
#        self.showSS = tk.Toplevel(self)
#        self.canvasSS = tk.Canvas(self.showSS, cursor="cross")
#        self.canvasSS.pack(expand='YES', fill='both')
#        
#        self.imgSS = Image.frombytes("RGB", self.ss.size, self.ss.bgra, "raw", "BGRX")
#        self.tkimgSS = ImageTk.PhotoImage(self.imgSS)
#        self.canvasSS.create_image(0,0,anchor="nw",image=self.tkimgSS) 
    
    def startRec(self):
#        print("startrec")
        self.isRecording = True
        self.portion = {"top": int(self.startY), "left": int(self.startX), 
                   "width": int(self.endX-self.startX), "height": int(self.endY-self.startY)}
        self.showSS = tk.Toplevel(self)
        self.showSS.title("Current Frame")
        
        self.canvasSS = tk.Canvas(self.showSS, width=self.portion["width"],
                                  height=self.portion["height"], cursor="cross")
        self.canvasSS.pack(expand='YES', fill='both')
        self.recording()
    
    def recording(self, delay=1000):
        if(self.isRecording):
#            print("recloop")
            with mss() as sct:
                self.ss = sct.grab(self.portion)
            self.imgSS = Image.frombytes("RGB", self.ss.size, self.ss.bgra, "raw", "BGRX").convert("L")
            #self.imgSS = self.imgSS.point(lambda x: 0 if (x>200) & (x!=214) else 255, '1')
            #self.imgSS = self.imgSS.point(lambda x: 125 if x>215 else x, '1')
            self.tkimgSS = ImageTk.PhotoImage(self.imgSS)
            self.canvasSS.create_image(0,0,anchor="nw",image=self.tkimgSS)
            
            #parse image through tesseract
            imgtext = pytesseract.image_to_string(self.imgSS)
            print(imgtext)
            self.parseOutput(imgtext)
            print(self.results)
            self.after(delay, self.recording)
            #pytesseract.image_to_string(question_img, config="-c tessedit_char_whitelist=0123456789 -oem 0")
            
    def stopRec(self):        
        self.isRecording = False
        #close the frame preview
        self.showSS.destroy()
    
    def parseOutput(self, output):
        byLine = output.split("\n")
        for line in byLine:
            #print("currentline " + line )
            if line.strip():
                lineSplit = line.rsplit(" ", 1)
                #print(lineSplit)
                if lineSplit[0] not in self.results:
                    self.results[lineSplit[0]] = lineSplit[1]
                
        
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract'  
root = tk.Tk()
root.title("OCRApp for FF")
app = OCRApp(root)
root.mainloop()