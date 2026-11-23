# Remotización de la Cúpula del Instituto de Astronomía de la UNAM

Sistema de control automatizado y remoto de una cúpula astronómica desarrollado como proyecto de tesis de Ingeniería en Software y Tecnologías Emergentes en el Instituto de Astronomía de la Universidad Nacional Autónoma de México (IAUNAM), sede Ensenada.

El sistema permite controlar por computadora el posicionamiento acimutal de la cúpula y la apertura y el cierre de su cortina. También permite sincronizar el movimiento de la cúpula con el telescopio para facilitar su operación remota durante las observaciones astronómicas.

## Arquitectura del sistema

El sistema integra controladores embebidos, un servidor de control y una interfaz gráfica de usuario.

- **Servidor de control:** implementa una API basada en el estándar ASCOM Alpaca y se comunica con los controladores mediante MQTT.
- **Controlador de la cúpula:** gestiona el posicionamiento acimutal mediante un microcontrolador ESP32 con firmware desarrollado en MicroPython.
- **Controlador de la cortina:** gestiona las operaciones de apertura y cierre mediante un segundo microcontrolador ESP32 con firmware desarrollado en MicroPython.
- **Interfaz gráfica:** permite ejecutar operaciones específicas del dispositivo que no están contempladas en la interfaz ASCOM implementada.
- **Integración astronómica:** permite la comunicación con software compatible con ASCOM Alpaca y la sincronización de la cúpula con el movimiento del telescopio.

## Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Python | Servidor de control e interfaz gráfica |
| MicroPython | Firmware de los controladores embebidos |
| ESP32 | Control de los mecanismos de la cúpula |
| Flask | Implementación del servidor de control |
| ASCOM Alpaca | Interfaz de comunicación con software astronómico |
| MQTT | Comunicación entre el servidor y los controladores |
| Tkinter | Interfaz gráfica de usuario |

## Estructura del repositorio

```text
.
├── alpaca-server/
│   └── Código del servidor de control y la implementación ASCOM Alpaca
├── docs/
│   └── Documentación de instalación y puesta en marcha
├── firmware/
│   ├── dome-controller/
│   │   └── Firmware MicroPython para el controlador de la cúpula
│   └── shutter-controller/
│       └── Firmware MicroPython para el controlador de la cortina
└── gui/
    └── Código de la interfaz gráfica de usuario
```

Los directorios `dome-controller` y `shutter-controller` contienen el código fuente de los respectivos controladores y los archivos binarios de MicroPython utilizados en cada microcontrolador.

## Funcionalidades

- Control por computadora del posicionamiento acimutal de la cúpula.
- Control de apertura y cierre de la cortina.
- Comunicación entre el servidor y los controladores mediante MQTT.
- Integración con software astronómico compatible con ASCOM Alpaca.
- Sincronización del movimiento de la cúpula con el telescopio.
- Interfaz gráfica para ejecutar funciones específicas del sistema.
- Calibración, pruebas funcionales y puesta a punto de los componentes.

## Instalación y puesta en marcha

Las instrucciones de instalación, configuración y puesta en marcha se encuentran en el directorio [`docs/`](docs/installation/01-prerequisites.md).

## Documentación académica

La tesis describe el problema abordado, el diseño del sistema, las decisiones de implementación, las pruebas realizadas y los resultados obtenidos.

**Tesis:** [Consultar documento PDF](https://drive.google.com/file/d/1rIsZGJCLbtymYo_5ozS09ZWx_EQ7jnSA/view?usp=sharing)

## Contexto académico

- **Institución:** Instituto de Astronomía, Universidad Nacional Autónoma de México (IAUNAM).
- **Sede:** Ensenada, Baja California, México.
- **Proyecto:** Remotización de la Cúpula del Instituto de Astronomía de la UNAM.
- **Modalidad:** Proyecto de tesis de licenciatura en Ingeniería en Software y Tecnologías Emergentes.
