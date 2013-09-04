from Tkinter import *
from tkFileDialog import *
#CHANGE ZOOM TO Fraction!!!!

class Vis:
    
    def __init__(self, h=500, w=500, points=[],deltazoom=0.1,t=1,zoom=1.0,pic_button=False,paper_side=BOTTOM):
        self.root=Tk()
        self.paper=Canvas(self.root,background="white",
                          height=h,
                          width=w)
        print self.paper['width'], self.paper['height']
        self.center=[0,0]
        self.points=points
        self.zoom=zoom
        self.h=h
        self.w=w
        self.t=t
        self.deltazoom=deltazoom
        self.drawnpoints=[]
        self.paper.bind("<Button-1>", self.leftclick)
        self.paper.bind("<ButtonRelease-1>", self.release)
        self.paper.bind("<Double-Button-1>", self.doubleclickleft)
        self.paper.bind("<Button-3>",self.rightclick)
        self.paper.bind("<Button-5>",self.zoomout)
        self.paper.bind("<Button-4>",self.zoomin)
        self.drawPoints()
        
        if pic_button:
            frame=Frame(self.root)
            frame.pack(side=TOP)
            
        if pic_button:
            photocam=PhotoImage(file="icons/camera.gif")
            picboton=Button(frame,image=photocam,command=self.take_picture)
            picboton.pack(side=LEFT)
            picboton.image = photocam
            
        self.paper.pack(fill=BOTH,expand=YES,side=paper_side)


    def drawPoints(self):
        
        self.destroypoints()
        self.centers=[]
        for p in self.points:
                
            x=p[0]-self.center[0]
            y=-(p[1]-self.center[1])
            x=x*self.zoom
            y=y*self.zoom
            
            x=x+self.paper.winfo_width()/2
            y=y+self.paper.winfo_height()/2
            
            #change the implementation of colored pointsets! so that
            # say p[2]='red' (this implies some rewriting on other modules
            self.centers.append([x,y])
            if len(p)<=2:
                self.drawnpoints.append(self.paper.create_oval(x,y,x+self.t,y+self.t,fill="black"))
            else:
                if p[2]==0:
                    self.drawnpoints.append(self.paper.create_oval(x,y,x+self.t,y+self.t,
                                                                   outline="red",fill="red"))
                if p[2]==1:
                    self.drawnpoints.append(self.paper.create_oval(x,y,x+self.t,y+self.t,
                                                                   outline="blue",fill="blue"))
                if p[2]==2:
                    self.drawnpoints.append(self.paper.create_oval(x,y,x+self.t,y+self.t,
                                                                   outline="green",fill="green"))
        self.root.update()
                    
                    
    

                
    def moveCenter(self,d):
        
       
        self.center[0]=self.center[0]+(d[0]/self.zoom)
        self.center[1]=self.center[1]+(d[1]/self.zoom)
        #self.drawPoints()
        for p in self.drawnpoints:
            self.paper.move(p,-d[0],d[1])

        
        

    def setzoom(self,zoom):
        self.zoom=zoom
        self.drawPoints()
        

    def destroypoints(self):
        for p in self.drawnpoints:
            self.paper.delete(p)
            
    def leftclick(self, event):
        global start
        start=[int(self.paper.canvasx(event.x)),int(self.paper.canvasy(event.y))]
    
    def doublezoomin(self):
        self.setzoom(2*self.zoom)
        
    def doublezoomout(self):
        self.setzoom(self.zoom/2)
        
    def rightclick(self,event):
        self.doublezoomout()
        
    def doubleclickleft(self,event):
        start=[int(self.paper.canvasx(event.x)),int(self.paper.canvasy(event.y))]
        end=[self.paper.winfo_width()/2,self.paper.winfo_height()/2]
        v=[-(end[0]-start[0]),(end[1]-start[1])]
        self.moveCenter([v[0],v[1]])
        self.doublezoomin()
        
    def release(self,event):
        global end
        end=[int(self.paper.canvasx(event.x)),int(self.paper.canvasy(event.y))]
        v=[-(end[0]-start[0]),(end[1]-start[1])]
        self.moveCenter([v[0],v[1]])
    
    def zoomout(self,event):
        if self.zoom >= 1.0:
            self.setzoom(self.zoom-self.deltazoom)
        else:
            zoominv=1/self.zoom
            newzoominv=zoominv+self.deltazoom*zoominv
            self.setzoom(1/(newzoominv))
                

    def zoomin(self,event):
        if self.zoom >= 1.0:
            self.setzoom(self.zoom+self.deltazoom*self.zoom)
        else:
            zoominv=1/self.zoom
            newzoominv=zoominv-self.deltazoom*zoominv
            self.setzoom(1/(newzoominv))
    
        
            
    def take_picture(self):
        """Saves the current view as an ps file"""
        filename=asksaveasfilename(filetypes=[("postscript","*.ps *.eps")],defaultextension=".ps")
        self.paper.postscript(file=filename)

        
