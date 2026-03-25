

##### MAIN PROGRAM :: MAKING PROFILE CLASS VER 1.7


import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pygame_widgets
import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import sys


"""GLOBAL CONSTANTS"""   #  all in SI units
V_INF = None         #   freestream velocity
RHO_INF = None     #   freestream density
P_INF =  101000     #   freestream static pressure
"""GLOBAL CONSTANTS"""

"""
pt_array=[[100, 214], [250, 150], [400, 150], [550, 177], [700, 212], [850, 250],[1000,275],
          [100, 316], [250, 375], [400, 340], [550, 319], [700, 310], [850, 306]]    #[1000,275] extrapolated, not from GUI
"""


"""TESTING"""

#   basic test case - flat line goemetry
#pt_array=[[0,0], [1,0], [2,0], [3,0],[4,0],[5,0]]

"""
#   NACA2412 test case
pt_array=[[1.0000,0.0013],[0.9500,0.0114],[0.9000,0.0208],[0.8000,0.0375],
          [0.7000,0.0518],[0.6000,0.0636],[0.5000,0.0724],[0.4000,0.0780],
          [0.2500,0.0767],[0.2000,0.0726],[0.1500,0.0661],[0.1000,0.0563],
          [0.0750,0.0496],[0.0500,0.0413],[0.0250,0.0299],[0.0125,0.0215],
          [0.0000,0.0000],[0.0125,-0.0165],[0.0250,-0.0227],[0.0500,-0.0301],
          [0.0750,-0.0346],[0.1000,-0.0375],[0.1500,-0.0410],[0.2000,-0.0423],
          [0.2500,-0.0422],[0.3000,-0.0412],[0.4000,-0.0380],[0.5000,-0.0334],
          [0.6000,-0.0276],[0.7000,-0.0214],[0.8000,-0.0150],[0.9000,-0.0082],
          [0.9500, -0.0048],[1.0000,-0.0013]]
"""
#custom geometry test case - output from ver 2.2 GUI file
pt_array=[[100, 214], [250, 150], [400, 150], [550, 177], [700, 212], [850, 250],[1000,275],
          [100, 316], [250, 375], [400, 340], [550, 319], [700, 310], [850, 306]]   



