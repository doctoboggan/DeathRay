"a sample system using general_optics.py to model a 10 Joule Nd:Glass CPA laser system"
_rcsid="$Id: general_optics_example.py 323 2011-04-06 19:10:03Z marcus $"

from math import *
import math
import Numeric
import types
import traceback

import general_optics 
from general_optics import composite_optic, grating, lens, reflector, null_optic, beam, qtens, Infinity, euler, trace_path, vec_mag
from general_optics import phase_plate, halfwave_plate, faraday_rotator

import copy

import abcd_optics

class spitfire:
	optics=abcd_optics
	mm=1e-3
	inch=25.4*mm
	lambda0=1.054e-6
	spitfire_thermal=optics.lens(500.0*mm) #unsubstantiated guess
	spitfire_abcd=(optics. mirror(1000.0*mm)*optics.space(19.0*inch)*optics.mirror(500.0*mm)*optics.space(9.5*inch)*spitfire_thermal*
			optics.space(9.5*inch)*optics.mirror(500.0*mm)* optics.space(19.0*inch)*optics.mirror(1000.0*mm)*
			optics.space(19.0*inch)*optics.mirror(500.0*mm)*optics.space(9.5*inch)*spitfire_thermal*optics.space(9.5*inch)*
			optics.mirror(500.0*mm)*optics.space(19.0*inch) )
	
	resonator=optics.abcd_resonator(spitfire_abcd, lambda0)
	exit_window=resonator.qw(optics.space(900.0*mm))	
	q0=exit_window.q	


clight=299792458. #m/sec
deg=pi/180.0
inch = 0.0254

import graphite

show_qd=0 #quickdraw graphics works on Macintosh only
show_pdf=1 #output nice pdf from graphite

def draw_layout(graph, optics):
	if optics is None:
		return
	
	colorline = graphite.PointPlot()
	colorline.lineStyle = graphite.LineStyle(width=1, color=graphite.orange, kind=graphite.SOLID)
	colorline.symbol = None
	for i in optics.keys():
		olist=optics[i].polygon_list()
		for o in olist:
			if o is not None:
				d=graphite.Dataset()
				d.x=o[:,2]
				d.y=o[:,0]
				d.z=o[:,1]
				#set coordinates to z=+right, x=+up, y=+out of paper
				graph.datasets.append(d)
				graph.formats.append(colorline)

def draw_trace(graph, optics_trace):
	if optics_trace is None:
		return
		
	colorline = graphite.PointPlot()
	if optics_trace.color is None:
		color=graphite.black
	else:
		color=optics_trace.color
	
	colorline.lineStyle = graphite.LineStyle(width=1, color=color, kind=graphite.SOLID)
	colorline.symbol = None

	count=len(optics_trace)
	coords=Numeric.zeros((count,3), Numeric.Float)
	for i in range(count):
		xy=optics_trace[i].x0
		coords[i]=(xy[2],xy[0], xy[1]) #z is horizontal, x is vertical!
	
	graph.datasets.append(graphite.Dataset(coords))
	graph.formats.append(colorline)

def draw_everything(optics, trace, xrange, yrange, three_d=None):
	
	g=graphite.Graph()
	g.top=10
	g.left=100
	g.right=g.left+700
	g.bottom=g.top+300
	g.axes[graphite.X].range=xrange
	g.axes[graphite.Y].range=yrange
	g.formats=[]
	if three_d:
		g.axes[graphite.Z].range=(-0.5, 0.5)
		g.lookAt=(-.25,-1.0,0)
		g.eyePosition=(-.75,-2,0.25)
		
	draw_layout(g, optics)
	draw_trace(g, trace)
	
	g.axes[graphite.Y].tickMarks[0].labels = "%+.1f"
	g.axes[graphite.Y].label.text = "meters"
	g.axes[graphite.Y].tickMarks[0].inextent= 0.02
	g.axes[graphite.Y].tickMarks[0].labelStyle=graphite.TextStyle(hjust=graphite.RIGHT, vjust=graphite.CENTER, 
		font=graphite.Font(10,0,0,0,None), 
		color=graphite.Color(0.00,0.00,0.00))
	g.axes[graphite.Y].tickMarks[0].labeldist=-0.01

	g.axes[graphite.X].tickMarks[0].labels = "%+.1f"
	g.axes[graphite.X].label.text = "meters"
	g.axes[graphite.X].tickMarks[0].inextent= 0.02
	g.axes[graphite.X].tickMarks[0].labelStyle=graphite.TextStyle(hjust=graphite.CENTER, vjust=graphite.TOP, 
		font=graphite.Font(10,0,0,0,None), 
		color=graphite.Color(0.00,0.00,0.00))
	g.axes[graphite.X].tickMarks[0].labeldist=-0.01
	
	return g
	
class mir(reflector):
	"a one inch mirror"
	def post_init(self):
		self.width=0.0254
		self.thickness=0.005
		reflector.post_init(self)

class serrated_aperture(null_optic):
	pass

class plain_aperture(null_optic):
	pass

class alignment_aperture(null_optic):
	pass
		
class laser_head(null_optic):
	"an optic with both an inner box (rod) and outer box (case)"
	def inner_polygon(self):
		savew, savet = self.width, self.thickness
		self.width=self.rodsize
		self.thickness=self.thickness*0.75
		try:
			p=self.polygon()
		finally:
			self.width=savew
			self.thickness=savet
		return p
	def polygon_list(self):
		return [self.polygon(), self.inner_polygon()]

