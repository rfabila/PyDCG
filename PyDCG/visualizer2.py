"""This is the original visualizer module extended to handle
   lines. In the future it will substitute the module visualizer"""
from Tkinter import *
from tkFileDialog import *
from fractions import *
import os
import line


class Vis:
    
    def __init__(self, h=500, w=500, points=[],lines=[],segments=[],center=None,
                 deltazoom=Fraction(1,10),t=3,zoom=None,pic_button=False,paper_side=BOTTOM,pack=True):
        self.root=Tk()
        self.paper=Canvas(self.root,background="white",
                          height=h,
                          width=w)
        print self.paper['width'], self.paper['height']
        
        self.points=points
        
        if center!=None:
            self.center=center
        else:
            self.center=self.compute_center()
        
        print "center",self.center
            
        if zoom!=None:
            self.zoom=zoom
        else:
            self.zoom=self.compute_zoom(h,w)
        
        self.lines=lines
        self.segments=segments
        self.h=h
        self.w=w
        self.t=t
        self.deltazoom=deltazoom
        self.drawnpoints=[]
        self.drawnlines=[]
        self.drawnsegments=[]
        self.paper.bind("<Button-1>", self.leftclick)
        self.paper.bind("<ButtonRelease-1>", self.release)
        self.paper.bind("<Double-Button-1>", self.doubleclickleft)
        self.paper.bind("<Button-3>",self.rightclick)
        self.paper.bind("<Button-5>",self.zoomout)
        self.paper.bind("<Button-4>",self.zoomin)
        self.first_time=True
        self.draw()
    
        if pic_button:
            frame=Frame(self.root)
            frame.pack(side=TOP)
            photocam=PhotoImage(file=os.path.join(os.path.dirname(__file__), "Icons/camera.gif"))
            picboton=Button(frame,image=photocam,command=self.take_picture)
            picboton.pack(side=LEFT)
            picboton.image = photocam
        if pack:
            self.paper.pack(fill=BOTH,expand=YES,side=paper_side)
    
    def compute_zoom(self,h,w):
        zoom=Fraction(1,1)
        h=h/2
        w=w/2
        for x,y in self.points:
            x=max(abs(x-self.center[0]),1)
            y=max(abs(-(y-self.center[1])),1)
            z1=Fraction(w,2*x)
            z2=Fraction(h,2*y)
            if zoom>z1:
                zoom=z1
            if zoom>z2:
                zoom=z2
        return zoom
    
    def compute_center(self):
        if len(self.points)==0:
            return [0,0]
        X=[p[0] for p in self.points]
        Y=[p[1] for p in self.points]
        max_x=max(X)
        min_x=min(X)
        max_y=max(Y)
        min_y=min(Y)
        return [Fraction((max_x+min_x)/2,1),Fraction((max_y+min_y)/2,1)]
        
    
    def convert_to_screen_coords(self,point):
        """Converts the point to screen coordinates"""
        if self.first_time:
            width=self.w
            height=self.h
        else:
            width=self.paper.winfo_width()
            height=self.paper.winfo_height()
        x=point[0]-self.center[0]
        y=-(point[1]-self.center[1])
        x=x*self.zoom
        y=y*self.zoom
        x=x+width/2
        y=y+height/2
        x=int(x)
        y=int(y)
        
        return [x,y]

    def draw(self):
      self.drawLines()
      self.drawSegments()
      self.drawPoints()
      self.first_time=False
        
    def drawLines(self):
        self.destroylines()
        
        if self.first_time:
            width=self.w
            height=self.h
        else:
            width=self.paper.winfo_width()
            height=self.paper.winfo_height()
        real_width=(Fraction(width,1)/self.zoom)/2
        real_height=(Fraction(height,1)/self.zoom)/2
        
        lu_corner=[-real_width,real_height]
        ld_corner=[-real_width,-real_height]
        ru_corner=[real_width,real_height]
        rd_corner=[real_width,-real_height]
        
        #translation
        lu_corner=[lu_corner[0]+self.center[0],lu_corner[1]+self.center[1]]
        ld_corner=[ld_corner[0]+self.center[0],ld_corner[1]+self.center[1]]
        ru_corner=[ru_corner[0]+self.center[0],ru_corner[1]+self.center[1]]
        rd_corner=[rd_corner[0]+self.center[0],rd_corner[1]+self.center[1]]
        
        l_line=line.Line(lu_corner,ld_corner)
        r_line=line.Line(ru_corner,rd_corner)
        t_line=line.Line(lu_corner,ru_corner)
        d_line=line.Line(ld_corner,rd_corner)

        for l in self.lines:
            in_vals=[]
            
            in_line_lu=l.point_in_line(lu_corner)
            in_vals.append(in_line_lu)
            
            in_line_ld=l.point_in_line(ld_corner)
            in_vals.append(in_line_ld)
            
            in_line_ru=l.point_in_line(ru_corner)
            in_vals.append(in_line_ru)
            
            in_line_rd=l.point_in_line(rd_corner)
            in_vals.append(in_line_rd)
            
            val=0
            draw=False
            for x in in_vals:
                if x!=0:
                    val=x
            for x in in_vals:
                if (x!=0 and x!=val):
                    draw=True
            
            if draw:
                
                #intersection points
                p=l_line.line_intersection(l)
                if p==None:
                    p=t_line.line_intersection(l)
                q=r_line.line_intersection(l)
                if q==None:
                    q=d_line.line_intersection(l)
                
                #set them in the screen coordinates
                p=[p[0]-self.center[0],-(p[1]-self.center[1])]
                q=[q[0]-self.center[0],-(q[1]-self.center[1])]
                p=[p[0]*self.zoom,p[1]*self.zoom]
                q=[q[0]*self.zoom,q[1]*self.zoom]
                p=[p[0]+(width/2),p[1]+(height/2)]
                q=[q[0]+(width/2),q[1]+(height/2)]
                p=[int(p[0]),int(p[1])]
                q=[int(q[0]),int(q[1])]
                
                #draw the line
                #print p[0],p[1],q[0],q[1]
                self.drawnlines.append(self.paper.create_line(p[0],p[1],q[0],q[1],fill=l.color))
                
                
        
        
        
    def drawPoints(self):
        
        self.destroypoints()
        #self.centers=[]
        for p in self.points:
                
            [x,y]=self.convert_to_screen_coords(p)
            
            #change the implementation of colored pointsets! so that
            # say p[2]='red' (this implies some rewriting on other modules)
            #self.centers.append([x,y])
            if len(p)<=2:
                self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,fill="black"))
            else:
                if p[2]==0:
                    self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                                                                   outline="red",fill="red"))
                if p[2]==1:
                    self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                                                                   outline="blue",fill="blue"))
                if p[2]==2:
                    self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                                                                   outline="green",fill="green"))
        self.root.update()
                    
                    
    def drawSegments(self):
        self.destroysegments()
        for s in self.segments:
            #[x0,y0]=self.convert_to_screen_coords(self.points[s[0]])
            #[x1,y1]=self.convert_to_screen_coords(self.points[s[1]])
            [x0,y0]=self.convert_to_screen_coords(s[0])
            [x1,y1]=self.convert_to_screen_coords(s[1])
            if len(s)>2:    
                self.drawnsegments.append(self.paper.create_line(x0+self.t/2,
                                                                 y0+self.t/2,
                                                                 x1+self.t/2,
                                                                 y1+self.t/2,
                                                                 fill=s[2],
                                                                 width=3))
            else:
                self.drawnsegments.append(self.paper.create_line(x0+self.t/2,
                                                                 y0+self.t/2,
                                                                 x1+self.t/2,
                                                                 y1+self.t/2,
                                                                 fill="grey"))
    

                
    def moveCenter(self,d):
        
       
        self.center[0]=self.center[0]+(d[0]/self.zoom)
        self.center[1]=self.center[1]+(d[1]/self.zoom)
        #for p in self.drawnpoints:
         #   self.paper.move(p,-d[0],d[1])
        self.draw()
    
        
        

    def setzoom(self,zoom):
        self.zoom=zoom
        self.draw()
     
    def destroysegments(self):
        for s in self.drawnsegments:
            self.paper.delete(s)
        self.drawnsegments=[]

    def destroypoints(self):
        for p in self.drawnpoints:
            self.paper.delete(p)
        self.drawnpoints=[]
        
    def destroylines(self):
        for l in self.drawnlines:
            self.paper.delete(l)
        self.drawnlines=[]
            
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

        