class Profile:      #   pass vars to Aerofoil class :: composition
                        
    """
    Profile class contains the methods for performing the vortex panel method.
    New Profile obj is created for each AoA increment
    """
    
    def __init__(self,pt_array, alpha):         
        self.points=pt_array
        self.n = len(self.points)   #   number of panels
        self.alpha = alpha
        self.panel_arr = {}
        self.gamma_matrix=None
        self.q_inf=None
        self.c=None #   chord length
        self.cl=0   #   lift coefficient
        self.cd=0   #   drag coefficient
        self.cp=0   #   pressure coefficient
        
        
    def get_chord_len(self):
        leading_pt = self.points[0]
        trailing_pt = self.points[len(self.points)//2]  #middle value of array
        c = np.sqrt((trailing_pt[0]-leading_pt[0])**2 + (trailing_pt[1]-leading_pt[1])**2)  #pythagoras
        self.c = c
        
    def normalise_coords(self):
        y_min=1050
        #   normalise coordinates to account for pygame's different coordinate system
        for x in range(len(self.points)):
            self.points[x][0] = 1050-self.points[x][0]
            if self.points[x][0]<=y_min:
                y_min=self.points[x][0]
        #   normalise coordinates with respect to the cord length
        x_min = self.points[0][0]
        for x in range(len(self.points)):
            pt = [(self.points[x][0]-x_min)/self.c,(self.points[x][1]-y_min)/self.c]
        
    def make_panels(self):
        
        #   add extra panel - between the first and last points
       
        #   add all other panels
        for x in range(0,self.n-1):
            name = 'panel_{}'.format(x+1)
            pt_1 = self.points[x]
            pt_2 = self.points[x+1]
            
            pan = Panel(pt_1=pt_1, pt_2=pt_2, alpha=self.alpha, name=name)
            pan.calc_params()
            
            self.panel_arr[name] = [pan.pt_1, pan.pt_2, pan.control_pt, pan.n_vector, pan.r, pan.theta, pan.t_vector]     ###  <--- PANEL CONTENTS  ###
        
        #print(self.panel_arr)
            
            
            
    def dynamic_pressure(self):
        q_inf = 0.5 * RHO_INF * (V_INF**2)
        return q_inf
    
    
    def induced_v(self,panel_j, panel_i,j):
        
        j=j     #   panel index
        
        x_c, y_c = panel_i[2][0], panel_i[2][1]
        
        #local panel origin - whatever pt_1 is
        x_0, y_0 = panel_j[0][0], panel_j[0][1]
        theta = panel_j[5]
        sj = panel_j[4]
        
        x_r = x_c - x_0
        y_r = y_c - y_0
        x_dash = (x_r*np.cos(theta))+(y_r*np.sin(theta))
        y_dash = (-x_r*np.sin(theta))+(y_r*np.cos(theta))
        
        
        #   prevent division by 0 error
        try:
            v_x_dash = (1/(2*np.pi))*(
            np.arctan((y_dash)/(x_dash-sj))-np.arctan(y_dash/x_dash))
        except ZeroDivisionError:
            v_x_dash = (1/(2*np.pi))*(
            np.arctan((y_dash)/(1e-8))-np.arctan(y_dash/1e-8))
            
        try:
            v_y_dash = (1/(4*np.pi))*(np.log((x_dash-sj)**2+y_dash**2) - 
                                     np.log(x_dash**2 + y_dash**2))
        except ZeroDivisionError:
            v_y_dash = (1/(4*np.pi))*(np.log((x_dash-sj)**2+y_dash**2) - 
                                     np.log(1e-8))
        #back to global coords
        v_x = v_x_dash * np.cos(theta) - v_y_dash * np.sin(theta)
        v_y = v_x_dash * np.sin(theta) + v_y_dash * np.cos(theta)
        
        
        print(f"Induced velocity for panel {j}: v_x={v_x}, v_y={v_y}")
        return v_x, v_y

    def get_gamma(self):
        
        """
        this method:
        calculates the matrix of influence coefficients A, using panel geometries
        forms the matrices for products of freestream velocity and normal vectors to each panel
        forms matrix for unknown gamma values
        uses the Kutta condition to generate the last row of the linear algebra equation
        so that there is n equations total for n unknown gamma (vortex strength) values
        solves resulting equation to obtain an array of gamma values
        """
        
        #initialise empty matrix nxn size
        A = np.zeros((self.n, self.n))
        A[self.n-1][0] = 1.0            #   kutta condition
        A[self.n-1][self.n-1] = 1.0    #   ensures leading and trailing velocities are equal 
        
        #   COMPUTE MATRIX A
        for i in range (self.n-1):
            
            name_i = 'panel_{}'.format(i+1)
            panel_i = self.panel_arr[name_i]
            #x_c, y_c = panel_i[2][0], panel_i[2][1]
            
            for j in range (1,self.n):
                
                #   make first row of matrix A
                if i==j:
                    A_ij = -0.5     #   special case
                    #print('special case here, i j', i, j)
                else:
                    #   define relative coordinate system
                    name_j = 'panel_{}'.format(j)
                    panel_j = self.panel_arr[name_j]
                    
                    v_x, v_y = self.induced_v(panel_j, panel_i,j)

                    #compute A_ij
                    #theta = panel_j[5]
                    
                    normal_x = panel_i[3][0]
                    normal_y = panel_i[3][1]
                    
                    A_ij = round(v_x * normal_x + v_y * normal_y,5)
                    #print('A_ij= ', A_ij)
                A[i][j]=A_ij
        #print('A=,', A)
        
        #   V_INF x NORMAL ARRAY
        n_v_matrix = []
        for x in range (1,self.n):    #populating normal array/matrix
            name = 'panel_{}'.format(x)
            panel = self.panel_arr[name]
            normal = panel[3]   #   normal vector
            #print('normal for', name, normal)
            scalar_normal = V_INF * (normal[0]*np.cos(self.alpha)+normal[1]*np.sin(self.alpha))
            n_v_matrix.append(scalar_normal)
        n_v_matrix = np.array(n_v_matrix)
        
        n_v_matrix[self.n-1]=0  #??? is this needed???
        
        print('n-v matrix: ', n_v_matrix)
        
        #solve for gamma
        self.gamma_matrix = np.linalg.solve(A, n_v_matrix)
        print("Gamma matrix:", self.gamma_matrix)
        #print('resolved gamma matrix: ', self.gamma_matrix)
        
        
    def VPM_Cl(self):
        
        """
        calculates circulation due to flow vortex at each panel to get cp (pressure coefficient) at that panel
        calculates total circulation - cgamma (capital greek gamma)
        calculates lift per unit span - l_dash
        Cl to go in a database
        """
        
        cp_array=[]
        cl_array=[]
        cd_array=[]
        
        cgamma=0                            #   cgamma = capital gamma = sum of gamma_j*s_j
        for j in range(self.n):
            name_j = 'panel_{}'.format(j)
            panel_j = self.panel_arr[name_j]
            
            ######## CHECK THIS 
            
            # Calculate tangential velocity component
            u_total = V_INF * np.cos(self.alpha)
            v_total = V_INF * np.sin(self.alpha)
            
            # Add induced velocities from all vortices
            for i in range(self.n):
                if i != j:  # Skip self-induced velocity
                    name_i = 'panel_{}'.format(i)
                    panel_i = self.panel_arr[name_i]
                    v_x, v_y = self.induced_v(panel_i, panel_j, i)
                    u_total += self.gamma_matrix[i] * v_x
                    v_total += self.gamma_matrix[i] * v_y
            print('t vector', panel_j[6])
            v_tang = u_total * panel_j[6][0] + v_total * panel_j[6][1]  #   Dot product with tangent vector
            cgamma += self.gamma_matrix[j] * panel_j[4]                 #   add to sum circulation
    
            
        #print('cgamma =',cgamma)
        l_dash = cgamma*V_INF*RHO_INF     #  lift per unit span
        #print('ldash= ', l_dash)
        q_inf = self.dynamic_pressure()
        
        self.cl = l_dash/(q_inf*self.c)
        print('lift coefficient = ', self.cl)
        return self.cl
        
        
    def VPM_Cd(self):
        
        """
        calculates velocity at each panel
        &  pressure coefficient
        to obtain the total force of drag
        --> calculate coefficient of drag (Cd)
        Cd to go into database

        """
        
        
        F_drag = 0      #   total drag force
        q_inf = self.dynamic_pressure()
        
        for j in range(self.n):
            name_j = 'panel_{}'.format(j)
            panel_j = self.panel_arr[name_j]
            j_point = panel_j[2]       
            s_j = panel_j[4]        #    panel length
            theta = panel_j[5]
            u_ij_total = 0
            v_ij_total = 0  
            v_y_total = V_INF * np.cos(self.alpha)
            v_x_total = V_INF * np.sin(self.alpha)
                            #   x_j, y_j are j panel's ctrl point coords
            for i in range(len(self.panel_arr)):
                i_gamma = self.gamma_matrix[i]          #    strength of panel j
                name_i = 'panel_{}'.format(i)
                panel = self.panel_arr[name_i]
                i_point = panel[2]                      #   ctrl point on panel i = source of vortex
                delta_x = j_point[0] - i_point[0]
                delta_y = j_point[1] - i_point[1]
                r_2 = delta_x**2 + delta_y**2           #   r^2 = distance between i and j points squares
                
                try:
                    u_ij = -delta_y / (2 * np.pi * r_2)
                except ZeroDivisionError:
                    u_ij = -delta_y / 1e-8
                try:
                    v_ij = delta_x / (2 * np.pi * r_2)
                except ZeroDivisionError:
                    v_ij = delta_x / 1e-8
                    
                u_ij_total = u_ij_total + (i_gamma*u_ij)
                v_ij_total = v_ij_total + (i_gamma*v_ij)
                
            #   vertical and horizontal velocity components calculated separately
            u_ij_total = u_ij_total + (V_INF*np.cos(self.alpha))
            v_ij_total = v_ij_total + (V_INF*np.sin(self.alpha))

            v_j = np.sqrt((u_ij_total)**2 + (v_ij_total)**2)        #   velocity at panel j (tangential, as normal assumed 0)
    
            C_p = 1 - (v_j / V_INF)**2
            theta = panel[5]        #   theta at panel j
            
           
            F_d_j = q_inf * C_p * s_j * np.cos(theta)               #   drag force at control point of panel j
            F_drag = F_drag + F_d_j
                
            
          
        self.cd = F_drag/(q_inf*self.c)
        print("drag coefficient = ", self.cd)
        return self.cd
        
        
    
    def pressure_dist(self):
        
        """
        finds velocity at control point of each panel
        from that finds pressure coefficient at cp of each panel
        adds Cp to the array which will go in a database?
        """
        
        
        #Draw pressure distribution from cp array
    
"""◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾"""  
    
class Panel:
    
    """
    v_inf = freestream velocity
    """
    
    def __init__(self, pt_1, pt_2,alpha,name):
        #print('done,', name)
        self.name=name
        self.pt_1=pt_1
        self.pt_2=pt_2
        self.control_pt = None
        self.gamma=0   #   vortex strength
        self.t_vector=None
        self.n_vector=None
        self.alpha=np.radians(alpha)    #   angle of attack
        self.theta = (np.arctan2((pt_2[1]-pt_1[1]), (pt_2[0]-pt_1[0])))-self.alpha  #   angle between panel and horizontal
        #   r - length of panel
        self.r=np.sqrt((pt_2[0]-pt_1[0])*(pt_2[0]-pt_1[0])+(pt_2[1]-pt_1[1])*(pt_2[1]-pt_1[1]))
        
        self.phi=0      #   velocity potential
        self.psi=0      #   stream function
        self.lmda=0     #   lambda - mass flow rate per unit length  
        
        
    def calc_params(self):
        
        """
        determine   centre point,
                    angle with neutral chord line (x-axis),
                    tangential vector
                    normal vector
        """
        #centre point
        self.control_pt = [(self.pt_2[0]+self.pt_1[0])/2,
                           (self.pt_2[1]+self.pt_1[1])/2]
        
        dx = self.pt_2[0] - self.pt_1[0]
        dy = self.pt_2[1] - self.pt_1[1]
        self.t_vector = np.array([dx, dy])/self.r    #  tangenttial vector
        
        self.n_vector = np.array([-dy, dx])/self.r   #  normal vector
        
        
    def calc_functions(self):
        
        """
        calculate [velocity potential function]  
                &  [stream function]
        for 3 types of flow
        """
        #####
        """
        #   UNIFORM FLOW
        phi_u = self.v_inf * self.r * np.cos(self.alpha)
        psi_u = self.v_inf * self.r * np.sin(self.alpha)
        
        #    SOURCE/SINK FLOW
        
        # CALCULATE BIG LAMBDA - MASS FLOW RATE PER UNIT LENGT
        
        phi_s = (self.lmda/(2*np.pi))*(np.log(self.r))
        psi_s = (self.lmda/(2*np.pi))*self.theta
        
        #   VORTEX FLOW
        phi_v = -(self.gamma/(2*np.pi))*self.theta
        psi_v = (self.gamma/(2*np.pi))*np.log(self.r)
        
        #   SUPERPOSITION OF FLOWS
        phi = phi_u + phi_s + phi_v
        psi = psi_u + psi_s + psi_v
        
        # input into database
        """

"""◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾◾"""  


class Aerofoil:   #   access methods from Profile class
              
    """
    contains all info relating to an aerofoil
    defines panels
    Outputs relevant info to the GUI class
    """
    

    def __init__(self,points,min_alpha,max_alpha):
        self._geometry=points                           #   points defining the airfoil
        self.chord_len=0                                #   distance from leading edge to trailing edge
        self.num_panels= len(self._geometry)-1          #   number of panels
        self.alpha=0                                    #   current angle of attack
        self.min_alpha=min_alpha                        #   lower bound of AoA range
        self.max_alpha=max_alpha                        #   upper bound of AoA range
        self.data_table=[]                              #   table of AoA & cl & cd values

    
    def setup_panels(self):
        temp=0
        """insert front panel here"""
        new_panel=Panel(self._geometry[6], self._geometry[0])
        self.panel_array.append(new_panel)
        
        for y in range(2):
            for x in range ((len(self._geometry)-2)/2):
                new_panel=Panel(self._geometry[x+temp], self._geometry[x+1+temp])
                self.panel_array.append(new_panel)
                
            if temp==0:
                """ trailing edge panels """
                new_panel=Panel(self._geometry[5], self._geometry[1000,300])
                self.panel_array.append(new_panel)
                new_panel=Panel(self._geometry[1000,300], self._geometry[11])
                self.panel_array.append(new_panel)
            temp=6
        
        
    def analysis(self):
        
        """
        executes VPM for the range of Alpha values (currently manually set o 0-15)
        """
        
        self.alpha=self.min_alpha
        for x in range (self.max_alpha-self.min_alpha):
            data = []
            data.append(x)
            prof=Profile(pt_array,self.alpha) 
            prof.get_chord_len()
            prof.normalise_coords()
            prof.make_panels()    
            prof.get_gamma()
            cl=round(prof.VPM_Cl(),3)
            cd=round(prof.VPM_Cd(),3)
            
            data.append(cl)
            data.append(cd)
            
            self.alpha=self.alpha+1
            
            self.data_table.append(data)
            print('alpha=', self.alpha)
            print('data=', data)
            
        print('table', self.data_table)
        print("Output table: ")
        for item in self.data_table:
            print(item)
        
        
    def make_graph(self,view_status):
        if view_status == 'AoA/lift':
            pass
        elif view_status == 'AoA/drag':
            pass
        elif view_status == 'lift/drag':
            pass
        else:
            print("error: view_status doesn't exist")
        
        #cd against AoA array
        data = np.array(self.data_table)
        num_rows = len(data)
        x = data[:,0]   #   first column only - all alpha values
        #print('x',x)
        y_lift = data[:,1]   #   2nd column - all cl values
        #print('y',y_lift)
        y_drag = data[:,2]   #   3rd column - all cd values
        
        fig = plt.figure()
        axis1 = fig.add_subplot(1,2,1)
        axis2 = fig.add_subplot(1,2,2)
        #axis3 = fig.add_subplot(1,2,2)
        
        axis1.plot(y_lift)
        #axis1.set_title("AoA vs Cl")
        
        axis2.plot(y_drag)
        #axis[1].set_title("AoA vs Cd")
        
        #axis3.plot(y_drag,y_lift)
        #axis[2].set_title("Cd vs Cl")
        
        plt.show()
        
        #cd (x-axis) vs cl (y-axis)
            
            
          
def runCode(pt_array,min_aoa,max_aoa,v_inf,rho_inf,VIEW_STATUS):
    pt_array = pt_array
    # variable have to be declared global here as they are passed from outside the python file
    # othersise they would be declared at the start of the script
    global     min_alpha, max_alpha
    min_alpha, max_alpha = min_aoa, max_aoa
    global     V_INF,RHO_INF
    V_INF,RHO_INF = v_inf,rho_inf
    
    A = Aerofoil(pt_array,min_alpha, max_alpha)    
    A.analysis()   
    A.make_graph(VIEW_STATUS)     
    

runCode(pt_array,0,15,5,1.225,'AoA/lift')