class PL_brewster_filter(reflector):
	def post_init(self):
		self.width=5.0*inch
		self.height=2.0*inch
		self.thickness=0.125*inch
		self.brewster_angle=56.0
		if not self.__dict__.has_key("transmit"):
			self.transmit=0
		if not self.__dict__.has_key("reversed"):
			self.eta=0
		else:
			self.eta=180
			
	def outer_polygon(self):
		savew, savet = self.width, self.thickness
		self.width=4*inch
		self.thickness=6*inch
		myrot=general_optics.eulermat(-self.brewster_angle,self.eta,0)
		self.rotate_in_local_frame(myrot)
		try:
			p=self.polygon()
		finally:
			self.width=savew
			self.thickness=savet
			self.rotate_in_local_frame(Numeric.transpose(myrot))
		return p
	
	def local_transform(self):
		if not self.transmit:
			reflector.local_transform(self)

	def q_transform(self):
		if not self.transmit:
			reflector.q_transform(self)

	def place_between(self, from_obj, to_obj, distance):
		reflector.place_between(self, from_obj, to_obj, distance)
		self.rotate_in_local_frame(general_optics.eulermat(self.brewster_angle,0,0))
		return self
	
	def rotate_axis(self, axis_theta): #must undo screwy angles for this object before rotating
		self.rotate_in_local_frame(general_optics.eulermat(-self.brewster_angle,0,0))
		self.rotate_in_local_frame(general_optics.eulermat(0,0,axis_theta))
		self.rotate_in_local_frame(general_optics.eulermat(self.brewster_angle,0,0))
		return self
		
	def polygon_list(self):
		return [self.polygon(), self.outer_polygon()]
	
class vacuum_spatial_filter(null_optic):
	"an optic with both an inner box (aperture) and outer box (tube)"
	def inner_polygon(self):
		savew, savet = self.width, self.thickness
		self.thickness=0.01
		try:
			p=self.polygon()
		finally:
			self.width=savew
			self.thickness=savet
		return p
	def polygon_list(self):
		return [self.polygon(), self.inner_polygon()]
						
class blue_through_ylf(composite_optic):
	#assign reasonably arbitrary keys to each optic for future reference.  
	#The values are unique within this optic
	
	UVM1, UVM2, UVM3, UVM4, UVM5, UVM6, UVM7, UVM8, UVM9, UVM10, UVM11, UVM12= range(12)
	PS1u, PS1d='ps1u', 'ps1d'
	UVL1, UVL2, DEMAG1, DEMAG2=range(20,24)
	YLF_SPLIT='ylf_split'
	SERR='serr'
	FILTER='filt'
	
	def __init__(self, **extras):
		inch=0.0254
		entrance_y=5.0*inch
		y0=2.5*inch #height of main line off table)
		my=blue_through_ylf
		optics={}
		
		#first, list all mirrors, and point them at each other
		optics[my.UVM1]=mir("UVM1", (13*inch, entrance_y, 7.5*inch))
		optics[my.UVM2]=mir("UVM2", (7.5*inch, entrance_y, 7.5*inch))
		optics[my.PS1u]=mir("Blue Peri 1 upper", (8*inch, entrance_y, 37*inch))
		optics[my.PS1d]=mir("Blue Peri 1 lower", (8*inch, y0, 37*inch))
		optics[my.UVM3]=mir("UVM3", (36*inch, y0, 38*inch))
		optics[my.UVM4]=mir("UVM4", (36*inch, y0, 137.5*inch))
		optics[my.UVM5]=mir("UVM5", (43.5*inch, y0, 49.5*inch))
		optics[my.UVM6]=mir("UVM6", (46.5*inch, y0, 137.5*inch))
		optics[my.UVM7]=mir("UVM7", (38*inch, y0, 38*inch))
		optics[my.UVM8]=mir("UVM8", (41.5*inch, y0, 136*inch))
		optics[my.UVM9]=mir("UVM9", (53*inch, y0, 136*inch))
		optics[my.UVM10]=mir("UVM10", (53*inch, y0, 41*inch))
		optics[my.UVM11]=mir("UVM11", (48*inch, y0, 41*inch))
		optics[my.UVM12]=mir("YLF retro", (48*inch, y0,80.5*inch))
		optics[my.YLF_SPLIT]=mir("YLF exit splitter", (48*inch, y0, 47.8*inch))
		
		optics[my.UVL1]=lens("UVL1", f=+0.75).place_between(optics[my.UVM3], optics[my.UVM4], 4.0*inch)
		optics[my.UVL2]=lens("UVL2", f=+1.00).place_between(optics[my.UVL1], optics[my.UVM4], 83*inch-0.0*inch)
				
		optics[my.DEMAG1]=lens("UVL3", f=+0.75).place_between(optics[my.UVM9], optics[my.UVM10], 23.0*inch)
		optics[my.DEMAG2]=lens("UVL4", f=+1.00).place_between(optics[my.DEMAG1], optics[my.UVM10], 1.7+5.0*inch)

		optics[my.SERR]=null_optic("Serr. Aperture", width=1.0*inch, thickness=0.1*inch).place_between(optics[my.DEMAG1], optics[my.DEMAG2], 3*inch)
		optics[my.FILTER]=null_optic("Filter Aperture", width=1.0*inch, thickness=0.1*inch).place_between(optics[my.DEMAG1], optics[my.DEMAG2], 0.75)
		
		looks=[my.UVM1, my.UVM2, my.PS1u, my.PS1d, my.UVM3, my.UVM4, my.UVM5, my.UVM6, my.UVM7,
			my.UVM8, my.UVM9, my.UVM10, my.UVM11, my.UVM12, my.YLF_SPLIT]
		#align all mirrors
		for i in range(1, len(looks)-1):
			optics[looks[i]].set_direction(optics[looks[i-1]], optics[looks[i+1]])

		order=[my.UVM1, my.UVM2, my.PS1u, my.PS1d, my.UVM3, my.UVL1, my.UVL2, my.UVM4, my.UVM5, my.UVM6, my.UVM7,
			my.UVM8, my.UVM9, my.DEMAG1, my.SERR, my.FILTER, my.DEMAG2, my.UVM10, my.UVM11, my.UVM12, my.YLF_SPLIT]
		
		#specify center and reference as (0,0,0) to make our coordinates absolute
		composite_optic.init(self, "blue line", optics, order, (0,0,0), (0,0,0), 0, extras=extras )
		
