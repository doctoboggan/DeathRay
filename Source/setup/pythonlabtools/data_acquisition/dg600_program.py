"""Program an InterfaceTechnologies DG600 pattern generator.
This is very specific to the Vanderbilt University Free Electron Laser Center
klystron drive system, and only useful as example code to the rest of the world."""

_rcsid="$Id: dg600_program.py 323 2011-04-06 19:10:03Z marcus $"

import math

KICK_MASK=(0xf00000f0L) # mask for all bits attached to kicker
DIV_KICK_BIT=3
DIV_KICK_MASK=(1L<<DIV_KICK_BIT)
KICK_BIT_MASK=(0x00080)
FREEZE_BIT=0x100
DID_PULSE_BIT=0x10000 # bit set to pass to ADC indicating DQing valid after pulse

last_kly_sub=-1
last_kick_sub=-1
last_pulse_train=0

def parse_timing_files(files=("clock_timing.dat.txt",)):
	"parse_timing_files(filelist) returns a list of [ (dtime, state),...] from the files"
	sigtable=[]
	for fn in files:
		f=open(fn,"r")
		linelist=[(l, l.split('\t')) for l in [l.strip() for l in f.readlines()] if (l and l!="**END**" and l[0]!="#")]
		f.close()
		try:
			sigtable+=[ (int(s[0]), int(s[1]), int(s[2])) for rawline, s in  linelist]
		except ValueError:
			comment='Bad number format.'
			raise ValueError, "Bad line in timing file '%s'. %s Contents: %s" % (fn, comment, rawline)
		except IndexError:
			comment='Too few fields; maybe missing tabs?'
			raise ValueError, "Bad line in timing file '%s'. %s Contents: %s" % (fn, comment, rawline)
		
	sigtable.sort(lambda a,b:cmp(a[1],b[1])) #sort into increasing time for edges
	state_word=0L
	edges=len(sigtable)
	tr=[] #real transition list
	for loop in (1,2): #do this twice, first to discover the final state, and then to measure transitions from there
		time_offset=sigtable[0][1] #time of first edge in file
		for n in range(edges):
			chan, time, state = sigtable[n]
			mask=1L<<chan
			if state: 
				state_word |= mask
			else:
				state_word &= ~mask
			if loop==2 and (n==edges-1 or sigtable[n+1][1] != time_offset): #last edge or time change gets written out on second pass
				if n==edges-1:
					dtime=100
				else:
					t1=sigtable[n+1][1]
					dtime, time_offset = t1-time_offset, t1
				tr+=[[state_word, dtime]]
		
	return tr

def generate_dg600_table(name, data):  #this is a private procedure to generate_timing_setup 
	# copy out data sequence for kicker being kicked but not divided kicker
	outstr = "DSTTABLE DA, '%s','bitorder',1,%d\rDATA DA" % (name, len(data))

	for pattern, dt in data:
		outstr += ",#H%08x,,%d NS" % (pattern, dt)
	outstr +='\r';
	return outstr

def generate_timing_setup(auxfiles, kly_sub):	
		
	main_pattern=parse_timing_files(["clock_timing.dat.txt"]+list(auxfiles))
	
	div_kick_idle_state=(main_pattern[-1][0] & KICK_BIT_MASK) # value of kicker bit between pulses
	div_kick_idle_state_mask=bool(div_kick_idle_state)*DIV_KICK_MASK
		
	# make sure pattern stored has div kicker idling properly according to kicker idle requirements
	for i in main_pattern:
		i[0] = (i[0] & ~DIV_KICK_MASK) | div_kick_idle_state_mask
		
	start_bits=main_pattern[-1][0] #final state at end of pulse / start of next pulse
	
	idle_pattern=[ [start_bits | FREEZE_BIT, 1000], [start_bits, 1000000] ]		
	pulse_pattern=[ [start_bits | FREEZE_BIT, 1000], [start_bits | DID_PULSE_BIT, 1000000] ]
	idle_size=len(idle_pattern)	
	pattern_head=pulse_pattern+(kly_sub-1)*idle_pattern

	total_pattern_length=len(pattern_head)+len(main_pattern);
	
	outstr=""
	
	outstr += "ABORT\r*RST\rMODE TG\rCHAN 32\rCLKSRC EXT_OSC\rCLK_TH 500\r"
	outstr += ("TABLE 'KICK', %d ,'NOKICK', %d,'DIVKICK', %d, 'SYNC', %d\r" %  
		(total_pattern_length, total_pattern_length, total_pattern_length , idle_size)) #define tables	
	outstr += "FIELD 'bitorder','p16-p31,p0-p15'\r" # put low 16 bits out on high-bit connector for mechanical convenience
	
	outstr += generate_dg600_table('SYNC', idle_pattern)
	
	outstr +=generate_dg600_table('KICK', pattern_head+main_pattern)

	nopulse=[ ((pattern & (~(KICK_MASK|DIV_KICK_MASK)) ) | (start_bits & (KICK_MASK|DIV_KICK_MASK) ) , dt ) for pattern, dt in main_pattern]
	outstr +=generate_dg600_table('NOKICK', pattern_head+nopulse)
	
	# copy out data sequence for kicker and divided kicker being kicked
	# this is done by copying the kicker bit to the divide kicker bit
	divkick=[( ( pattern & (~DIV_KICK_MASK) ) | (bool(pattern& KICK_BIT_MASK)*DIV_KICK_MASK) , dt ) for pattern, dt in main_pattern]
	outstr +=generate_dg600_table('DIVKICK', pattern_head+divkick)
				
	return outstr

def setup_clock(desired_freq, kick_sub, train_length=0, auxfiles=() ):
	global last_kly_sub, last_kick_sub, last_pulse_train
	
	kly_sub=int(math.ceil(60.0/(desired_freq+0.001)))

	if (kly_sub > 20 or kick_sub < 1 or kick_sub > 300):
		raise UserWarning, "Bad clock: main=%.1f, kly sub=%d, kick_sub=%d" % (desired_freq, kly_sub, kick_sub)

	closest_freq = 60.0 / kly_sub

	if(kly_sub != last_kly_sub):
		tablestr=generate_timing_setup(auxfiles, kly_sub) #if the kly_sub has changed, we need to load new tables
	else:
		tablestr=''

	last_kly_sub=kly_sub; 
	last_kick_sub=-1;
	last_pulses=-1;
	
	outstr=''
	
	assert train_length==0, "Counted trains not supported yet"
	
	if not train_length: #
		outstr+="ABORT\rCLRSEQUENCE\r"
		r2=30//(kick_sub*kly_sub) #note new-style integer divide
		ml=1 #counter for major loop index on dg600
		
		# note that at divider ratios below 2 Hz, divide-by-N clock runs at kicker speed (i.e. slowly)
		nokickstr=bool(kick_sub>1)*(", 'NOKICK', %d" % (kick_sub-1) ) #blank unkicked pattern string completely if kick_sub <= 1
		
		if r2>1: # generate sequence of pulses without divide kicker
			outstr+="SEQUENCE ML %d, %d %s, 'KICK',1\r" % (ml, r2-1, nokickstr); ml+=1

		# generate final set with divided kicker on
		outstr+="SEQUENCE ML %d, %d %s, 'DIVKICK',1\r" % (ml, 1, nokickstr); ml+=1
		outstr += "mjloop c\rarm\rrun\r"
		
		return tablestr+outstr, closest_freq
	else:
		pass #add this code later

