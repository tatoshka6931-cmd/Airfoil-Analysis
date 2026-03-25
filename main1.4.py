
#MAIN 1.4 - file run by user

#   LIBRARY PACKAGES
import pygame_widgets
import pygame
import runfile

pygame.init()
pygame.font.init()

#initialise dictionary with aerofoil defining points

points={
        #   top left window
    "points_1":[[100, 214], [250, 150], [400, 150], [550, 177], [700, 212], [850, 245],[1000,280],
              [100, 316], [250, 375], [400, 340], [550, 319], [700, 310], [850, 300]],
        #   bottom left window
    "points_2":[[100, 714], [250, 650], [400, 650], [550, 677], [700, 712], [850, 745], [1000, 780],
              [100, 816], [250, 875], [400, 840], [550, 819], [700, 810], [850, 800]],
        #   bottom right window
    "points_3":[[1100, 714], [1250, 650], [1400, 650], [1550, 677], [1700, 712], [1850, 745], [2000, 780],
              [1100, 816], [1250, 875], [1400, 840], [1550, 819], [1700, 810], [1850, 800]]
    }


#   GUI COLOUR CONSTANTS
SLDR_CLR_1 = (255,255,255)      #   slider track colour
SLDR_CLR_2 = (0,0,0)            #   slider node colour
BCKGRND_CLR = (200,200,200)     #   outer GUI box
WINDOW_CLR = (166, 164, 164)    #   indiv aerofoil window box
BTN_CLR_1 = (170,170,170)     #   default colour 
BTN_CLR_2 = (125,125,125)     #   alternative colour
TXT_CLR = (200,200,200)         #   button text colour
TXT_CLR_2 = (50,50,50)          #   

FONT = pygame.font.SysFont('wilke', 40)
FONT_2 = pygame.font.SysFont('helvetica', 18, bold=True)
FONT_3 = pygame.font.SysFont('wilke', 46)

#   GEOMETRIC CONSTANTS
SLDRWIDTH, SLDRHEIGHT, NODEHEIGHT = 10, 190, 10                  
BTN_DIMENSIONS = (220,55)        
WIN_DIMENSIONS = (960,455)
INPUT_BOX_DIMENSIONS = (150,50)


#   PHYSICAL CONSTANTS - by default
MIN_AOA = 0
MAX_AOA = 15
V_INF = 5
RHO_INF = 1.225



class Button:
    """
    button class draws a box and blits text on it
    """
    def __init__(self,x,y,text,_dimens,clr):
        self.rect=pygame.Rect(x,y,_dimens[0],_dimens[1])
        self.text=text
        self.colour = clr
    def draw_button(self,win, font):
        font=font
        pygame.draw.rect(win,self.colour,self.rect)
        text_surface=font.render(self.text,True,TXT_CLR_2)
        win.blit(text_surface,(self.rect.x+10,self.rect.y+10))
        pygame.display.update()
    
    
    
class Slider:
    """
    sliders are made by drawing separate boxes controlling the track and the node
    """
    def __init__(self,_sldr_x,sldr_y,node_y):
        self.node_y=node_y  #   node_x would be same as sldr_x so its redundant
        self._sldr_x=_sldr_x
        self.sldr_y=sldr_y
    
    def draw_slider(self,win):
        # draw slider track
        track=pygame.Rect(self._sldr_x, self.sldr_y, SLDRWIDTH, SLDRHEIGHT)
        pygame.draw.rect(win, SLDR_CLR_1, track)
        
        # draw slider node
        node=pygame.Rect(self._sldr_x, self.node_y, SLDRWIDTH, NODEHEIGHT)
        pygame.draw.rect(win, SLDR_CLR_2, node)
        pygame.display.update()
  
    

