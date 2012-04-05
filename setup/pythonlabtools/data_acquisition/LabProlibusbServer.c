calc/* serve up USB data from a Vernier LabPro device attached via USB using libusb on MacOSX, Linux or *BSD */

static char rcsid[]="RCSID $Id: LabProlibusbServer.c 323 2011-04-06 19:10:03Z marcus $";

/* 
requires libusb or libusb-win32 (from www.sourceforge.net) installed.  It has been recently tested with version 0.1.12

to compile on a Mac under OSX (using Fink libusb, e.g.):
cc -o LabProUSBServer -I /sw/include -L/sw/lib -framework IOKit -framework CoreFoundation -lusb LabProlibusbServer.c
mv LabProUSBServer <same directory as active copy of LabPro_USB.py, if it's not already there>

or to compile it using libusb statically, (so it can be installed on machines without libusb)
cc -o LabProUSBServer -framework IOKit -framework CoreFoundation /usr/local/lib/libusb.a LabProlibusbServer.c

to compile under Linux or *BSD:
cc -o LabProUSBServer -lpthread -lusb  LabProlibusbServer.c 
mv LabProUSBServer <same directory as active copy of LabPro_USB.py, if it's not already there>
which should produce a working binary.

Under linux, it is apparently necessary also to do (as root):
chmod 4555 LabProUSBServer
chown root:root LabProUSBServer
to give the server setuid(0) privileges since libusb access to devices must be done as root 
*/

#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <pthread.h>
#include <signal.h>
#include <string.h>

#include <usb.h>

int keep_running=1, reader_running=0;
usb_dev_handle *global_intf=0; /* global reference to device, for cleanup */
int use_time_stamps=0;

void handle_signal(int what)
{
	int err;
	keep_running=0;
	if (global_intf) {
		while(reader_running) {
			/* usb_resetep listed as deprecated in 0.1.12 and beyond, functionality in usb_clear_halt */
			/* usb_resetep(global_intf, USB_ENDPOINT_IN | 2); */ /* terminate eternal read operation */
			usb_clear_halt(global_intf, USB_ENDPOINT_IN | 2); /* terminate eternal read operation */
			/* usb_resetep(global_intf, USB_ENDPOINT_OUT | 2); */ /* terminate eternal read operation */
			usb_clear_halt(global_intf, USB_ENDPOINT_OUT | 2); /* terminate eternal read operation */
			sleep(1);
		}
		global_intf=0; /* we've done our work, don't allow funny loops */
		fprintf(stderr,"Got signal\n");
	}
	
}

int pass_input(usb_dev_handle *udev)
{
	fd_set inpipeinfo;
	struct timeval timeout;
	int hasdata, count, err;
	char buf[8192], *eol, *bp, *bpstart;
	static int currbufpos=0;

	while(keep_running) {
		timeout.tv_sec=0;
		timeout.tv_usec=10;
	
		FD_ZERO(&inpipeinfo);
		FD_SET(fileno(stdin), &inpipeinfo);
		count=select(1, &inpipeinfo, 0, 0, &timeout);
		hasdata=FD_ISSET(fileno(stdin), &inpipeinfo);
		if(!(count && hasdata)) continue; /* select says no data on stdin */
		if (currbufpos > sizeof(buf)-1000) { /* approaching overflow..., dump some data, something is wrong */
			currbufpos=0;
		}
		
		count=read(fileno(stdin), &buf[currbufpos], sizeof(buf)-currbufpos-10);	
		if (count <=0) continue; /* somehow, even though select saw data, this didn't ?! */
		currbufpos+=count;
		buf[currbufpos]=0;
		bp=buf;
		while(bp) {
			bpstart=strsep(&bp, "\r\n"); /* find an eol */
			if(bp) { /* bp points beyond a terminator character */
				if (strstr(bpstart,"****QUIT****")!=0) break;
				/* fprintf(stderr, "bp = %p,  bp-bpstart=%d, *bpstart=%s \n", bp, bp-bpstart, bpstart); */
				bp[-1]='\r'; /* put on a carriage return for the LabPro */
				while(bpstart<bp) {
					int xcount;
					xcount=(bp-bpstart > 64)?64:bp-bpstart;
					count = usb_bulk_write(udev, USB_ENDPOINT_OUT | 2, bpstart, xcount, 10000);
					if (count < 0 || count != xcount)
					{
						fprintf(stderr, "write error: count=%d,  %s\n", count, usb_strerror());
						break;
					}
					bpstart+=count;
				}
			}
		}
		if(bp) break; /* we must have hit ****QUIT**** */
		/* fprintf(stderr, "copying string down...\n"); */
		strcpy(buf, bpstart); /* move leftover data down in buffer */
		currbufpos=strlen(buf);
	}
	keep_running=0;
	return 0;
}