class ir_line(composite_optic):
	M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M15= range(15)
	L1, L2, L3, L4, L5, L6, L7, L8, L7a=range(20,29)
	VSF1, VSF2, VSF3=range(30,33)
	SERR1='Serr1'
	SF1='SF1'
	FR12, FR25 = 'fr12', 'fr25'
	A1, A2, A3, A4, A5 = range(40,45)
	G9a, G9b, G25a, G25b, G50 = range(50,55)
	TrM1, TrM2, TrM3, TrM4 = range(60,64)
	BP2, BP3, BP4 = range(70,73)	
	QR1, QR2, QR3, QR4 =range(80,84)
	EXIT='exit'
		
	def __init__(self, **extras):
		inch=0.0254
		entrance_y=5.0*inch
		exit_y=13.5*inch
		my=ir_line
		optics={}
		
		#first, list all mirrors, and point them at each other
		optics[my.M1]=mir("M1", (2*inch, entrance_y, 10*inch))
		optics[my.M2]=mir("M2", (4*inch, entrance_y, 10*inch))
		optics[my.TrM1]=mir("TrM1", (4*inch, entrance_y, 96*inch))
		optics[my.TrM2]=mir("TrM2", (6*inch, entrance_y, 96*inch))
		optics[my.TrM3]=mir("TrM3", (6*inch, entrance_y, 82.5*inch))
		optics[my.TrM4]=mir("TrM4", (2*inch, entrance_y, 82.5*inch))
		optics[my.M3]=mir("M3", (4*inch, entrance_y, 135*inch))
		optics[my.M4]=mir("M4", (12*inch, entrance_y, 135*inch))
		optics[my.M5]=mir("M5", (13*inch, entrance_y, 105*inch))
		optics[my.M6]=mir("M6", (14*inch, entrance_y, 105*inch))
		optics[my.M7]=mir("M7", (16.5*inch, entrance_y, 3*inch))
		optics[my.M8]=mir("M8", (24*inch, entrance_y, 3*inch))
		optics[my.M9]=mir("M9", (23*inch, entrance_y, 135*inch))
		optics[my.M10]=mir("M10", (33*inch, entrance_y, 134.5*inch))
		optics[my.M11]=mir("M11", (33*inch, entrance_y, -6*inch))
		optics[my.BP4]=PL_brewster_filter("BP4", (33*inch, entrance_y, 27*inch), reversed=1)
		optics[my.M12]=mir("M12", (20*inch, entrance_y, 33*inch))
		optics[my.M13]=mir("M13", (20*inch, entrance_y, 12*inch))
		optics[my.M14]=mir("M14", (8.5*inch, entrance_y, 11.5*inch))
		optics[my.M15]=mir("M15", (8.5*inch, exit_y, 11.5*inch))
		
		optics[my.EXIT]=sys_exit=null_optic("exit", (10.0*inch, exit_y, 142.0*inch))
				
		optics[my.L1]=lens("L1", f=+0.400).place_between(optics[my.M2], optics[my.TrM1], 12.0*inch)
		optics[my.L2]=lens("L2", f=+0.800).place_between(optics[my.L1], optics[my.TrM1], 1.30)
		optics[my.L3]=lens("L3", f=+0.750).place_between(optics[my.M6], optics[my.M7], 10*inch)
		optics[my.L4]=lens("L4", f=+1.500).place_between(optics[my.L3], optics[my.M7], 2.25)
		optics[my.L5]=lens("L5", f=+0.750).place_between(optics[my.M10], optics[my.M11], 5*inch)
		optics[my.L6]=lens("L6", f=+1.500).place_between(optics[my.L5], optics[my.M11], 95.5*inch)
		optics[my.L7]=lens("L7", f=+0.750).place_between(optics[my.M15], sys_exit, 4.5*inch)
		optics[my.L8]=lens("L8", f=+2.500, width=6*inch, thickness=0.25*inch).\
			place_between(optics[my.M15], sys_exit, -1*inch).tilt_off_axis((0,45,0))
		
		optics[my.G9a]=laser_head("9mm-1", width=2.0*inch, thickness=6.0*inch, rodsize=0.009).\
			place_between(optics[my.M4], optics[my.M5], 9*inch)
		optics[my.G9b]=laser_head("9mm-2", width=2.0*inch, thickness=6.0*inch, rodsize=0.009).\
			place_between(optics[my.M4], optics[my.M5], 23*inch)
		
		optics[my.G25a]=laser_head("25mm-1", width=6.0*inch, thickness=12.0*inch, rodsize=0.025).\
			place_between(optics[my.M8], optics[my.M9], 74*inch)
		optics[my.G25b]=laser_head("25mm-2", width=6.0*inch, thickness=12.0*inch, rodsize=0.025).\
			place_between(optics[my.M8], optics[my.M9], 94*inch)

		optics[my.G50]=laser_head("50mm", width=9.0*inch, thickness=15.0*inch, rodsize=0.050).\
			place_between(optics[my.M10], optics[my.M11], -19*inch)

		optics[my.SERR1]=serrated_aperture("serrated aperture", diameter=0.003).\
			place_between(optics[my.M2], optics[my.TrM1], 10*inch)		
		optics[my.SF1]=plain_aperture("spatial filter 1", diameter=0.001).\
			place_between(optics[my.M2], optics[my.TrM1], 35*inch)
		
		optics[my.QR1]=halfwave_plate("QR1", width=1*inch, thickness=0.5*inch).\
			place_between(optics[my.G9a], optics[my.G9b], 8*inch).rotate_axis(22.5)	
		optics[my.FR12]=faraday_rotator("FR12", width=0.5*inch, thickness=6*inch, rotation=45).\
			place_between(optics[my.M6], optics[my.M7], 5*inch)
		optics[my.VSF1]=vacuum_spatial_filter("VSF1", thickness=24*inch, width=2*inch).\
			place_between(optics[my.L3], optics[my.L4], 0.750)
			
		optics[my.QR2]=halfwave_plate("QR2", width=1*inch, thickness=0.5*inch).\
			place_between(optics[my.G25a], optics[my.G25b], 8*inch).rotate_axis(22.5)	

		optics[my.BP2]=PL_brewster_filter("BP2", transmit=1).\
			place_between(optics[my.G25b], optics[my.M9], 13*inch).rotate_axis(90)
		optics[my.QR3]=halfwave_plate("QR3", width=1*inch, thickness=0.5*inch).\
			place_between(optics[my.G25b], optics[my.M9], 19*inch).rotate_axis(22.5)	
		optics[my.FR25]=faraday_rotator("FR25", width=1.0*inch, thickness=6.0*inch, rotation=45).\
			place_between(optics[my.G25b], optics[my.M9], 23*inch)
		optics[my.BP3]=PL_brewster_filter("BP3", transmit=1).\
			place_between(optics[my.G25b], optics[my.M9], 30*inch).rotate_axis(0)
		
		looks=[my.M1, my.M2, my.TrM1, my.TrM2, my.TrM3, my.TrM4, my.M3, my.M4, my.M5,
			my.M6, my.M7, my.M8, my.M9, 
			my.M10, my.M11, my.BP4, my.M12, my.M13, my.M14, my.M15, my.EXIT]
		#align all mirrors
		for i in range(1, len(looks)-1):
			optics[looks[i]].set_direction(optics[looks[i-1]], optics[looks[i+1]])

		order=[my.M1, my.M2, my.SERR1, my.L1, my.SF1, my.L2, my.TrM1, my.TrM2, my.TrM3, my.TrM4, my.M3, my.M4, my.G9a, 
			my.QR1, my.G9b, my.M5,
			my.M6, my.FR12, my.L3, my.VSF1, my.L4, my.M7, my.M8, my.G25a, my.QR2, my.G25b, 
			my.BP2, my.QR3, my.FR25, my.BP3, 
			my.M9, my.M10, my.L5, my.L6, my.G50, my.M11, my.BP4, my.M12, 
			my.M13, my.M14, my.M15, my.L7, my.L8]
		
		#specify center and reference as (0,0,0) to make our coordinates absolute
		composite_optic.init(self, "IR line", optics, order, (0,0,0), (0,0,0), 0, extras=extras )