class Dropdown(Button):
    """
    Drop-down menu - inheritance from Button class
    when pressed, creates n rectangles below the button until any of those are pressed again
    """
    def __init__(self,x,y,text,dimens,clr,selection,name):
        super().__init__(x,y,text,dimens,clr)
        self.x=x
        self.y=y
        self._dimens=dimens
        self.selection=selection    #   array of items to select from
        self.name=name
        self.selection_array=[]
        self.active=False           #   True when menu is opened
        self.text=text
        self.menu_coords=[]         #   coords of the menu when opened
       
    def menu_pressed(self,win):
        #   drop down menu is activated and selection items are displayed
        print('menu pressed')
        y_temp=self.y+self._dimens[1]
        
        #   loops through every item in the drop-down menu selection array
        for item in self.selection:
            selection_item=pygame.Rect(self.x+1,y_temp+1,self._dimens[0]-2,self._dimens[1]-2)
            #   border added for easier selection
            sel_item_border=pygame.Rect(self.x,y_temp,self._dimens[0],self._dimens[1])
            
            pygame.draw.rect(win,(200,200,200),sel_item_border)
            pygame.draw.rect(win,self.colour,selection_item)
            text_surface=FONT.render(str(item),True,TXT_CLR_2)
            win.blit(text_surface,(self.rect.x+10,y_temp+10))
            pygame.display.update()
            self.selection_array.append([self.x,y_temp,item])
            
            y_temp=y_temp+self._dimens[1]
        self.active=True
        
        self.menu_coords=[self.x,self.y,self.x+self._dimens[0],y_temp+self._dimens[1]]
        print('self menu coords',self.menu_coords)
        print('selection_array ', self.selection_array)
        return self.menu_coords
    
    def selection_made(self,pos):
        # one of the selection items was pressed
        print('selection made')
        for item in self.selection_array:   #   loop determines which item has been pressed and returns it as a string
            if item[1]<=pos[1]<=(item[1]+self._dimens[1]):
                self.text=str(item[2])
                print('selected value ',self.text)
                self.active=False
                break
        return self.text
    


