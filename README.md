# Task Management ADA

Sistema de gestión de tareas que combina dos estructuras de datos:

- **Montículo binario (max-heap)** para la cola de prioridad: siempre permite obtener la tarea más urgente.
- **Árbol AVL** para indexar las tareas por su ID único, con búsqueda en O(log n).

Ambas estructuras se mantienen sincronizadas a través del `TaskManager`, que es el punto de entrada para agregar, buscar y completar tareas.

## Requisitos

- Python 3.10 o superior (probado con Python 3.12).
- **Tkinter** (incluido en la mayoría de instalaciones de Python, ver instrucciones abajo).

## Instalación de Tkinter

Tkinter es la librería gráfica estándar de Python. Dependiendo del sistema operativo:

### 🪟 Windows

En Windows, Tkinter viene incluido con el instalador oficial de Python. Asegúrate de marcar la opción **"tcl/tk and IDLE"** durante la instalación.

Si ya tienes Python instalado y Tkinter no está disponible, reinstálalo desde [python.org](https://www.python.org/downloads/) marcando esa opción.

Para verificar que funciona:
```bash
python -m tkinter
```

### 🍎 macOS

En macOS, la versión de Python del sistema no incluye Tkinter. Se recomienda instalar Python con Homebrew:

```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python con soporte de Tkinter
brew install python-tk

# O si quieres una versión específica, por ejemplo 3.13:
brew install python-tk@3.13
```

Para verificar que funciona:
```bash
python3 -m tkinter
```

### 🐧 Linux

En la mayoría de distribuciones Linux, Tkinter debe instalarse por separado:

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install python3-tk
```

**Fedora / RHEL / CentOS:**
```bash
sudo dnf install python3-tkinter
```

**Arch Linux:**
```bash
sudo pacman -S tk
```

Para verificar que funciona:
```bash
python3 -m tkinter
```

## Ejecutar la aplicación

```bash
# En macOS / Linux
python3 main.py

# En Windows
python main.py
```

## Estructura del proyecto

```
Task_management_ADA/
├── models/
│   └── task.py            # Modelo Task (id, descripción, prioridad, fecha)
├── structures/
│   ├── avl_tree.py         # Árbol AVL: indexación por ID
│   └── max_heap.py         # Montículo binario: cola de prioridad
├── services/
│   └── task_manager.py     # Une heap + AVL: agregar, buscar, completar tareas
├── gui/
│   └── app.py              # Interfaz gráfica minimalista (notas B/N)
├── tests/
│   ├── test_avl.py
│   ├── test_heap.py
│   └── test_task_manager.py
└── main.py                  # Punto de entrada
```

## Cómo correr las pruebas

Cada archivo agrega la raíz del proyecto a `sys.path`, así que se puede correr de cualquiera de las dos formas, sin importar el directorio actual:

```bash
python3 tests/test_avl.py
python3 tests/test_heap.py
python3 tests/test_task_manager.py

# o como módulo, desde la raíz del proyecto
python3 -m tests.test_avl
python3 -m tests.test_heap
python3 -m tests.test_task_manager
```

Cada script imprime `OK: ...` por cada caso que pasa y termina con un mensaje de resumen.

## Uso básico de `TaskManager`

```python
from datetime import date
from models.task import Task
from services.task_manager import TaskManager

manager = TaskManager()

# ID automático (recomendado desde la GUI)
manager.create_task("Estudiar para el examen", 2, date(2026, 7, 20))  # Alta
manager.create_task("Comprar útiles escolares", 1)                     # Media
manager.create_task("Revisar correos electrónicos", 0)                # Baja

# También se puede insertar con ID manual (tests / demos)
manager.add_task(Task(101, "Otra tarea", 2, date(2026, 7, 20)))

manager.get_most_urgent()      # -> la más urgente, sin sacarla
manager.find_task(1)           # -> búsqueda por ID en el AVL
manager.complete_urgent()      # -> saca la más urgente del heap y del AVL
manager.complete_by_id(2)      # -> completa una tarea puntual por su ID
manager.list_tasks()           # -> todas las tareas ordenadas por ID
manager.balance_report()       # -> (id, altura, factor de balance) de cada nodo del AVL
```

Prioridad: `0 = Baja`, `1 = Media`, `2 = Alta`. Ante empate, gana la fecha más próxima; si no hay fecha, es la menos urgente. El ID de la GUI se asigna solo.

## Estado del proyecto

- [x] Montículo binario (heap) con inserción, extracción y eliminación por ID
- [x] Árbol AVL con inserción, búsqueda, eliminación y reequilibrio automático
- [x] `TaskManager` que sincroniza ambas estructuras
- [x] Pruebas unitarias de heap, AVL y `TaskManager`
- [x] Interfaz gráfica (GUI)
- [x] Punto de entrada (`main.py`)