class ir_compressor(composite_optic):
	INPUT='M1'
	OUTPUT='M2'
	FOCUS='L1'
	G1="grating 1"
	G2="grating 2"
	VR1='vert_retro_1'
	VR2='vert_retro_2'
	START='bc.start'
	END='bc.end'
				
	def __init__(self, theta1=61.486, clen=1.02, lambda0=1.054e-6, center=(0,0,0), angle=0, **extras):
		self.init(theta1, clen, lambda0, center, angle, extras)
		
	def init(self, theta1, clen, lambda0, center, angle, extras):
		my=ir_compressor
		input_height=18*inch
		output_height=12*inch
		center_height=(input_height+output_height)/2.0
		
		basebeam=beam((0,input_height,-1.0), qtens(lambda0, w=0.005, r=Infinity))		
		optics={}
					
		optics[my.INPUT]=m1=reflector("input mirror", center=(0, input_height, 0), width=8*inch, angle=-45)
		
		optics[my.G1]=g1=grating("g1", angle=theta1+90, center=(52*inch,center_height, 0), 
				pitch=1740e3, order=1, width=16*inch, thickness=2.0*inch)
		mybeam=basebeam.clone()
		m1.transport_to_here(mybeam)
		m1.transform(mybeam)	
		g1.transport_to_here(mybeam)
		g1.transform(mybeam)
		mybeam.free_drift(clen) #this is where grating 2 should be
		optics[my.G2]=g2=grating("g2", angle=theta1-90, center=mybeam.x0+(0,0,1e-8), 
				pitch=1740e3, order=1, width=16*inch, thickness=2.0*inch)
		
		optics[my.VR1]=reflector("retro", center=(40*inch, center_height, g2.center[2]),  angle=90.0, width=8*inch, thickness=1.0*inch)
		
		out=optics[my.OUTPUT]=reflector("output mirror", center=(8*inch, output_height, 0.0), 
				width=8.0*inch, thickness=1.0*inch)
		focus=optics[my.FOCUS]=lens("output focus", center=out.center+(35*inch, 0, 7*inch), 
				angle=90-math.atan(0.2)/deg, f=2.0, width=8.0*inch, 
				height=8.0*inch, thickness=1.0*inch).tilt_off_axis(0)
		out.set_direction(g1.center-(0, center_height-output_height, 0), focus)
		
		comp_order=(my.INPUT, my.G1, my.G2, my.VR1, my.G2, my.G1, my.OUTPUT, my.FOCUS)
		
		composite_optic.init(self, "ir compressor", optics, comp_order, None, center=center, angle=0, extras=extras )		

		#prepare to handle to downslope in the beam through the compressor while we are still
		#not rotated to the funny beam axis
		m1label=self.mark_label(my.INPUT)
		g1label=self.mark_label(my.G1)
		m2label=self.mark_label(my.OUTPUT)
		ir_trace=trace_path(self, basebeam.clone())
		path_len=(ir_trace[(m2label,0)].total_drift-ir_trace[(m1label,0)].total_drift)
		slope=(output_height-input_height)/path_len
		
		#distance from entrance to first g1 hit
		g1_first_distance=(ir_trace[(g1label,0)].total_drift-ir_trace[(m1label,0)].total_drift) 
		#distance from entrance to second g1 hit
		g1_second_distance=(ir_trace[(g1label,1)].total_drift-ir_trace[(m1label,0)].total_drift) 
		
		#now, rotate us to the real beam direction
		self.update_coordinates(self.center, self.center, general_optics.eulermat(angle, 0, 0))	
		
		#and set up the aiming points
		self.g1target1=g1.center+(0, (input_height-center_height)+g1_first_distance*slope, 0)		
		self.g1target2=g1.center+(0, (input_height-center_height)+g1_second_distance*slope, 0)	
		out.set_direction(self.g1target2, focus)

	def set_entrance_direction(self, look_to):
		my=ir_compressor
		self.optics_dict[my.INPUT].set_direction(look_to, self.g1target1)
		
