import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import InputControlElement
from _Framework.NotifyingControlElement import NotifyingControlElement
from Map import *

MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE,
 MIDI_CC_TYPE,
 MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

class MonoButtonElement(ButtonElement):
	__module__ = __name__
	__doc__ = ' Special button class that can be configured with custom on- and off-values, some of which flash at specified intervals called by ControlSurface._update_display()'

	#_original_forwarding_callback = None

	#def set_original_forwarding_callback(callback):
	#	"""set callback for installing forwardings"""
	#	assert (dir(callback).count('im_func') is 1)
	#	MonoButtonElement._original_forwarding_callback = callback

	#set_original_forwarding_callback = staticmethod(set_original_forwarding_callback)

	def __init__(self, is_momentary, msg_type, channel, identifier, name, cs):
		ButtonElement.__init__(self, is_momentary, msg_type, channel, identifier)
		#assert (MonoButtonElement._original_forwarding_callback != None)
		self._last_pressed = 0
		self._flash_state = 0
		self._color = 0
		self._on_value = 127
		self._off_value = 0
		self._is_enabled = True
		self._is_notifying = False
		self._force_next_value = False
		self.name = name
		self._script = cs
		self._report_value = False
		self._last_sent_value = -1
		#self._install_original_forwarding = MonoButtonElement._original_forwarding_callback
	

	def set_on_off_values(self, on_value, off_value):
		assert (on_value in range(128))
		assert (off_value in range(128))
		self._last_sent_value = -1
		self._on_value = on_value
		self._off_value = off_value
	

	def original_message_channel(self):
		return self._original_channel

	
	def original_message_identifier(self):
		return self._original_identifier
	

	def set_on_value(self, value):
		assert (value in range(128))
		self._last_sent_value = -1
		self._on_value = value
	

	def set_off_value(self, value):
		assert (value in range(128))
		self._last_sent_value = -1
		self._off_value = value
	

	def set_force_next_value(self):
		self._force_next_value = True
	

	def set_enabled(self, enabled):
		self._is_enabled = enabled
	

	def turn_on(self, force = False):
		self.send_value(self._on_value)
	

	def turn_off(self, force = False):
		self.send_value(self._off_value)
	

	def reset(self, force = False):
		self.send_value(0, force)
	

	def receive_value(self, value):
		#for notification in self._value_notifications:
		#	self._script.log_message(str(self.name) + ' ' + str(notification))
		if self._is_enabled:
			InputControlElement.receive_value(self, value)
	

	def send_value(self, value, force_send = False):
		if(type(self) != type(None)):
			assert (value != None)
			assert isinstance(value, int)
			assert (value in range(128))
			if (force_send or ((value != self._last_sent_value) and self._is_being_forwarded)):
				data_byte1 = self._original_identifier
				if value in range(1, 127):
					data_byte2 = COLOR_MAP[(value - 1) % 7]
				elif value == 127:
					data_byte2 = COLOR_MAP[6]
				else:
					data_byte2 = 0
				self._color = data_byte2
				status_byte = self._original_channel
				if (self._msg_type == MIDI_NOTE_TYPE):
					status_byte += MIDI_NOTE_ON_STATUS
				elif (self._msg_type == MIDI_CC_TYPE):
					status_byte += MIDI_CC_STATUS
				else:
					assert False
				self.send_midi((status_byte,
				 data_byte1,
				 data_byte2))
				self._last_sent_value = value
				if self._report_output:
					is_input = True
					self._report_value(value, (not is_input))
				self._flash_state = round((value - 1)/7)
				self._last_pressed = int(self._script._timer)
	

	def install_connections(self):	#this override has to be here so that translation will happen when buttons are disabled
		if self._is_enabled:
			ButtonElement.install_connections(self)
		elif ((self._msg_channel != self._original_channel) or (self._msg_identifier != self._original_identifier)):
			self._install_translation(self._msg_type, self._original_identifier, self._original_channel, self._msg_identifier, self._msg_channel)
	

	def flash(self, timer):
		if (self._is_being_forwarded and self._flash_state in range(1, 18) and (timer % self._flash_state) == 0):
			data_byte1 = self._original_identifier
			data_byte2 = self._color * int((timer % (self._flash_state * 2)) > 0)
			status_byte = self._original_channel
			if (self._msg_type == MIDI_NOTE_TYPE):
				status_byte += MIDI_NOTE_ON_STATUS
			elif (self._msg_type == MIDI_CC_TYPE):
				status_byte += MIDI_CC_STATUS
			else:
				assert False
			self.send_midi((status_byte,
			 data_byte1,
			 data_byte2))
	