from machine import Pin, Encoder
import time
import ujson as json

PULSOS_POR_ROTACION = 118745
PULSOS_POR_GRADO =  PULSOS_POR_ROTACION / 360
HOME_POSITION = 146.0
FIND_HOME_TIMEOUT = 60000
TOLERANCIA = 2
UMBRAL_INERCIA = 5
INERCIA = 3

class Base:
  def __init__(self, mqtt_client):
    self.state = {
      "dome_slewing": False,
      "at_park": False,
      "azimuth": None,
      "at_home": False,
      "base_online": True
    }
    self.last_state = None
    self.last_serialized_state = ""
    self.desiredAzimuth = None
    self.slewing_to_home = False
    self.slewing_to_azimuth = False
    self.slewing_to_park = False
    self.abort_requested = False
    self.client = mqtt_client
    self.last_update = time.ticks_ms()
    self.last_state_publish = time.ticks_ms()
    self.find_home_start_time = None
    self.motor_stop_time = None
    self.homing_state = None
    self.home_detect_time = None
    self.fine_steps =  0
    self.home_confirm_count = 0
    self.pulse_active = False
    self.pulse_start = 0
    self.pulse_duration = 0
    self.movement_direction = None # 0 izquierda, 1 derecha
    self.use_inertia_stop = False

    self.encoder = Encoder(0, Pin(25), Pin(33), x=4)
    self.last_encoder_value = self.encoder.value()
    self.encoder_stall_timer = None

    self.referenced = False

    # Pines del motor
    self.motor_right = Pin(26, Pin.OUT)
    self.motor_left = Pin(27, Pin.OUT)
    self.motor_left.value(0)
    self.motor_right.value(0)

    # Pin del sensor de home
    self.home_sensor = Pin(14, Pin.IN, Pin.PULL_UP)

    # Inicializar valores si está en home
    if self.home_sensor.value() == 0:
      self.handleAtHome()

    self.publishState()

  def _check_encoder_stall(self):
    current = self.encoder.value()
    now = time.ticks_ms()

    if current != self.last_encoder_value:
        self.encoder_stall_timer = now
        self.last_encoder_value = current
        return False

    if time.ticks_diff(now, self.encoder_stall_timer) > 2000:
        print("ERROR: no se detectó movimiento del codificador.")
        self.abort_requested = True
        return True

    return False
  
  def _check_find_home_timeout(self):
    now = time.ticks_ms()
    if time.ticks_diff(now, self.find_home_start_time) > FIND_HOME_TIMEOUT:
      print("ERROR: no se pudo encontrar home.")
      self.abort_requested = True
      return True
    
    return False
    
  def _stop_motors(self):
    self.motor_left.value(0)
    self.motor_right.value(0)
  
  def setSlaved(self, value):
    value = value.lower()
    if value == 'true':
      self.Slaved = True
    else: 
      self.Slaved = False

  def abortSlew(self, payload):
    self.abort_requested = True

  def handleAtHome(self):
    self.referenced = True
    self.state["at_home"] = True
    self.state["at_park"] = True
    self.state["azimuth"] = HOME_POSITION
    self.encoder.value(int(HOME_POSITION * PULSOS_POR_GRADO))

  def findHome(self, payload):
    
    # Si se encuentra en home, retorna.
    if self.home_sensor.value() == 0:
      self.handleAtHome()
      return
    
    self.slewing_to_home = True
    self.abort_requested = False

    self.encoder_stall_timer = time.ticks_ms()
    self.last_encoder_value = self.encoder.value()
    self.find_home_start_time = time.ticks_ms()

    # Si se encontraba realizando alguna operación de slewing, se cancela dicha operación,
    # pero continúa en movimiento hasta encontrar home.
    if self.slewing_to_azimuth or self.slewing_to_park:
      self.slewing_to_azimuth = False
      self.slewing_to_park = False
      return
    
    # Si se conoce el azimut actual, se calcula la dirección de movimiento para encontrar
    # home.

    self.homing_state = "search"
    self.home_confirm_count = 0

    if self.referenced:

      delta = self._angular_delta(HOME_POSITION, self.state["azimuth"])
      self._stop_motors()

      if delta > 0:
          self.movement_direction = 1
          self._move(self.movement_direction)
      else:
          self.movement_direction = 0
          self._move(self.movement_direction)
          
    else:
      self._stop_motors()
      self.movement_direction = 1
      self._move(self.movement_direction)

    return

  def park(self, payload):
    # Si ya se encuentra en posición de park (que es la misma que home), retorna.
    if self.home_sensor.value() == 0:
      return
    
    if self.slewing_to_azimuth or self.slewing_to_home:
      self.slewing_to_azimuth = False
      self.slewing_to_home = False
    
    self.slewing_to_park = True
    self.abort_requested = False

    self.encoder_stall_timer = time.ticks_ms()
    self.last_encoder_value = self.encoder.value()
    self.find_home_start_time = time.ticks_ms()

    if self.referenced:

      delta = self._angular_delta(HOME_POSITION, self.state["azimuth"])
      self._stop_motors()

      if delta > 0:
          self.movement_direction = 1
          self._move(self.movement_direction)
      else:
          self.movement_direction = 0
          self._move(self.movement_direction)
    else:
      self._stop_motors()
      self.movement_direction = 1
      self._move(self.movement_direction)

    return

  def slewToAzimuth(self, payload):

    if not self.referenced:
      print("ERROR: domo no referenciado.")
      return

    desiredAzimuth = float(payload["azimuth"])
    delta = self._angular_delta(desiredAzimuth, self.state["azimuth"])
    dist = abs(delta)
    print(dist)
    if dist > UMBRAL_INERCIA:
      self.use_inertia_stop = True
    elif dist > TOLERANCIA:
      self.use_inertia_stop = False    
    if dist < TOLERANCIA:
      return
    
    if self.slewing_to_park or self.slewing_to_home:
      self.slewing_to_park = False
      self.slewing_to_home = False

    self.encoder_stall_timer = time.ticks_ms()
    self.last_encoder_value = self.encoder.value()
    
    self.motor_stop_time = None
    self.slewing_to_azimuth = True
    self.desiredAzimuth = desiredAzimuth
    self.abort_requested = False
    self.pulse_active = False

    direction = 1 if delta > 0 else 0 
    self.movement_direction = direction 
    self._move(direction)

    return

  def getState(self, payload):
    self.publishState()

  def update(self):
    now = time.ticks_ms()

    if time.ticks_diff(now, self.last_update) < 50:
      return
    
    self.last_update = now

    if self.abort_requested:
      self._stop_motors()
      self.slewing_to_azimuth = False
      self.slewing_to_home = False
      self.slewing_to_park = False
      self.abort_requested = False
      return
    
    if self.referenced:
        self._update_azimuth()

    if self.slewing_to_azimuth:
      self._update_slew_to_azimuth()
    elif self.slewing_to_home: 
      self._update_slew_to_home()
    elif self.slewing_to_park:
      self._update_slew_to_park()

    if time.ticks_diff(now, self.last_state_publish) > 1000:
      self.publishState()
      self.last_state_publish = now

    if (self.slewing_to_azimuth or self.slewing_to_home or self.slewing_to_park):
          self.state["dome_slewing"] = True
    else:
      self.state["dome_slewing"] = False

  def _update_azimuth(self):
    encoder_value = self.encoder.value() % PULSOS_POR_ROTACION
    self.encoder.value(encoder_value)

    azimuth = encoder_value / PULSOS_POR_GRADO
    self.state["azimuth"] = azimuth

  def _update_slew_to_azimuth(self):

    delta = self._angular_delta(self.desiredAzimuth, self.state["azimuth"])
    dist = abs(delta)
    now = time.ticks_ms()

    if dist >= TOLERANCIA and self._check_encoder_stall():
      return
      
    if dist <= TOLERANCIA and not self.use_inertia_stop :
      self._stop_motors()
      self.slewing_to_azimuth = False
      self.desiredAzimuth = None
      self.motor_stop_time = None
      self.movement_direction = None
      return

    if self.use_inertia_stop and dist < INERCIA:
      self._stop_motors()

      if self.motor_stop_time:
        if time.ticks_diff(now, self.motor_stop_time) > 1000:
          self.slewing_to_azimuth = False
          self.desiredAzimuth = None
          self.motor_stop_time = None
          self.movement_direction = None
      else:
        self.motor_stop_time = now

      return
    
    self.motor_stop_time = None

  def _update_slew_to_home(self):
    if self._check_encoder_stall():
      return
    if self._check_find_home_timeout():
      return
    
    home_sensor = self.home_sensor.value()

    # Buscando home a velocidad normal
    if self.homing_state == "search":
      if home_sensor == 0:
        self._stop_motors()
        self.homing_state = "wait_stop"
        self.home_detect_time = time.ticks_ms()

    # Esperando a que se detenga la cupula
    elif self.homing_state == "wait_stop":
      if time.ticks_diff(time.ticks_ms(), self.home_detect_time) > 1000:
        self.homing_state = "fine_back"
        self.fine_steps = 0

    elif self.homing_state == "fine_back":
      if home_sensor == 0:
        self.home_confirm_count += 1
      else:
        self.home_confirm_count = 0

      if self.home_confirm_count >= 3:
        self._stop_motors()
        self.slewing_to_home = False
        self.homing_state = None
        self.movement_direction = None
        self.handleAtHome()
        return
      
      if self.fine_steps > 50:
        print("ERROR: no se pudo centrar home.")
        self._stop_motors()
        self.slewing_to_home = False
        self.homing_state = None
        self.movement_direction = None
        return

      if not home_sensor == 0:
        self._pulse_move(abs(self.movement_direction - 1), 150)
        self.fine_steps += 1

  # Find home y park son equivalentes
  def _update_slew_to_park(self):
    if self._check_encoder_stall():
      return
    if self._check_find_home_timeout():
      return
    
    home_sensor = self.home_sensor.value()

    now = time.ticks_ms()
    if home_sensor == 0:
      self._stop_motors()
      if self.motor_stop_time:
        if time.ticks_diff(now, self.motor_stop_time) > 1000:
          self.slewing_to_park = False
          self.motor_stop_time = None
          self.handleAtHome()
      else:
        self.motor_stop_time = now
  
  def _angular_delta(self, target, current):
    return (target - current + 540) % 360 - 180

  def _pulse_move(self, direction, duration):
    now = time.ticks_ms()

    if not self.pulse_active:
      self._move(direction)
      self.pulse_start = now
      self.pulse_duration = duration
      self.pulse_active = True
      return
    
    elapsed = time.ticks_diff(now, self.pulse_start)
    
    if elapsed > self.pulse_duration:
      self._stop_motors()

      if elapsed < self.pulse_duration + 500:
        return
      
      self.pulse_active =  False

  def _move(self, direction):
    self._stop_motors()
    
    if direction > 0:
      self.motor_right.value(1)
    else:
      self.motor_left.value(1)

  def publishState(self):
    if self.state != self.last_state:
      self.last_serialized_state = json.dumps(self.state)
      self.last_state = self.state.copy()
    self.client.publish_message(self.last_serialized_state)