class blue_compressor(composite_optic):
	IR1="bc.ir1"
	IR2="bc.ir2"
	OR1="bc.or1"
	GRATE="bc.grating"
	VR1='bc.vert_retro_1'
	VR2='vbc.ert_retro_2'
	IPERI1='bc.ip1'
	IPERI2='bc.ip2'
	EXP1='bc.exp1'
	EXP2='bc.exp2'
	OPERI1='bc.op1'
	OPERI2='bc.op2'
	TM1='bc.turn1'
	TM2='bc.turn2'
	DEMAG1='bc.dmg1'
	DEMAG2='bc.dmg2'
	START='bc.start'
	END='bc.end'
	y_offset=0.5*inch
		
	def setup_retro_standard(self, beam, vertex_distance, retro_beam_offset, retro_err, y_center):
		"""setup_retro_standard(diffracted_beam, vertex_distance, grating_beta, grating_spot_offset, retro_err) ->
		(retro_mirror_1, retro_mirror_2)"""
		my=blue_compressor
		c,s = beam.direction()[2], beam.direction()[0]
		vz, vx = c*vertex_distance, s*vertex_distance
		vz, vx = vz - s*retro_beam_offset, vx + c*retro_beam_offset
		beam_angle=math.atan2(s,c)/deg
		ir1=reflector(my.IR1, angle=(beam_angle-45-retro_err/2), center=(vx,y_center,vz), justify="left", width=0.05)
		ir2=reflector(my.IR2, angle=(beam_angle+45+retro_err/2), center=(vx,y_center,vz), justify="right", width=0.05)
		#print beam_angle, ir1,ir2
		return ir1, ir2
	
	def setup_reflectors_blue(self, basebeam, theta1, clen, grating_spot_offset, pitch=1.5e6, lam0=1.053e-6, inside_retro_err=0, zeta=0):
		my=blue_compressor
		y_offset=my.y_offset
		grate=grating(my.GRATE, angle=theta1, center=(0,y_offset/2, 0), pitch=pitch, order=1, justify=-.8, height=0.05, width=0.1)
		littrow, beta=grate.degree_angles(theta1, lam0)
		vertex_dist=(clen-grating_spot_offset*sin(beta*deg))*0.5
		retro_beam_offset=grating_spot_offset*math.cos(beta*deg)*0.5
		beam=basebeam.clone().set_lambda(lam0)
		grate.transport_to_here(beam)
		grate.transform(beam)
		return_x=-grating_spot_offset*math.cos(theta1*deg)
		vretvertex=Numeric.array((return_x, y_offset/2, -0.22))
		yvec=Numeric.array((0.,y_offset,0.))
		ir1, ir2 = self.setup_retro_standard(beam, vertex_dist, retro_beam_offset, inside_retro_err, y_offset/2)
		vr1=reflector('vert retro 1', angle=0, center=vretvertex-yvec/2, width=0.025, height=0.05, thickness=0.01)
		vr2=reflector('vert retro 2', angle=0, center=vretvertex+yvec/2, width=0.025, height=0.05)
		vr1.set_direction((return_x,0,0), vr2)
		vr2.set_direction(vr1, (return_x, y_offset, 0))
		return {my.GRATE:grate, my.IR1:ir1, my.IR2:ir2, my.VR1:vr1, my.VR2:vr2 }
	
	def __init__(self, theta1, clen, lambda0, center=(0,0,0), angle=0, **extras):
		self.init(theta1, clen, lambda0, center, angle, extras)
		
	def init(self, theta1, clen, lambda0, center, angle, extras):
		grating_offset=-0.075
		exit_height=-1.0*inch
		exit_z=-0.275
		my=blue_compressor
		basebeam=beam((0,0,-1.0), qtens(lambda0, w=0.001, r=Infinity))
		optics=self.setup_reflectors_blue(basebeam, theta1, clen, grating_offset, lam0=lambda0, inside_retro_err=0.0)
					
		cs=Numeric.array((0, exit_height, -0.44)) #entrance to compressor, before rotation
	
		optics[my.IPERI1]=reflector("input peri bot", angle=0, center=cs, width=.025)
		optics[my.IPERI2]=reflector("input peri top", angle=0, center=cs+(0.0,-exit_height, 0), width=.025)
	
		optics[my.EXP1]=lens("expander diverge", f=-.15).place_between(cs+(-.1,0,0), optics[my.IPERI1], -0.09)
		optics[my.EXP2]=lens("expander re-coll", f=0.3).place_between(optics[my.IPERI2], (0,0,0), 0.037)	
		#optics[my.EXP2]=lens("expander re-coll", f=0.3).place_between(optics[my.IPERI2], (0,0,0), 0.0357)	
	
		optics[my.IPERI1].set_direction(optics[my.EXP1], optics[my.IPERI2])
		optics[my.IPERI2].set_direction(optics[my.IPERI1], optics[my.EXP2])
	
		optics[my.OPERI1]=reflector("output peri top", angle=0, center=(0,my.y_offset,exit_z), width=.025)
		optics[my.OPERI2]=reflector("output peri bot", angle=0, center=(0,exit_height,exit_z), width=.025)

		optics[my.TM1]=reflector("output turn 1", angle=90, center=(0.30, exit_height,exit_z), width=.025)
	
		optics[my.OPERI1].set_direction((0,my.y_offset,0), optics[my.OPERI2])
		optics[my.OPERI2].set_direction(optics[my.OPERI1], optics[my.TM1])
				
		comp_order=(my.EXP1, my.IPERI1, my.IPERI2, my.EXP2, my.GRATE, 
				my.IR2, my.IR1, my.GRATE, my.VR1, my.VR2, my.GRATE, my.IR1, my.IR2, 
				my.GRATE, my.OPERI1, my.OPERI2, my.TM1)
					
		composite_optic.init(self, "compressor", optics, comp_order, None, center=center, angle=angle, extras=extras )		


