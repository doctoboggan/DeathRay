/* serve up USB data from a Measurement Computing USB device using libusb on MacOSX, Linux or *BSD */

static char rcsid[]="RCSID $Id: MeasurementComputingServer.c 323 2011-04-06 19:10:03Z marcus $";

/* 
requires libusb or libusb-win32 (from www.sourceforge.net) installed 
to compile on a Mac under OSX:
cc -o MeasurementComputingServer -framework IOKit -framework CoreFoundation -lusb MeasurementComputingServer.c

or to compile it using libusb statically, (so it can be installed on machines without libusb)
cc -o MeasurementComputingServer -framework IOKit -framework CoreFoundation /usr/local/lib/libusb.a MeasurementComputingServer.c

to compile under Linux or *BSD:
cc -o MeasurementComputingServer -lpthread -lusb  MeasurementComputingServer.c 
which should produce a working binary.

Under linux, it is apparently necessary also to do (as root):
chmod 4555 MeasurementComputingServer
chown root:root MeasurementComputingServer
to give the server setuid(0) privileges since libusb access to devices must be done as root 
*/

#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <pthread.h>
#include <signal.h>
#include <string.h>

#include <usb.h>
extern int usb_error_errno;

int keep_running=1;
usb_dev_handle *global_intf=0; /* global reference to device, for cleanup */
int use_time_stamps=0;

void handle_signal(int what)
{
	int err;
	keep_running=0;
	if (global_intf) {
		usb_resetep(global_intf, USB_ENDPOINT_IN | 1); /* terminate eternal read operation */
		usb_clear_halt(global_intf, USB_ENDPOINT_IN | 1); /* terminate eternal read operation */
		usb_resetep(global_intf, USB_ENDPOINT_OUT | 1); /* terminate eternal read operation */
		usb_clear_halt(global_intf, USB_ENDPOINT_OUT | 1); /* terminate eternal read operation */
	}
	global_intf=0; /* we've done our work, don't allow funny loops */
	fprintf(stderr,"Got signal\n");	
}

int read_feature_report(usb_dev_handle *udev, int readlen,  int index);
int pass_input(usb_dev_handle *udev);
int pass_output(usb_dev_handle *udev, int readlen);

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
				unsigned char breport[8];
				unsigned int ireport[8];
				int i;

#if DEBUG
				fprintf(stderr, "bp = %p,  bp-bpstart=%d, *bpstart=%s \n", bp, bp-bpstart, bpstart);
				fflush(0);
