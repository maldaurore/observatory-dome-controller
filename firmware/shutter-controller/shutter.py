from machine import Pin
import time
import ujson as json

# TO DO: añadir timestamps en logs

class Actions:
  OPEN = 0
  FREE_FLAP = 2
  CLOSE = 3
  RELEASE_FLAP_HOOK = 4

class DesiredActions:
  OPEN = 0
  OPEN_WITHOUT_FLAP = 1
  CLOSE = 2

class ShutterStatus:
    OPEN = 0
    CLOSED = 1
    OPENING = 2
    CLOSING = 3
    ERROR = 4
    UNKNOWN = 5

class FlapStatus:
    UP = 0
    DOWN = 1

class Shutter:
  def __init__(self, mqtt_client):
    self.state = {
      "shutter_status": None,
      "flap_status": None,
      "shutter_online": True
    }
    self.last_state = None
    self.last_serialized_state = ""
    self.abort_requested = False
    self.desired_action = None
    self.current_action = None
    self.client = mqtt_client
    self.last_update = time.ticks_ms() - 1000
    self.last_state_publish = time.ticks_ms()
    self.open_confirm_start = None
    self.close_confirm_start = None
    self.action_start_time = None
    self.hook_movement_start_time = None
    self.ACTION_TIMEOUTS = {
      Actions.OPEN: 120000,
      Actions.CLOSE: 120000,
    }

    # Pines de switches
    self.bottom_switch = Pin(26, Pin.IN, Pin.PULL_DOWN)
    self.top_switch = Pin(27, Pin.IN, Pin.PULL_DOWN)
    self.flap_switch = Pin(25, Pin.IN, Pin.PULL_DOWN)

    # Pines de los motores
    self.motor_open = Pin(13, Pin.OUT)
    self.motor_close = Pin(12, Pin.OUT)
    self.motor_close.value(0)
    self.motor_open.value(0)
    self.flap_motor_open = Pin(33, Pin.OUT)
    self.flap_motor_open.value(1)
    self.flap_motor_close = Pin(32, Pin.OUT)
    self.flap_motor_close.value(1)

    self.update()
    self.publishState()

  def openWithoutFlap(self):
    if self.state["shutter_status"] != ShutterStatus.CLOSED:
      return
    
    print("Liberando gajo...")
    now = time.ticks_ms()
    self.desired_action = DesiredActions.OPEN_WITHOUT_FLAP
    self.current_action = Actions.FREE_FLAP
    self.action_start_time = now
    self._reset_timers()
    self._stop_motors()
    self.flap_motor_open.value(0)
    return
  
  def abortSlew(self):    
    print('Abortando movimiento.')
    self.abort_requested = True
    return
  
  def close(self):
    if (self.state["shutter_status"] == ShutterStatus.CLOSED or
        self.state["shutter_status"] == ShutterStatus.OPENING
      ):
      return
    
    print('Closing shutter')
    self._stop_motors()
    self.desired_action = DesiredActions.CLOSE
    self.current_action = Actions.CLOSE
    self.action_start_time = time.ticks_ms()
    self._reset_timers()
    self.motor_close.value(1)
    return
  
  def open(self):
    if (
      self.state["shutter_status"] == ShutterStatus.OPENING or
      self.state["shutter_status"] == ShutterStatus.CLOSING or
      self.current_action == Actions.FREE_FLAP
      ):
      return

    print("Abriendo cortina.")
    
    self.desired_action = DesiredActions.OPEN
    self._stop_motors()

    self.current_action = Actions.OPEN
    self.motor_open.value(1)

    self.action_start_time = time.ticks_ms()
    self._reset_timers()

    return 'Abriendo cortina.'
  
  def _stop_motors(self):
    self.motor_close.value(0)
    self.motor_open.value(0)
    self.flap_motor_close.value(1)
    self.flap_motor_open.value(1)
  
  def getState(self):
    self.publishState()

  def publishState(self):
    if self.state != self.last_state:
      self.last_serialized_state = json.dumps(self.state)
      self.last_state = self.state.copy()
    self.client.publish_message(self.last_serialized_state)

  def update(self):
    now = time.ticks_ms()

    if time.ticks_diff(now, self.last_update) < 100:
      return
    
    self.last_update = now
    self._update_flap_status()
    self._update_shutter_status()

    if self.abort_requested:
      self._stop_motors()
      self.desired_action = None
      self.current_action = None
      self.action_start_time = None
      self._reset_timers()
      self.abort_requested = False
      return
    
    if self.current_action is not None and self.action_start_time is not None:
      timeout = self.ACTION_TIMEOUTS.get(self.current_action, None)
      if timeout is not None:
        if time.ticks_diff(now, self.action_start_time) > timeout:
          print("ERROR: timeout en acción", self.current_action)
          self._stop_motors()
          self.desired_action = None
          self.action_start_time = None
          self._reset_timers()
          self.current_action = None

    if self.current_action == Actions.OPEN:
      self._update_open()

    elif self.current_action == Actions.CLOSE:
      self._update_close()

    elif self.current_action == Actions.FREE_FLAP:
      self._update_free_flap()

    elif self.current_action == Actions.RELEASE_FLAP_HOOK:
      self._update_release_flap_hook()

    if time.ticks_diff(now, self.last_state_publish) > 1000:
      self.publishState()
      self.last_state_publish = now

  def _update_shutter_status(self):
    if self.bottom_switch.value() == 1:
      self.state["shutter_status"] = ShutterStatus.CLOSED
    elif self.bottom_switch.value() == 0 and self.top_switch.value() == 1 and self.current_action == Actions.OPEN:
      self.state["shutter_status"] = ShutterStatus.OPEN
    elif self.bottom_switch.value() == 0 and self.top_switch.value() == 1:
      if self.motor_close.value() == 1:
        self.state["shutter_status"] = ShutterStatus.CLOSING
      else:
        self.state["shutter_status"] = ShutterStatus.OPEN
    elif self.bottom_switch.value() == 0 and self.top_switch.value() == 0 and self.motor_open.value() == 1:
        self.state["shutter_status"] = ShutterStatus.OPENING
    else:
        self.state["shutter_status"] = ShutterStatus.ERROR

  def _update_flap_status(self):
    if self.flap_switch.value() == 1:
      self.state["flap_status"] = FlapStatus.DOWN
    else:
      self.state["flap_status"] = FlapStatus.UP

  def _update_open(self):
    now = time.ticks_ms()

    if self.state["shutter_status"] == ShutterStatus.OPEN:
      if self.open_confirm_start is None:
        self.open_confirm_start = now
      elif time.ticks_diff(now, self.open_confirm_start) > 200:
        self._stop_motors()
        self.desired_action = None
        self.current_action = Actions.RELEASE_FLAP_HOOK
        self.flap_motor_close.value(0)
        self.action_start_time = now

        self.open_confirm_start = None
        print('Cortina abierta.')
    else:
      self.open_confirm_start = None

  def _update_close(self):
    now = time.ticks_ms()
    if self.state["shutter_status"] == ShutterStatus.CLOSED:
      if self.close_confirm_start is None:
        self.close_confirm_start = now
      elif time.ticks_diff(now, self.close_confirm_start) > 200:
        self._stop_motors()
        self.desired_action = None
        self.current_action = Actions.RELEASE_FLAP_HOOK
        self.flap_motor_close.value(0)
        self.action_start_time = now

        self.close_confirm_start = None
        print("Cortina cerrada.")
    else:
      self.close_confirm_start = None
  
  def _update_free_flap(self):
    now = time.ticks_ms()
    if time.ticks_diff(now, self.action_start_time) > 1000:
      print("Gajo liberado, abriendo cortina...")
      self._stop_motors()
      self.current_action = Actions.OPEN
      self.action_start_time = time.ticks_ms()
      self._reset_timers()
      self.motor_open.value(1)

  def _update_release_flap_hook(self):
    now = time.ticks_ms()
    if time.ticks_diff(now, self.action_start_time) > 1000:
      print("Gancho en posición de reposo.")
      self._stop_motors()

      if self.desired_action == DesiredActions.OPEN:
        self.current_action = Actions.OPEN
        self.action_start_time = now
        self.motor_open.value(1)
      else:
        self.desired_action = None
        self.current_action = None
        self.action_start_time = None

  def _reset_timers(self):
    self.open_confirm_start = None
    self.close_confirm_start = None