def doit_bc(theta1, clen, lambda0, drawit=0):
	
	print "\n\n***start blue line trace***\n"
	grating_offset=-0.075
	exit_height=0
	exit_z=-0.3
	eta1=0.0
	
	optics={}
	
	END='end'
	optics[END]=null_optic("end", (0.15,exit_height,0), 0)
	START='start'
	optics[START]=null_optic("start", (0,0,-0.85))

	
	tracebeam=basebeam.clone()
	system_center=Numeric.array((-0.1, 0, -0.85))
	
	basebeam=beam(system_center, qtens(lambda0, q=spitfire.q0), lambda0)
	tracebeam.free_drift(-0.2)
		
	COMP='comp'
	comp=optics[COMP]=blue_compressor(theta1, clen, lambda0, center=system_center, angle=rotation)
	TM2='turn2'
	optics[TM2]=reflector("output turn 2", angle=0, center=(0.15,exit_height,-0.6), width=.025)

	optics[COMP].set_exit_direction(optics[TM2])
	optics[TM2].set_direction(optics[COMP], optics[END])

	sys_order=(START, COMP, TM2, DEMAG1, DEMAG2, END)

	GRATE=comp.mark_label(blue_compressor.GRATE)
	IR1=comp.mark_label(blue_compressor.IR1)
	IR2=comp.mark_label(blue_compressor.IR2)
	
	optic_sys=composite_optic("system", optics, sys_order, center=optics[START].center)
	
	trace0=trace_path(optic_sys, tracebeam.shift_lambda(0))
	trace0.color=graphite.green
	trace1=trace_path(optic_sys, tracebeam.shift_lambda(-0.5e-9))
	trace1.color=graphite.blue
	trace2=trace_path(optic_sys, tracebeam.shift_lambda(+0.5e-9))
	trace2.color=graphite.red
			
	try: #if one of the traces failed, this may not work
		print "Theta1=%.3f eta=%.3f len=%.3f lambda=%.4f" % (theta1, eta1, clen, lambda0*1e6)
		d0=trace0[-1]['total_drift']
		d1=trace1[-1]['total_drift']
		d2=trace2[-1]['total_drift']
		print ("d(lambda0-0.5nm)=%.3f m, d(lambda0+0.5nm)=%.3f m, dt/dl=%.0f ps/nm, " % (d1, d2, (d2-d1)*1e12/clight)), 
		print "d2t/dl2 = %.2f ps/nm^2" % ((d2+d1-2.0*d0)*(1e12/clight)*4)
		spot1info=trace0[(GRATE,0)] 
		spot2info=trace0[(GRATE,1)] 
		ir1info=trace0[(IR1,0)]
		ir2info=trace0[(IR2,0)]
		spot_offset=spot2info['position']-spot1info['position']
		retro_offset=ir2info['position']-ir1info['position']
		print "Grating offset = %.3f, retro_offset=%.3f" % (vec_mag(spot_offset), vec_mag(retro_offset))
		print "measured vertex length = %.3f" % vec_mag(comp[GRATE].center-comp[IR1].center)
		print "dispersion offset on grating = %.3f m / nm" % vec_mag(trace2[(GRATE,1)]['position']-trace1[(GRATE,1)]['position'])
		print "final q = ", trace0[-1]['q']
	except:
		traceback.print_exc()
		pass
				
	if drawit:
		g=draw_everything({"sys":optic_sys}, trace0, (-.9, .1), (-.5, .5), three_d=0)
		#g=draw_everything(optics, trace0, (-2, 2), (-2, 2))
		draw_trace(g, trace1)
		draw_trace(g, trace2)
		graphite.genOutput(g,'QD',canvasname="Compressor layout", size=(600,500))
		#graphite.genOutput(g,'PDF',canvasname="mendenhall pbg3:compressor.pdf", size=(600,500))

