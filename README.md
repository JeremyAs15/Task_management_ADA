# Task Management ADA

Sistema de gestión de tareas que combina dos estructuras de datos:

- **Montículo binario (max-heap)** para la cola de prioridad: siempre permite obtener la tarea más urgente.
- **Árbol AVL** para indexar las tareas por su ID único, con búsqueda en O(log n).

Ambas estructuras se mantienen sincronizadas a través del `TaskManager`, que es el punto de entrada para agregar, buscar y completar tareas.

## Requisitos

- Python 3.10 o superior (probado con Python 3.12).
- No requiere librerías externas por ahora (`requirements.txt` está vacío; se irá llenando cuando se agregue la GUI).

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
│   └── app.py              # Interfaz gráfica (pendiente)
├── tests/
│   ├── test_avl.py
│   ├── test_heap.py
│   └── test_task_manager.py
└── main.py                  # Punto de entrada (pendiente)
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

manager.add_task(Task(101, "Estudiar para el examen", 3, date(2026, 7, 20)))  # prioridad alta
manager.add_task(Task(102, "Comprar útiles escolares", 2))                     # prioridad media
manager.add_task(Task(103, "Revisar correos electrónicos", 1))                # prioridad baja

manager.get_most_urgent()      # -> tarea 101 (la más urgente, sin sacarla)
manager.find_task(102)         # -> búsqueda por ID en el AVL
manager.complete_urgent()      # -> saca la más urgente del heap y del AVL
manager.complete_by_id(102)    # -> completa una tarea puntual por su ID
manager.list_tasks()           # -> todas las tareas ordenadas por ID
manager.balance_report()       # -> (id, altura, factor de balance) de cada nodo del AVL
```

La prioridad de una tarea se define como `1 = Baja`, `2 = Media`, `3 = Alta`. Ante empate de prioridad, gana la tarea con fecha de vencimiento más próxima.

## Estado del proyecto

- [x] Montículo binario (heap) con inserción, extracción y eliminación por ID
- [x] Árbol AVL con inserción, búsqueda, eliminación y reequilibrio automático
- [x] `TaskManager` que sincroniza ambas estructuras
- [x] Pruebas unitarias de heap, AVL y `TaskManager`
- [ ] Interfaz gráfica (GUI)
- [ ] Punto de entrada (`main.py`)