int pass_output(usb_dev_handle *udev)
{
	int err, count;
	const unsigned int retbufsize=64; /* LabPro always transfers 64 bytes blocks */
	struct { int blockflag; struct timeval tv; char inBuf[retbufsize];} datastruct;
	struct timezone tz;
	time_t start_time, stop_time;
	
	datastruct.blockflag=0x00ffffff; /* make it easy to find timestamps in data */
	reader_running=1;
	while(keep_running) {
		count=0;
		start_time=time(NULL);
		count = usb_bulk_read(udev, USB_ENDPOINT_IN | 2 , datastruct.inBuf, retbufsize, 1000000);
		if (keep_running && count != retbufsize) {
			stop_time=time(NULL);
			if(stop_time-start_time < 995) {
				/* timeouts are 1000 seconds (1000000 milliseconds), so if we fail after this long, it's
					probably a timeout */
				fprintf(stderr, "read error: %s\n", usb_strerror());
				break;
			} else continue;
		} 
		if(keep_running) {
			if(use_time_stamps) {
				gettimeofday(&datastruct.tv, &tz);
				err=write(fileno(stdout), (void *)&datastruct, sizeof(datastruct));
			} else {
				err=write(fileno(stdout), &datastruct.inBuf, retbufsize);
			}
			fflush(stdout);
			if (err<0) break;
		}
	}
	keep_running=0;
	reader_running=0;
	
	return 0;	
}

void dealWithDevice(usb_dev_handle *udev)
{
	int err=1,i;
	pthread_t input_thread, output_thread;
	void *thread_retval;

	/* sometime other processes may be probing the LabPro just when we try to claim it, so try a few times */
	for(i=0, err=1; i<3 && err; i++) {	
#ifdef DEBUG
		fprintf(stderr, "trying to claim interface\n");
		fflush(0);
#endif
		err=usb_claim_interface(udev, 0);
		usleep(20000); /* wait 20 ms for safety */
		if(err) sleep(1);
	}
	if (err) {
		fprintf(stderr, "error claiming interface: %s\n", usb_strerror());
		return;
	}
	
#ifdef DEBUG
		fprintf(stderr, "trying to configure interface\n");
		fflush(0);
#endif
	if (!usb_device(udev)->config) { /* sometimes the Labpro returns no descriptors, configure it anyway! */
#ifdef DEBUG
		fprintf(stderr, "no descriptors... doing default configure\n");
		fflush(0);
#endif
			err=usb_set_configuration(udev, 1); /* configure interface */
	} else {
		err=usb_set_configuration(udev, usb_device(udev)->config[0].bConfigurationValue); /* configure interface */
	}
	
	if (err) {
		fprintf(stderr, "error configuring interface: %s\n", usb_strerror());
		return;
	}
	usleep(20000); /* wait 20 ms for safety */
#ifdef DEBUG
		fprintf(stderr, "done configuring... trying to reclaim\n");
		fflush(0);
#endif

	/* sometime other processes may be probing the LabPro just when we try to claim it, so try a few times */
	for(i=0, err=1; i<3 && err; i++) {	
#ifdef DEBUG
		fprintf(stderr, "trying to claim interface\n");
		fflush(0);
#endif
		err=usb_claim_interface(udev, 0);
		usleep(20000); /* wait 20 ms for safety */
		if(err) sleep(1);
	}
	if (err) {
		fprintf(stderr, "error claiming interface: %s\n", usb_strerror());
		return;
	}

#ifdef DEBUG
	fprintf(stderr, "USB device apparently fully prepared to handle data\n");
	fflush(0);
#endif
	
	err=pthread_create(&input_thread, 0, (void *)pass_input, udev);
	if(!err) err=pthread_create(&output_thread, 0, (void *)pass_output, udev);
	
	if(!err) {
		err=pthread_join(input_thread, &thread_retval);
		while(reader_running) { 
			usb_clear_halt(global_intf, USB_ENDPOINT_IN | 2); /* terminate eternal read operation */
			/* usb_resetep(global_intf, USB_ENDPOINT_IN | 2); */ /* terminate eternal read operation */
			usb_clear_halt(global_intf, USB_ENDPOINT_OUT | 2); /* terminate eternal read operation */
			/* usb_resetep(global_intf, USB_ENDPOINT_OUT | 2); */ /* terminate eternal read operation */
			sleep(1);
		}
		err=pthread_join(output_thread, &thread_retval);
	}
	usb_reset(udev);
	usb_release_interface(udev,0);
	
}