class quadrupler(composite_optic):
	L1, ENTRANCE, L2, DOUBLE, QUADRUPLE, EXIT = range(6)

	def __init__(self, center, from_optic, **extras):
		my=quadrupler
		optics={}
		ent=optics[my.ENTRANCE]=mir("quadrupler entrance")
		exit=optics[my.EXIT]=null_optic("quadrupler exit", (0,0,-1.0))
		l1=optics[my.L1]=lens("quadrupler telescope 1", f=+0.300)
		l2=optics[my.L2]=lens("quadrupler telescope 2", f=-0.150).place_between(ent, exit, 0.111).tilt_off_axis(4.0)
		#print l2.strength
		green=optics[my.DOUBLE]=null_optic("green crystal").place_between(l2, exit, 0.1)
		optics[my.QUADRUPLE]=null_optic("UV crystal").place_between(green, exit, 0.1)

		order=(my.L1, my.ENTRANCE, my.L2, my.DOUBLE, my.QUADRUPLE, my.EXIT)		
		composite_optic.init(self, "quadrupler", optics, order, (0,0,0), center, 0, extras=extras )
		l1.place_between(from_optic, ent, -0.04)

	def entrance_optics_tags(self):
		#the alignment element in the quadrupler is _not_ the first element (the lens)
		return quadrupler.ENTRANCE, quadrupler.EXIT
		
def plotq(trace):
	qxl=[]
	qyl=[]
	zl=[]
	for i in trace:
		zl.append(i.total_drift)
		qi=i.incoming_q
		qix, qiy=i.transform_q_to_table(qi)
		#xform, qix, qiy=qi.qi_moments()
		qxl.append(qi.rw(qix)[1])
		qyl.append(qi.rw(qiy)[1])
		zl.append(i.total_drift)
		qi=i.q
		qix, qiy=i.transform_q_to_table(qi)
		#xform, qix, qiy=qi.qi_moments()
		qxl.append(qi.rw(qix)[1])
		qyl.append(qi.rw(qiy)[1])
	
	
	g=graphite.Graph()
	g.top=10
	g.left=100
	g.right=g.left+700
	g.bottom=g.top+300
	#g.axes[graphite.X].range=xrange
	#g.axes[graphite.Y].range=yrange
	g.formats=[]
	
	dsx=graphite.Dataset()
	dsx.x=zl
	dsx.y=qxl
	g.datasets.append(dsx)
	colorline = graphite.PointPlot()
	colorline.lineStyle = graphite.LineStyle(width=1, color=graphite.red, kind=graphite.SOLID)
	colorline.symbol = None
	g.formats.append(colorline)	
	
	dsy=graphite.Dataset()
	dsy.x=zl
	dsy.y=qyl
	g.datasets.append(dsy)
	colorline = graphite.PointPlot()
	colorline.lineStyle = graphite.LineStyle(width=1, color=graphite.blue, kind=graphite.SOLID)
	colorline.symbol = None
	g.formats.append(colorline)

	g.axes[graphite.Y].tickMarks[0].labels = "%+.3f"
	g.axes[graphite.Y].label.text = "meters"
	g.axes[graphite.Y].tickMarks[0].inextent= 0.02
	g.axes[graphite.Y].tickMarks[0].labelStyle=graphite.TextStyle(hjust=graphite.RIGHT, vjust=graphite.CENTER, 
		font=graphite.Font(10,0,0,0,None), 
		color=graphite.Color(0.00,0.00,0.00))
	g.axes[graphite.Y].tickMarks[0].labeldist=-0.01

	g.axes[graphite.X].tickMarks[0].labels = "%+.0f"
	g.axes[graphite.X].label.text = "meters"
	g.axes[graphite.X].tickMarks[0].inextent= 0.02
	g.axes[graphite.X].tickMarks[0].labelStyle=graphite.TextStyle(hjust=graphite.CENTER, vjust=graphite.TOP, 
		font=graphite.Font(10,0,0,0,None), 
		color=graphite.Color(0.00,0.00,0.00))
	g.axes[graphite.X].tickMarks[0].labeldist=-0.01
		
	if show_qd:
		graphite.genOutput(g,'QD',canvasname="Beam size", size=(900,500))
	if show_pdf:
		graphite.genOutput(g,'PDF',canvasname="Q_plot", size=(900,500))
			