#endif
				
				if (strstr(bpstart,"****QUIT****")!=0) break;
				else if(strncmp(bpstart,"READ ",5)==0) {
					int readcount, readerr;
					readerr=sscanf(bpstart,"READ %d", &readcount);
					if (readerr==1) readerr=pass_output(udev, readcount);
					if(readerr) break;
				} 	else if(strncmp(bpstart,"FEAT ",5)==0) {
					int readerr, index, readlen;
					readerr=sscanf(bpstart,"FEAT %d %d", &readlen, &index);
					readerr=read_feature_report(udev, readlen, index);
					if(readerr) break;
				} else {
					sscanf(bpstart, "%d %d %d %d %d %d %d %d", 
						ireport, ireport+1, ireport+2, ireport+3, ireport+4, ireport+5, ireport+6, ireport+7);
					for(i=0; i<8; i++) breport[i]=ireport[i]; /* copy to byes for send */
					count = usb_interrupt_write(udev, USB_ENDPOINT_OUT | 1, breport, 8, 1000);
					if (count < 0 || count != 8)
					{
						fprintf(stderr, "write error: count=%d,  %s\n", count, usb_strerror());
						break;
					}
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

/* Note: the constant definitions are from the Darwin Project USBSpec.h file.  I hope that using a few constants in another
open-source project does not violate either the spirit or letter of Apple's APSL */
 
enum {
    kHIDRtInputReport		= 1,
    kHIDRtOutputReport		= 2,
    kHIDRtFeatureReport		= 3
};

#define HIDMgr2USBReportType(x) (x + 1)

enum {
    kUSBRqDirnShift = 7,
    kUSBRqDirnMask = 1,

    kUSBRqTypeShift = 5,
    kUSBRqTypeMask = 3,

    kUSBRqRecipientMask = 0X1F
};

enum {
	kUSBOut			= 0,
	kUSBIn			= 1,
	kUSBNone		= 2,
	kUSBAnyDirn		= 3
};

/*USBDirection*/

enum {
	kUSBStandard		= 0,
	kUSBClass		= 1,
	kUSBVendor		= 2
};

/*USBRqType*/

enum {
	kUSBDevice		= 0,
	kUSBInterface		= 1,
	kUSBEndpoint		= 2,
	kUSBOther		= 3
};

/*USBRqRecipient*/

enum {
    kHIDRqGetReport		= 1,
    kHIDRqGetIdle		= 2,
    kHIDRqGetProtocol		= 3,
    kHIDRqSetReport		= 9,
    kHIDRqSetIdle		= 10,
    kHIDRqSetProtocol		= 11
};


#define USBmakebmRequestType(direction, type, recipient)		\
    ((direction & kUSBRqDirnMask) << kUSBRqDirnShift) |			\
    ((type & kUSBRqTypeMask) << kUSBRqTypeShift) |			\
    (recipient & kUSBRqRecipientMask)

int read_feature_report(usb_dev_handle *udev, int readlen, int index)
{
	int err, count;
	const unsigned int retbufsize=256; /* the feature report for MCC devices is suppoed to be 105 bytes */
	struct { int blockflag; struct timeval tv; int bytecount; char inBuf[retbufsize];} datastruct;
	struct timezone tz;
	time_t start_time, stop_time;

	if (readlen > retbufsize) {
		fprintf(stderr, "MCC report length limited to  %d bytes, %d requested", retbufsize, readlen);
		return -1;
	}
	    
	datastruct.blockflag=0x00ffffff; /* make it easy to find timestamps in data */

	for(count=0; count<retbufsize;count++) datastruct.inBuf[count]=0;

	count=0;
	start_time=time(NULL);
	err=usb_control_msg(udev, USBmakebmRequestType(kUSBIn, kUSBClass, kUSBInterface), kHIDRqGetReport,
				HIDMgr2USBReportType(kHIDRtFeatureReport), index, datastruct.inBuf, readlen, 200);

#if DEBUG
	fprintf(stderr, "get feature error code %08lx\n", err);
	fflush(stderr);
#endif

	if(err) {
		datastruct.bytecount=err;
	} else {
		datastruct.bytecount=readlen;
	}
	
	if(use_time_stamps) {
		gettimeofday(&datastruct.tv, &tz);
		err=write(fileno(stdout), (void *)&datastruct, readlen+16);
	} else {
		err=write(fileno(stdout), &datastruct.inBuf, readlen);
	}
	fflush(stdout);
	return 0;	
}


int pass_output(usb_dev_handle *udev, int readlen)
{
	int err, count;
	const unsigned int retbufsize=256; /* MCC devices never transfer more than 256 bytes blocks */
	struct { int blockflag; struct timeval tv; int bytecount; char inBuf[retbufsize];} datastruct;
	struct timezone tz;
	time_t start_time, stop_time;
	
	if (readlen > retbufsize) {
		fprintf(stderr, "MCC devices never read more than %d bytes at a time, %d requested", retbufsize, readlen);
		return -1;
	}
	
	datastruct.blockflag=0x00ffffff; /* make it easy to find timestamps in data */
	count=0;
	start_time=time(NULL);
	count = usb_bulk_read(udev, USB_ENDPOINT_IN | 1 , datastruct.inBuf, readlen, 200);
#if DEBUG
	fprintf(stderr, "read %d bytes\n", count);
	fflush(stderr);
#endif

	datastruct.bytecount=count;
	
	if(use_time_stamps) {
		gettimeofday(&datastruct.tv, &tz);
		err=write(fileno(stdout), (void *)&datastruct, readlen+16);
	} else {
		err=write(fileno(stdout), &datastruct.inBuf, readlen);
	}
	fflush(stdout);
	return 0;	
}

void dealWithDevice(usb_dev_handle *udev)
{
	int err=1,i;
	pthread_t input_thread, output_thread;
	void *thread_retval;
	int count;
	
#ifdef DEBUG
		fprintf(stderr, "trying to configure interface\n");
		fflush(0);
#endif
	err=usb_set_configuration(udev, usb_device(udev)->config[0].bConfigurationValue); /* configure interface */

	if (err) {
		usb_reset(udev);
		usb_release_interface(udev,0);
		fprintf(stderr, "error configuring interface: %s\n", usb_strerror());
		return;
	}
	usleep(20000); /* wait 20 ms for safety */
#ifdef DEBUG
		fprintf(stderr, "done configuring... trying to claim\n");
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
		usb_reset(udev);
		usb_release_interface(udev,0);
		fprintf(stderr, "error claiming interface: %08lx\n", usb_error_errno);
		return;
	}
	
#ifdef DEBUG
	fprintf(stderr, "USB device apparently fully prepared to handle data\n");
	fflush(0);
#endif
	
	pass_input(udev);
	usb_reset(udev);
	usb_release_interface(udev,0);
	
}


int main (int argc, const char * argv[])
{
    int			idVendor = 0x09db, idProduct;
    int USBIndex, matchcount;
	int i;
	usb_dev_handle *udev=0;
	struct usb_bus *bus;
	struct usb_device *dev, *matchdev;
	
	/* if one argument is provided, it should be an index as to _which_ MCC device is to be opened 
		providing a negative index enables time stamping as is used when this is run as a robot */
	if (argc==3) {
		USBIndex=atoi(argv[2]);
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
		idProduct=atoi(argv[1]);
	} else {
		fprintf(stderr, "usage: %s <idProduct> <device index>\n", argv[0]);
		return -1;
	}
	
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
	for (bus = usb_busses; bus && matchcount<USBIndex; bus = bus->next) {
		for (dev = bus->devices; dev && matchcount<USBIndex; dev = dev->next) {			
			if(dev->descriptor.idVendor==idVendor && dev->descriptor.idProduct==idProduct) {
				matchcount++; matchdev=dev; }
		}
	}
	

	if(matchcount==USBIndex) {
		udev = usb_open(matchdev);
		if(udev) {
			fprintf(stderr, "Found device %p ID=0x%04x\n", (void*)udev, matchdev->descriptor.idProduct);
			fflush(0);
			global_intf=udev;
			usb_reset(udev);
			usb_reset(udev); /* make sure it's OK at the start */
			dealWithDevice(udev);
			global_intf=0; /* don't need resets any more */
			usb_reset(udev);
			usb_close(udev);
		} else {
			fprintf(stderr, "Found but couldn't open device %d... probably already open\n", USBIndex+1);
		}
    } else fprintf(stderr,"No MCC Device Found at index %d\n", USBIndex+1);
	    
	fprintf(stderr,"****EXITED****\n");
    return 0;
}
