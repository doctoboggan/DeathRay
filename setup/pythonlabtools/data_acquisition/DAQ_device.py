"abstract general data acquisition device class, implementing single-sample reads, triggered single block reads, queued block reads, and queued streaming reads"

_rcsid="$Id: DAQ_device.py 323 2011-04-06 19:10:03Z marcus $"

import threading
import time

class DAQ_device:
	"since DAQ_device will often be used as a mixin, most of its variables are private"
	
	#override this if some more interesting thread handler is needed e.g. one with failure notification
	ThreadingMethod=threading.Thread
	
	__streaming_starting=0
	__streaming_running=1
	__streaming_paused=2
	__stop_streaming=3

	queue_overflow_drop_new=1
	queue_overflow_drop_old=2
	
	def __init__(self ):
		pass
	
	def reset_device(self):
		"clear all channel info and return device to default state, all channels off typically"
		pass
		
	def set_input_channel_properties(self, chan, range, offset=0, **keywords):
		"set the full-scale range of a channel, assumed +-range if offset=0"
		pass
	
	def set_sample_properties(self, npoints=1, sampletime_seconds=1.0, averages=None, prestore_seconds=0.0):
		"set the block length, inter-sample time, and averageing for an acquisition"
		pass
	
	def set_trigger_properties(self, trig_channel=1, trig_level=0.0, trig_slope=1, trig_mode='immediate', **keywords):
		"set the trigger level for the device, using whatever units are likely to be obvious (!)"
		pass
	
	def get_sample_now(self):
		"get one sample or block immediately"
		pass
	
	def check_for_data_available(self):
		"return 1 if data is available, 0 if not"
		return 1
	
	def get_streamed_points(self):
		"get most recent points returned by a streaming source, returns [(timestamp, data),...]"
		raise NotImplementedError, "must define get_streamed_point for a device"
	
	def start_device_streaming(self):
		"initiate streaming on the device... must be overridden by real actions"
		raise NotImplementedError, "must define start_device_streaming for a device"

	def stop_device_streaming(self):
		"terminate streaming on the device... must be overridden by real actions"
		raise NotImplementedError, "must define stop_device_streaming for a device"

	def streamer_thread(self):
		self.__streaming_state=self.__streaming_running
		while(self.__streaming_state != self.__stop_streaming):
			newpoints=self.get_streamed_points()
			if self.__streaming_state==self.__streaming_paused: continue #ignore new data if paused
			self.__data_queue_lock.acquire() #freeze queue now
			self.__data_queue+=nl #tack data on
			ql=len(self.__data_queue)
			maxlen=self.__max_queue_len
			if ql > maxlen:
				self.stream_overflow_timestamp=time.time() #flag an overflow
				if self.__queue_overflow_action==self.queue_overflow_drop_old: 
					del self.__data_queue[:-maxlen]
				elif self.__queue_overflow_action==self.queue_overflow_drop_new:
					del self.__data_queue[maxlen:]
			self.__data_queue_lock.notify() #alert consumers to data
			self.__data_queue_lock.release() #unfreeze queue now
				
	def collect_streaming_data(self, queue_overflow_action=queue_overflow_drop_old, max_queue_len=100):
		"start queueing data from a device which has been put in streaming mode"
		self.__data_queue=[]
		self.stream_overflow_timestamp=None
		self.__data_queue_lock=threading.Condition()
		self.__streaming_state=self.__streaming_starting
		self.__queue_overflow_action=queue_overflow_action
		self.__max_queue_len=max_queue_len
		self.__streamer=self.ThreadingMethod(target=self.streamer_thread)
		self.__streamer_thread.setDaemon()
		self.__streamer_thread.start()
	
	def pause_streaming(self):
		"keep device running, but store no new data in queue"
		self.__streaming_state=self.__streaming_paused
	
	def resume_streaming(self):
		"restart storing data in queue"
		self.__streaming_state=self.__streaming_running
	
	def stop_streaming(self):
		"terminate all streaming operations"
		self.__streaming_state=self.__stop_streaming
			
	def get_next_queued_point(self, timeout=None):
		"get oldest data point from queue, or None if timeout seconds pass and no data is available. timeout=None waits forever"

		self.__data_queue_lock.acquire() #freeze queue now

		if self.__streamer.isAlive() and timeout != 0  and not self.__data_queue:
			self.__data_queue_lock.wait(timeout) #wait until queue has data
		
		if self.__data_queue:
			result=self.data_queue.pop()
		else:
			result=None
		self.__data_queue_lock.release() #unfreeze queue now
		return result
		
	def get_all_queued_points(self):
		"get all available data from queue"
		self.__data_queue_lock.acquire() #freeze queue now
		result=self.__data_queue
		self.__data_queue=[]
		self.__data_queue_lock.release() #unfreeze queue now
		return result
	
	def check_streamer_status(self):
		return self.__streamer.isAlive()
			
	