def show_table():
	inch=0.0254
	lambda0=1.054e-6
	spitfire_exit=Numeric.array((2*inch, 5*inch, -0.65))
	compressor_entrance=Numeric.array((45.5*inch, 2.5*inch, 46.5*inch))
	
	optics={}
	BLUELINE='bl'
	SPLIT='split'
	START='start'
	COMP='compressor'
	QUAD='quadrupler'
	IR='ir'
	IR_COMP='ir compressor'
	BE_TURN='be_turn'
	IZ_SCREEN='iz'
	
	optics[START]=null_optic("start", spitfire_exit)
	optics[BLUELINE]=blueline=blue_through_ylf()	
	optics[SPLIT]=split1=reflector("splitter1", center=(2*inch, 5*inch, 3*inch))
	optics[IR]=irline=ir_line()
	
	comp=optics[COMP]=blue_compressor(38.5, 1.28, lambda0, center=compressor_entrance, angle=270)
	mainbeam=beam( spitfire_exit, qtens(lambda0, spitfire.q0), lambda0)
	#print mainbeam.q
	split1.set_direction(spitfire_exit, blueline)
	blueline.set_entrance_direction(split1)
	blueline.set_exit_direction(comp)
	comp.rotate_to_axis(blueline)
	q=optics[QUAD]=quadrupler(center=(40*inch, 2.5*inch, 34.5*inch), from_optic=comp[blue_compressor.TM1])
	comp.set_exit_direction(q)
	q.set_entrance_direction(comp)
	blue_sys=composite_optic("blue_sys", optics, [START, SPLIT, BLUELINE, COMP, QUAD], (0,0,0), (0,0,0), 0)
	irline.set_entrance_direction(spitfire_exit)
	
	#align compressor table to output of main IR line
	ir_sys=composite_optic("ir_sys", optics, [START, IR], (0,0,0), (0,0,0), 0).clone()
	pointer=trace_path(ir_sys, mainbeam.clone())[-1]
	pointer.free_drift(1.0)
	optics[IR_COMP]=ircomp=ir_compressor(center=pointer.x0, angle=math.atan(0.2)/deg)
	ircomp.set_entrance_direction(irline)

	#now, align IZ
	ir_sys=composite_optic("ir_sys", optics, [START, IR, IR_COMP], (0,0,0), (0,0,0), 0).clone()
	pointer=trace_path(ir_sys, mainbeam.clone())[-1]
	pointer.free_drift(1.0)
	bemir=optics[BE_TURN]=reflector("be turn mirror", center=pointer.x0, angle=45.0)
	bemir.transport_to_here(pointer).transform(pointer)
	pointer.free_drift(0.1)
	dz=pointer.q.next_waist()
	pointer.free_drift(dz)
	optics[IZ_SCREEN]=null_optic("IZ", pointer.x0)
	ir_sys=composite_optic("ir_sys", optics, [START, IR, IR_COMP, BE_TURN, IZ_SCREEN], (0,0,0), (0,0,0), 0)
	
	whole_table=composite_optic("whole table", optics, [START, SPLIT, BLUELINE, COMP, QUAD, IR, IR_COMP, BE_TURN, IZ_SCREEN], (0,0,0), (0,0,0), 0)
	
	
	ir_trace=trace_path(ir_sys, mainbeam.clone())
	ir_trace.color=graphite.red
	blue_trace=trace_path(blue_sys, mainbeam.clone())
	blue_trace.color=graphite.blue
	
	if table_layout:
		g=draw_everything({"sys":whole_table}, ir_trace, (-.25,5), (0,2.5), three_d=0)
		draw_trace(g, blue_trace)
		
		#g=draw_everything({"sys":sys}, trace, (0.5,1.1), (0.8,1.1), three_d=0)
		#g=draw_everything({"sys":sys}, trace, (0.7,1.3), (0.9,1.2), three_d=0)
		if show_qd:
			graphite.genOutput(g,'QD',canvasname="Compressor layout", size=(900,500))
		if show_pdf:
			graphite.genOutput(g,'PDF',canvasname="Tablelayout", size=(900,500))
	#print trace[0]
	plotq(blue_trace)
	
	if 0:
		glabel=ircomp.mark_label(ircomp.INPUT)
		m=ir_trace[(glabel,0)]
		print "\n\n**start**\n\n"
		print m.incoming_direction, m.direction()
		print m.incoming_q
		print m.incoming_q.qi_moments()[1:3]
		print m.incoming_q.q_moments()[1:3]
		print m.incoming_q.qit, "\n"
		print m.localize_transform_tensor
		print m.footprint_q
		print m.footprint_q.qi_moments()[1:3]
		print m.footprint_q.q_moments()[1:3]
		print m.footprint_q.qit, "\n"
		print m.globalize_transform_tensor
		print m.q
		print m.q.qi_moments()[1:3]
		print m.q.q_moments()[1:3]
		print m.q.qit, "\n"

	glabel=ircomp.mark_label(ircomp.INPUT)
	#endpoint=ir_trace[(glabel,0)]  #get first hit on optic <glabel>
	endpoint=ir_trace[-1]
	q=endpoint.q
	
	t, qx0, qy0=q.qi_moments()
	theta=math.atan2(t[0,1].real, t[0,0].real)/deg
	qxx, qyy = endpoint.transform_q_to_table(q)
	dzx, dzy = (1e6/qxx).real, (1e6/qyy).real
	print ("qxx = %.1f, dzx = %.0f, qyy=%.1f, dzy=%.0f, (in um), theta=%.1f deg" % 
			(q.rw(qxx)[1]*1e6, dzx, q.rw(qyy)[1]*1e6, dzy, theta ) )

show_pdf=0
show_qd=1
table_layout=1

show_table()
	
#doit_bc(38.5, 1.28, 1.054e-6, 1)