int main (int argc, const char * argv[])
{
    int			idVendor = 0x8f7;
    int			idProduct = 1;
    int USBIndex, matchcount;
	int i;
	usb_dev_handle *udev=0;
	struct usb_bus *bus;
	struct usb_device *dev, *matchdev;
	
	/* if one argument is provided, it should be an index as to _which_ USB LabPro is to be opened 
		providing a negative index enables time stamping as is used when this is run as a robot */
	if (argc==2) {
		USBIndex=atoi(argv[1]);
		if (abs(USBIndex) < 1 || abs(USBIndex) > 255) {
			fprintf(stderr,"Bad USB index argument provided... should be 1<=index<=255 or negative to enable binary time stamps, got: %s\n", argv[1]);
			fprintf(stderr,"****EXITED****\n");
			return 1;
		}
		if (USBIndex < 0) {
			USBIndex=-USBIndex;
			use_time_stamps=1;
		}
		USBIndex -=1;
	} else USBIndex=0;
	
	setbuf(stdout, 0);
	setbuf(stderr,0);

	usb_init();

#ifdef DEBUG
			usb_set_debug(DEBUG);
#else
			usb_set_debug(0);
#endif

	
#ifdef DEBUG
		fprintf(stderr, "inited libusb\n");
		fflush(0);
#endif
	usb_find_busses();
#ifdef DEBUG
		fprintf(stderr, "found busses in libusb\n");
		fflush(0);
#endif
	usb_find_devices();
    
#ifdef DEBUG
		fprintf(stderr, "found devices in libusb\n");
		fflush(0);
#endif

	signal(SIGHUP, handle_signal);
	signal(SIGINT, handle_signal);
	signal(SIGQUIT, handle_signal);
	signal(SIGTERM, handle_signal);
	signal(SIGPIPE, handle_signal);
	
	matchcount=-1;
	for (bus = usb_get_busses(); bus && matchcount<USBIndex; bus = bus->next) {
		for (dev = bus->devices; dev && matchcount<USBIndex; dev = dev->next) {			
			if(dev->descriptor.idVendor==idVendor && dev->descriptor.idProduct==idProduct) {
				matchcount++; matchdev=dev; }
		}
	}
	

	if(matchcount==USBIndex) {
		udev = usb_open(matchdev);
		if(udev) {
			fprintf(stderr, "Found device %p\n", (void*)udev);
			fflush(0);
			global_intf=udev;
			/* docs for 0.1.12 say usb_reset may cause re-enumeration, so don't do it here! */
			/*
			usb_reset(udev);
			usb_reset(udev); */ /* make sure it's OK at the start */
			dealWithDevice(udev);
			global_intf=0; /* don't need resets any more */
			usb_reset(udev);
			usb_close(udev);
		} else {
			fprintf(stderr, "Found but couldn't open device %d... probably already open\n", USBIndex+1);
		}
    } else fprintf(stderr,"No LabPro Found at index %d\n", USBIndex+1);
	    
	fprintf(stderr,"****EXITED****\n");
    return 0;
}