class AerofoilWindow:
    """
    Up to 3 Airfoil window objects can be on the screen
    instantiated by pressing 'New Aerofoil+' button
    the geometry of each aerofoil window is individually edited or loaded from a txt file
    """
    def __init__(self,x,y,points,win):
        self.x=x
        self.y=y
        self.points=points      #   initial values
        self.slider_array=[]    #   NB: array doesn't contain the trailing edge point (middle one) as it's fixed
        self.window=pygame.Rect(self.x, self.y, WIN_DIMENSIONS[0],WIN_DIMENSIONS[1])
        pygame.draw.rect(win, WINDOW_CLR, self.window)
        self.__initialise=True
        
    def draw_lines(self,win,points):  #   ???review this
        """  
        connects all points of the aerofoil to construct the shape
        """
         #drawing connecting lines
        points=points
        y=0
        for i in range(2):
             for x in range(6):
                 if x+y !=6:
                     start_pos=points[x+y]
                     line_end_1 = [start_pos[0]+5, start_pos[1]+5]
                     end_pos=points[x+y+1]
                     line_end_2 = [end_pos[0]+5, end_pos[1]+5]
                     pygame.draw.line(win, SLDR_CLR_2, line_end_1, line_end_2)
             y=6
             
         #leading edge line
        start_pos=points[0]
        line_end_1 = [start_pos[0]+5, start_pos[1]+5]
        end_pos=points[7]
        line_end_2 = [end_pos[0]+5, end_pos[1]+5]
        pygame.draw.line(win, SLDR_CLR_2, line_end_1, line_end_2)
        
        #trailing edge converging lines
        start_pos=points[6]
        
        line_end_1 = [start_pos[0]+5, start_pos[1]+5]
        end_pos=points[5]
        line_end_2 = [end_pos[0]+5, end_pos[1]+5]
        pygame.draw.line(win, SLDR_CLR_2, line_end_1, line_end_2)
        end_pos=points[12]
        line_end_2 = [end_pos[0]+5, end_pos[1]+5]
        pygame.draw.line(win, SLDR_CLR_2, line_end_1, line_end_2)
        
        pygame.display.update()
        
    def draw_window(self,win,window_num):
        """
        this method first erases the whole aerofoil window (by putting a rectangle over it)
        then draws all sliders/lines from scratch
        which is necessary each time a slider is interacted with
        """
        pygame.draw.rect(win, WINDOW_CLR, self.window)
        #   add slider x&y offset from screen edge - accounting for different window positions
        sldr_y = 50 
        if self.y==545:
            sldr_y=550
        
        
        #   iterate 2 layers of sliders - defining top and bottom of the shape
        
        #differentiate between points1/2/3 as they are stored as separate arrays
        array_name = 'points_{}'.format(window_num)
        points_array = points[array_name]
        
        
        for y in range (2): 
            _sldr_x = 100
            if self.x>=1000:
                _sldr_x=1100
            for x in range(6):                  #   6 is the number of sliders in each layer
                index=x+(7*(y))                 #   calculation converts x,y loop cycle indexes into repsective position in the array
                if self.__initialise==True:     #   if window drawn for the first time, slider objects are instantiated into an array-
                    node = points_array[index]
                    slider = Slider(_sldr_x,sldr_y,node[1])
                    self.slider_array.append(slider)
                else:                           #   -otherwise, their node position is edited inside relevant object instance
                    self.slider_array[index].node_y = points_array[index][1]
                #print("slider array", self.slider_array)
                self.slider_array[index].draw_slider(win)
                pygame.display.update()
                _sldr_x = _sldr_x + 150
                
            if self.__initialise==True and y==0:
                #   add the trailing edge here as a slider even though it appears as a fixed point and can't be changed
                #   it's not drawn on
                ghost_point = points_array[6]
                ghost_slider = Slider(ghost_point[0],ghost_point[1],ghost_point[1])
                self.slider_array.append(ghost_slider)
                
            sldr_y = sldr_y + 250
            
        self.draw_lines(win,points_array)       #!!!!!!      
        pygame.display.update()
        self.__initialise=False
            
    
        
    def update_points(self,x_pos,y_pos,win_num,win): #xpos and ypos are coords of mousebutton down
    
        """
        method decides if user interacted with a slider
        if yes, its coordinates are changed 
        each slider track has a small tolerance on either side of it where the mouse click will be counted 
        """

        array_name = 'points_{}'.format(win_num)
        
        #if user pressed within 20 pixels of the track, the value will snap to the edge of the track
        track_corner_vals = [100,250,400,550,700,850, 
                               1100,1250,1400,1550,1700,1850]
                                
        pressed=False
        for x in range(len(track_corner_vals)):
            #print('xpos ',x_pos)
            #print('corenrval ',track_corner_vals[x])
            if (x_pos-track_corner_vals[x]) <=20 and (x_pos-track_corner_vals[x]) >= -20:   #   tolerance of 20 pixels
                pressed=True
                x_pos= track_corner_vals[x]
                break
        if pressed!=True:
            #print('return')
            return  #   sliders aren't edited if pressed outside the range, the function stops
                
        temp=0     
        if win_num!=1:
            temp=500

        #   get y coordiante of top left corner of the track 
        if y_pos <= 275+temp:
            sldr_y=50+temp
        else:
            sldr_y=300+temp
        
        #   exception handling - limits node height, so it stays on the track
        if sldr_y==50+temp:      #   top row sliders
            if y_pos<=50+temp:
                y_pos=50+temp
            if y_pos>=240+temp:
                y_pos=240+temp
                
        elif sldr_y==300+temp:   #   bottom row sliders
            if y_pos<=300+temp:
                y_pos=300+temp
            elif y_pos>490+temp:
                y_pos=490+temp
        #print('ypos',y_pos)
        #print('xpos',x_pos)
  
        #   find index of the slider pressed and then input new coords into array 
        if win_num==3:          #   sliders on windows 1&2 have the same slider x-coordinates. window 3's is changed here to match
            index=((x_pos+50-1000)//150)-1
        else:
            index=((x_pos+50)//150)-1

        if sldr_y==300+temp:    #   index increments by 7 if item is in the bottom row
            index=index+7
        #print('index', index)
        #print('points',points)
        points[array_name][index]=[x_pos, y_pos]
        print(points[array_name][index])
        self.draw_window(win,win_num)
        
    


 
class GUI:
    """
    this class controls the GUI elements defined by other classes
    it also runs the analysis python file
    and contains the main progrtam loop
    """
    def __init__(self):
    
        self.win=pygame.display.set_mode((2050, 1050))
        self.win.fill(BCKGRND_CLR)
        self.win.set_alpha(None)
        self.__window_array = []
        self.__button_array=[]
        self.__win1=False
        self.__win2=False
        self.__win3=False
        self.__window1_btn = None
        self.__window2_btn = None
        self.__window3_btn = None
        self.menu_active=False
        self.view_status = '-select-'
        self.selected_aerofoil=None
        self.analyse_ops=[]
        self.menu_coords=[]
        
        
    def init_windows(self):
        #   instantiate the dropdown menu buttons for adding aeorfoils 
        window_ops = ['edit new','edit existing file']
        self.__window1_btn = Dropdown(501,262,"+Add Aerofoil", BTN_DIMENSIONS,BTN_CLR_1,window_ops,'q1')
        self.__window1_btn.draw_button(self.win,FONT)
        self.__window2_btn = Dropdown(501,762,"+Add Aerofoil", BTN_DIMENSIONS,BTN_CLR_1,window_ops,'q2')
        self.__window2_btn.draw_button(self.win,FONT)
        self.__window3_btn = Dropdown(1501,762,"+Add Aerofoil", BTN_DIMENSIONS,BTN_CLR_1,window_ops,'q3')
        self.__window3_btn.draw_button(self.win,FONT)
        
        
    def init_buttons(self):
        #   instantiate all other buttons
        
        #   erase top right quadrant of the screen (where all the buttons are)
        window=pygame.Rect(1050, 50, WIN_DIMENSIONS[0],WIN_DIMENSIONS[1])
        pygame.draw.rect(self.win, BCKGRND_CLR, window)
        
        #   instantiate buttons controlling user-defined constants
        AoA_text = Button(1182,102,"Angle of attack range", INPUT_BOX_DIMENSIONS,BCKGRND_CLR)
        AoA_text.draw_button(self.win,FONT_2)
        v_text = Button(1188,272,"Freestream velocity", INPUT_BOX_DIMENSIONS,BCKGRND_CLR)
        v_text.draw_button(self.win,FONT_2)
        rho_text = Button(1188,342,"Freestream density", INPUT_BOX_DIMENSIONS,BCKGRND_CLR)
        rho_text.draw_button(self.win,FONT_2)
        
        AoA_LB = Button(1200,130,str(MIN_AOA), INPUT_BOX_DIMENSIONS,BTN_CLR_1)
        AoA_LB.draw_button(self.win,FONT)
        
        AoA_UB = Button(1200,200,str(MAX_AOA), INPUT_BOX_DIMENSIONS,BTN_CLR_1)
        AoA_UB.draw_button(self.win,FONT)
        
        v_inf = Button(1200,300,str(V_INF), INPUT_BOX_DIMENSIONS,BTN_CLR_1)
        v_inf.draw_button(self.win,FONT)
        
        rho_inf = Button(1200,370,str(RHO_INF), INPUT_BOX_DIMENSIONS,BTN_CLR_1)
        rho_inf.draw_button(self.win,FONT)
            
        
        #   button to run the code from supplemental pythion file
        self.analyse = Dropdown(1430,130,"Run Analysis", (230,80),BTN_CLR_1,self.analyse_ops,'analyse')
        self.analyse.draw_button(self.win,FONT_3)
        
        #   button to select which output to put on screen
        self.select_ops=['Geometry','AoA/lift','AoA/drag','lift/drag']  #   output options
        self.select = Dropdown(1680,130,self.view_status, (170,50),BTN_CLR_1,self.select_ops,'select')
        self.select.draw_button(self.win,FONT)
        
        self.__button_array.extend([AoA_LB,AoA_UB,v_inf,rho_inf])
        
        self.menu_active=False
        
        #print('all buttons drawn')
        
        
    def init_aerofoils(self,pos,name,selection):

        """
        method controls instantiation of aerofoil windows when
        the user presses the button to add new window
        """
        if self.menu_active!=True:
            #   +Add Aerofoil button has been pressed
            if name=='1':
                self.menu_coords=self.__window1_btn.menu_pressed(self.win)
                self.menu_active=True
                quadrant='1'
            elif name=='2':
                self.menu_coords=self.__window2_btn.menu_pressed(self.win)
                self.menu_active=True
                quadrant='2'
            elif name=='3':
                self.menu_coords=self.__window3_btn.menu_pressed(self.win)
                self.menu_active=True
                quadrant='3'
        else:
            #   a selection on the drop-down menu has been made
            if selection =='edit new':
                index="points_{}".format(name)
                print('index',index)
            elif selection=='edit existing file':
                #   user can open a file with their own aerofoil
                try:
                    filename=str(input("enter name of file: "))
                except:
                    print("error: file not found")      #   exception handling
                    return
                with open(filename, mode="r", encoding ="utf-8") as array_file:
                    
                    #   this section reads the text file as a string and converts it into-
                    #   -the needed format like [[x,y],[x,y]]
                    array = array_file.read()
                    array=array.replace(" ", "")
                    array=array.split(",")
                    for x in range(len(array)):
                        array[x]=int(array[x])
                    formatted_data = [[]]
                    for x in range(0, len(array), 2):
                        if (x+1)<len(array):  
                            temp_array=[array[x], array[x+1]]
                            formatted_data.append(temp_array)
                    
                    if len(array)!=13:                  #   exception handling
                        print('array  ',array)
                        print("error: file format isn't compatible")
                        return
                    index_key = 'points_'+name
                    points[index_key]=formatted_data
            else:
                return
            if name=='1':
                self.window_1 = AerofoilWindow(50,45,points[index],self.win)
                self.window_1.draw_window(self.win,name)
                self.__window_array.append(self.window_1)
                self.__win1 = True
                self.analyse_ops.append('1')
                self.menu_active=False
            
            elif name=='2':
                self.__win2 = True
                self.analyse_ops.append('2')
                self.window_2 = AerofoilWindow(50,545,points[index],self.win)
                self.window_2.draw_window(self.win,name)
                self.__window_array.append(self.window_2)
                self.menu_active=False
            
            elif name=='3':
                self.__win3 = True
                self.analyse_ops.append('3')
                self.window_3 = AerofoilWindow(1050,545,points[index],self.win)
                self.window_3.draw_window(self.win,name)
                self.__window_array.append(self.window_3)
                self.menu_active=False
            
            
  
    
    def press_buttons(self,pos):
        """
        method checks position of mouse click
        to decide if a button or dropdown menu was pressed 
        if yes - handles the event
        """
        if self.menu_active!=True:
            if pos[0]>=1199 and pos[0]<=1350:   #   button 1 - 4 was pressed
                y_pts_array = [[130,180],[200,250],[300,350],[370,420]]
                for pt in y_pts_array:
                    if pt[0]<=pos[1]<=pt[1]:
                        # a button has been pressed
                        index=y_pts_array.index(pt)
                        self.__button_array[index].colour=BTN_CLR_2
                        self.__button_array[index].draw_button(self.win,FONT)
                        try:
                            new_value = str(input("enter new value: "))
                            check = float(new_value)
                        except ValueError:                          #   exception handling
                            print("input must be a number")
                        
                        self.__button_array[index].text=new_value
                        self.__button_array[index].colour=BTN_CLR_1
                        self.__button_array[index].draw_button(self.win,FONT)
                    
        
            if (pos[0]>=1430 and pos[0]<=1660):     #   button 5 or 6 was pressed
                if 130<=pos[1]<=210:
                    self.menu_coords=self.analyse.menu_pressed(self.win)
                    #print('1')
                    self.menu_active=True
            elif (pos[0]>=1680 and pos[0]<=1850): 
                if 130<=pos[1]<=210:
                    self.menu_coords=self.select.menu_pressed(self.win)
                    #drop down menu pressed
                    self.menu_active=True
                    
        else:
            print('menu coords',self.menu_coords)

            if self.menu_coords[0]<=pos[0]<=self.menu_coords[2] and self.menu_coords[1]<=pos[1]<=self.menu_coords[3]:
                #   menu option has been selected
                #   checks which menu is active to determine which one was pressed  
                name=None
                if self.analyse.active==True:
                    self.selected_aerofoil=self.analyse.selection_made(pos)
                    self.run_analysis()
                    self.selected_aerofoil=None
                    
                    
                elif self.select.active==True:
                    self.view_status=self.select.selection_made(pos)
                
                elif self.__window1_btn.active==True:
                    selection=self.__window1_btn.selection_made(pos)
                    name='1'
                elif self.__window2_btn.active==True:
                    selection=self.__window2_btn.selection_made(pos)
                    name='2'
                elif self.__window3_btn.active==True:
                    selection=self.__window3_btn.selection_made(pos)
                    name='3'
               

            
                if name!=None:
                    self.init_aerofoils(pos,name,selection)
                else:
                    self.init_buttons()
                
            pygame.display.update()
            
        
    def GUI_interaction(self,pos):
        
        """
        1. determine quadrant of button press. screen is split into 4 quadrants
        2. if quadrant 1 or 2 or 3 see if there's an aerofoil there
            if yes, update_sliders()
            else, check if +AddAerofoil button is pressed
                if yes, instantiate aerofoil
        3. if quadrant 2 was pressed, run press_buttons() to check if a button was pressed
        """
        
        x=pos[0]
        y=pos[1]
        if y<=501 and y>=49:
            if x<=1001 and x>=49:
                quadrant=1
                if self.__win1==False:
                    if pos[0] in range(501,(501+BTN_DIMENSIONS[0])) and pos[1] in range(262,(262+BTN_DIMENSIONS[1])):
                        #button has been pressed
                        self.init_aerofoils(pos,'1',None)  
                else:
                    #print('sliders on 1 pressed')
                    self.window_1.update_points(pos[0],pos[1],quadrant,self.win)
              
                    
            elif x<=2001 and x>=1049:
                quadrant=4  #   top right doesn't contain aerofoil window, so last quadrant
                
                #check if button is pressed in quadrant 4 
                self.press_buttons(pos)
                
                
        elif y<=1001 and y>=549:
            if x<=1001 and x>=49:
                quadrant=2
                if self.__win2==False:
                    if pos[0] in range(501,(501+BTN_DIMENSIONS[0])) and pos[1] in range(762,(762+BTN_DIMENSIONS[1])):
                        #button has been pressed
                        self.init_aerofoils(pos,'2',None)
                else:
                    #print('sliders on 2 pressed')
                    self.window_2.update_points(pos[0],pos[1],quadrant,self.win)
                  
            elif x<=2001 and x>=1049:
                quadrant=3
                if self.__win3==False:
                    if pos[0] in range(1501,(1501+BTN_DIMENSIONS[0])) and pos[1] in range(762,(762+BTN_DIMENSIONS[1])):
                        #button has been pressed
                        self.init_aerofoils(pos,'3',None)
                else:
                    #print('sliders on 3 pressed')
                    self.window_3.update_points(pos[0],pos[1],quadrant,self.win)


    def run_analysis(self):
        if self.view_status=='-select-':    #   exception handling so program doesn't crash
            print("Error: Please select output format before analysis")
            return
        if self.view_status!='Geometry':
            print('analysing...')
            
                
            key = "points_{}".format(self.selected_aerofoil)
            point_list = points[key]
            runfile.runCode(point_list, MIN_AOA, MAX_AOA, V_INF, RHO_INF, self.view_status)
            image = pygame.image.load("aerofoil_analysis_plot.png").convert()
            image = pygame.transform.scale(image, WIN_DIMENSIONS)
            
            #   put image in the respective quadrant
            if self.selected_aerofoil=='1':
                self.win.blit(image, (50, 45))
            if self.selected_aerofoil=='2':
                self.win.blit(image, (50, 545))
            if self.selected_aerofoil=='3':
                self.win.blit(image, (1050, 545))
            pygame.display.update()
            
        else:
            #   select geometry to return to editor window
            if self.__win1==True:
                self.window_1.draw_window(self.win,'1')
            elif self.__win2==True:
                self.window_2.draw_window(self.win,'2')
            elif self.__win3==True:
                self.window_3.draw_window(self.win,'3')
            pygame.display.update()   

    def run(self):
        #   main program loop

        RUNNING=True

        while RUNNING==True:
            events = pygame.event.get()
            for event in events:    
                if event.type == pygame.QUIT:
                    RUNNING=False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos_down = pygame.mouse.get_pos()
                    if self.menu_active==True:
                        self.press_buttons(pos_down)
                        break
                    
                    
                if event.type == pygame.MOUSEBUTTONUP:
                    pos_up = pygame.mouse.get_pos()
                    if self.menu_active!=True:
                        self.GUI_interaction(pos_up)
                    
                    
                    """
                    x_pos=pos_down[0]
                    y_pos=pos_up[1]
                    self.window_1.update_points(x_pos,y_pos,self.win)
                    """
                pygame_widgets.update(event)
                pygame.display.update
        pygame.quit()
    
                            
def runGUI():
    test=GUI()
    test.init_windows()
    test.init_buttons()
    test.run()
    

runGUI()




