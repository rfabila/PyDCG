#    PyDCG
#
#    A Python library for Discrete and Combinatorial Geometry.
#
#    Copyright (C) 2015 Ruy Fabila Monroy
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation version 2. 
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""This is the original visualizer module extended to handle
   lines. In the future it will substitute the module visualizer"""
from tkinter import *
from tkinter.filedialog import *
from fractions import *
import os
from . import line
from . import geometricbasics
from . import convexhull


class Vis:
    
    def __init__(self, h=500, w=500, points=[],lines=[],segments=[],center=None,
                 deltazoom=Fraction(1,10),t=3,zoom=None,pic_button=False,paper_side=BOTTOM,
                 pack=True,show_grid=False,grid_color="light gray",move_points_button=False,polygons=[],
                 add_point_button=False,delete_point_button=False,update_objects=None,keyboard_events=[]):
        self.root=Tk()
        self.paper=Canvas(self.root,background="white",
                          height=h,
                          width=w)
        print(self.paper['width'], self.paper['height'])
        
        self.points=points
        
        if center!=None:
            self.center=center
        else:
            self.center=self.compute_center()
        
        print("center",self.center)
            
        if zoom!=None:
            self.zoom=zoom
        else:
            self.zoom=self.compute_zoom(h,w)
        
        self.grabbed=False
        self.grabbed_point=None
        self.max_distance=49
        
        self.state="view"
        
        self.update_objects=update_objects
        self.show_grid=show_grid
        self.grid_color=grid_color
        self.lines=lines
        self.segments=segments
        self.polygons=polygons
        self.h=h
        self.w=w
        self.t=t
        self.deltazoom=deltazoom
        self.drawnpoints=[]
        self.drawnlines=[]
        self.drawnsegments=[]
        self.drawnpolygons=[]
        self.paper.bind("<Button-1>", self.leftclick)
        self.paper.bind("<ButtonRelease-1>", self.release)
        self.paper.bind("<Double-Button-1>", self.doubleclickleft)
        self.paper.bind("<Button-3>",self.rightclick)
        self.paper.bind("<Button-5>",self.zoomout)
        self.paper.bind("<Button-4>",self.zoomin)
        self.first_time=True
        self.draw()
    
        if pic_button or move_points_button:
            frame=Frame(self.root)
            frame.pack(side=TOP)
            
    
        if pic_button:
            photocam=PhotoImage(master=self.paper, file=os.path.join(os.path.dirname(__file__), "Icons/camera.gif"))
            picboton=Button(frame,image=photocam,command=self.take_picture)
            picboton.pack(side=LEFT)
            picboton.image = photocam
        
        if move_points_button:
            hand=PhotoImage(file=os.path.join(os.path.dirname(__file__), "Icons/hand.gif"))
            boton=Button(frame,image=hand,command=self.change_state("move point"))
            boton.pack(side=LEFT)
            boton.image = hand
            
        if add_point_button:
            add_pic=PhotoImage(file=os.path.join(os.path.dirname(__file__), "Icons/add.png"))
            boton=Button(frame,image=add_pic,command=self.change_state("add point"))
            boton.pack(side=LEFT)
            boton.image = add_pic
            
        if delete_point_button:
            del_pic=PhotoImage(file=os.path.join(os.path.dirname(__file__), "Icons/gtk-remove.png"))
            boton=Button(frame,image=del_pic,command=self.change_state("delete point"))
            boton.pack(side=LEFT)
            boton.image = del_pic
            
        for Keyboard in keyboard_events:
            def f(event):
                Keyboard[1](self)(event)
                self.draw()
            #needed to do it this way in order to be able to redraw   
            self.root.bind(Keyboard[0],f)
            
        
        if pack:
            self.paper.pack(fill=BOTH,expand=YES,side=paper_side)
    
    def change_state(self,state):
        def f():
            if self.state!=state:
                self.state=state
            else:
                self.state="view"
        return f
    
    def move_points(self):
        if self.state!="move point":
            self.state="move point"
        else:
            self.state="view"
    
    def add_point(self):
        if self.state!="add point":
            self.state="add point"
        else:
            self.state="view"
    
    def closest_point(self,point):
        """Returns the index point of the set current point set closest to the given point."""
        q=0
        min=(self.points[q][0]-point[0])**2+(self.points[q][1]-point[1])**2
        
        for p in range(len(self.points)):
            new_min=(self.points[p][0]-point[0])**2+(self.points[p][1]-point[1])**2
            if new_min<min:
                min=new_min
                q=p
        return q
    
    # def compute_zoom_2(self,h,w):
    #     zoom=Fraction(1,1)
    #     h=h/2
    #     w=w/2
    #     for p in self.points:
    #         x=p[0]
    #         y=p[1]
    #         x=max(abs(x-self.center[0]),1)
    #         y=max(abs(-(y-self.center[1])),1)
    #         z1=Fraction(w,2*x)
    #         z2=Fraction(h,2*y)
    #         if zoom>z1:
    #             zoom=z1
    #         if zoom>z2:
    #             zoom=z2
    #     return zoom
    
    def compute_zoom(self,h,w):
        zoom=Fraction(1,1)
        if len(self.points)==0:
            return zoom
        X=[p[0] for p in self.points]
        Y=[p[1] for p in self.points]
        max_x=max(X)
        min_x=min(X)
        max_y=max(Y)
        min_y=min(Y)
        
        w_pts=max_x-min_x
        if w_pts<0:
            w_pts=w_pts*-1
        if w_pts==0:
            w_pts=2
        
        h_pts=max_y-min_y
        if h_pts<0:
            h_pts=h_pts*-1
        
        if h_pts==0:
            h_pts=2
            
        z1=Fraction(w,2*w_pts)
        z2=Fraction(h,2*h_pts)
        return min(z1,z2)
            
    
    def compute_center(self):
        if len(self.points)==0:
            return [0,0]
        X=[p[0] for p in self.points]
        Y=[p[1] for p in self.points]
        max_x=max(X)
        min_x=min(X)
        max_y=max(Y)
        min_y=min(Y)
        return [Fraction((max_x+min_x),2),Fraction((max_y+min_y),2)]
        
    
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
        
        if self.update_objects!=None:
            self.update_objects(self)
        
        self.destroysegments()
        
        if self.show_grid:
            self.draw_grid()
            
        self.drawLines()
        self.drawSegments()
        self.drawPolygons()
        self.drawPoints()
        self.first_time=False
    
    def drawPolygons(self):
        self.destroypolygons()
        
        for P in self.polygons:
            if P.bounded:
                vertices=[self.convert_to_screen_coords(p) for p in P.vertices]
                Q=self.paper.create_polygon(vertices,fill=P.fill,outline=P.outline)
                self.drawnpolygons.append(Q)
            else:
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
        
                corners=[lu_corner,ld_corner,ru_corner,rd_corner]
        
                l_line=line.Line(p=lu_corner,q=ld_corner)
                r_line=line.Line(p=ru_corner,q=rd_corner)
                t_line=line.Line(p=lu_corner,q=ru_corner)
                d_line=line.Line(p=ld_corner,q=rd_corner)
                
                S=[l_line,r_line,t_line,d_line]
                vertices=[P.vertices[0],P.vertices[1]]
            
                for s in S:
                    p=P.rays[0].intersection(s)
                    if p!=None:
                        vertices.append(p)
                            
                for s in S:
                    p=P.rays[1].intersection(s)
                    if p!=None:
                        vertices.append(p)
                        
                for s in S:
                    p=P.base.intersection(s)
                    if p!=None:
                        vertices.append(p)
                
                for s in corners:
                    if P.point_in_interior(s):
                        vertices.append(s)
                
                vertices=convexhull.CH(vertices)
                    
                o=[Fraction(P.vertices[0][0]+P.vertices[1][0],2),
                    Fraction(P.vertices[0][1]+P.vertices[1][1],2)]
                vertices=geometricbasics.sort_around_point(o,vertices)
                vertices=[self.convert_to_screen_coords(x) for x in vertices]
                Q=self.paper.create_polygon(vertices,fill=P.fill,outline=P.outline)
                self.drawnpolygons.append(Q)
                
                
                
                
                
    def draw_grid(self):
        
        grid_segments=[]
        
        x1 = min(self.points, key=lambda p: p[0])[0] - 1
        x2 = max(self.points, key=lambda p: p[0])[0] + 1

        y1 = min(self.points, key=lambda p: p[1])[1] - 1 
        y2 = max(self.points, key=lambda p: p[1])[1] + 1
                
        for i in range(x1,x2+1):
            grid_segments.append([[i,y1],[i,y2]])
            
        for i in range(y1,y2+1):
            grid_segments.append([[x1,i],[x2,i]])
            
        for s in grid_segments:
            p = self.convert_to_screen_coords(s[0])
            q = self.convert_to_screen_coords(s[1])
            self.drawnsegments.append(self.paper.create_line(p[0],p[1],q[0],q[1],fill=self.grid_color))
        
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
                colors = ['red', 'blue', 'green', 'orange', 'cyan', 'purple', 'yellow', 'magenta', 'pale green', 'plum1', 'slate blue', 'violet red',
                 'brown4', 'gold', 'coral', 'SeaGreen1', 'RoyalBlue1', 'turquoise1', 'khaki1', 'OliveDrab1', 'DeepPink2', 'chocolate1', 'SteelBlue1', 'cyan3', 'PaleGreen1']
                self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                                                                   outline=colors[p[2]],fill=colors[p[2]]))
                # if p[2]==0:
                #     self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                #                                                    outline="red",fill="red"))
                # if p[2]==1:
                #     self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                #                                                    outline="blue",fill="blue"))
                # if p[2]==2:
                #     self.drawnpoints.append(self.paper.create_oval(x-self.t,y-self.t,x+self.t,y+self.t,
                                                                   # outline="green",fill="green"))
        self.root.update()
                    
                    
    def drawSegments(self):
        
        for s in self.segments:
            #[x0,y0]=self.convert_to_screen_coords(self.points[s[0]]) #TODO: restore this part
            #[x1,y1]=self.convert_to_screen_coords(self.points[s[1]])
            [x0,y0]=self.convert_to_screen_coords(s[0])
            [x1,y1]=self.convert_to_screen_coords(s[1])
            if len(s)>2:    
                self.drawnsegments.append(self.paper.create_line(x0+self.t/2,
                                                                 y0+self.t/2,
                                                                 x1+self.t/2,
                                                                 y1+self.t/2,
                                                                 fill=s[2],
                                                                 width=s[3] if len(s) > 3 else 3))#TODO: restore this part, it was width=s[3])
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
        
    def destroypolygons(self):
        for p in self.drawnpolygons:
            self.paper.delete(p)
        self.drawnpolygons=[]
        
    def destroylines(self):
        for l in self.drawnlines:
            self.paper.delete(l)
        self.drawnlines=[]
            
    def leftclick(self, event):
        if self.state=="view":
            global start
            start=[int(self.paper.canvasx(event.x)),int(self.paper.canvasy(event.y))]
        elif self.state=="move point" and len(self.points)>0:
            point=self.convert_from_screen_coordinates([self.paper.canvasx(event.x),
                                self.paper.canvasy(event.y)])
            q=self.closest_point(point)
            distance=(point[0]-self.points[q][0])**2+(point[1]-self.points[q][1])**2
            if distance*self.zoom<=self.max_distance:
               #print q
               self.grabbed=True
               self.grabbed_point=q
               #print self.grabbed_point
            else:
                self.grabbed=None
        
        elif self.state=="add point":
            point=self.convert_from_screen_coordinates([self.paper.canvasx(event.x),
                                self.paper.canvasy(event.y)])
            self.points.append(point)
            self.draw()
        elif self.state=="delete point":
            point=self.convert_from_screen_coordinates([self.paper.canvasx(event.x),
                                self.paper.canvasy(event.y)])
            q=self.closest_point(point)
            distance=(point[0]-self.points[q][0])**2+(point[1]-self.points[q][1])**2
            if distance*self.zoom<=self.max_distance:
                self.points.pop(q)
                self.draw()

    def convert_from_screen_coordinates(self, point):
        x = int(point[0])
        y = int(point[1])
        x = x - self.paper.winfo_width() / 2
        y = y - self.paper.winfo_height() / 2
        x = x / self.zoom
        y = y / self.zoom
        x = x + self.center[0]
        y = -y + self.center[1]
        x = int(round(x))
        y = int(round(y))
        return [x, y]

    def doublezoomin(self):
        self.setzoom(2*self.zoom)

    def doublezoomout(self):
        self.setzoom(self.zoom/2)

    def rightclick(self, event):
        self.doublezoomout()

    def doubleclickleft(self, event):
        start = [int(self.paper.canvasx(event.x)), int(self.paper.canvasy(event.y))]
        end = [self.paper.winfo_width()/2, self.paper.winfo_height()/2]
        v = [-(end[0]-start[0]), (end[1]-start[1])]
        self.moveCenter([v[0], v[1]])
        self.doublezoomin()

    def release(self,event):
        if self.state=="view":
            global end
            end=[int(self.paper.canvasx(event.x)),int(self.paper.canvasy(event.y))]
            v=[-(end[0]-start[0]),(end[1]-start[1])]
            self.moveCenter([v[0],v[1]])
        elif self.state=="move point" and self.grabbed:
            point=self.convert_from_screen_coordinates([self.paper.canvasx(event.x),
                                                        self.paper.canvasy(event.y)])
            if self.grabbed:
                self.points[self.grabbed_point][0]=point[0]
                self.points[self.grabbed_point][1]=point[1]
                self.draw()
    
    def zoomout(self,event):
        if self.zoom >= 1.0:
            self.setzoom(self.zoom-self.deltazoom*self.zoom)
        else:
            zoominv=1/self.zoom
            newzoominv=zoominv+self.deltazoom*zoominv
            self.setzoom(1/(newzoominv))
                

    def zoomin(self,event):
        if self.zoom >= 1.0:
            self.setzoom(self.zoom+self.deltazoom*self.zoom)
        else:
            zoominv = 1 / self.zoom
            newzoominv = zoominv - self.deltazoom * zoominv
            self.setzoom(1 / newzoominv)

    def take_picture(self):
        """Saves the current view as an ps file"""
        filename=asksaveasfilename(filetypes = [("postscript", "*.ps *.eps")], defaultextension=".ps")
        self.paper.postscript(file=filename)
