# tests/test_heap.py
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from structures.max_heap import MaxHeap


def crear_tarea(task_id, desc="Tarea", prioridad=1, fecha=None):
    return Task(task_id, desc, prioridad, fecha)


def es_max_heap(heap):
    """Verifica que cada padre gane (o empate) a sus hijos."""
    items = heap.items
    n = len(items)
    for i in range(n):
        izq = 2 * i + 1
        der = 2 * i + 2
        if izq < n and items[izq].has_more_priority(items[i]):
            return False
        if der < n and items[der].has_more_priority(items[i]):
            return False
    return True


def test_heap_vacio():
    heap = MaxHeap()
    assert heap.is_empty() is True
    assert heap.size() == 0
    assert heap.peek() is None
    assert heap.extract_max() is None
    assert heap.remove_by_id(1) is False
    print("OK: heap vacío")


def test_insercion_y_orden_de_extraccion():
    # Caso del PDF: Alta, Media, Baja -> debe salir primero la de Alta
    heap = MaxHeap()
    heap.insert(crear_tarea(101, "Estudiar para el examen", 3))
    heap.insert(crear_tarea(102, "Comprar útiles escolares", 2))
    heap.insert(crear_tarea(103, "Revisar correos electrónicos", 1))

    assert heap.size() == 3
    assert heap.peek().id == 101  # la más urgente, sin sacarla

    orden = [heap.extract_max().id for _ in range(3)]
    assert orden == [101, 102, 103]
    assert heap.is_empty() is True
    print("OK: inserción y orden de extracción por prioridad")


def test_desempate_por_fecha():
    # misma prioridad: gana la fecha más próxima; sin fecha es lo menos urgente
    heap = MaxHeap()
    heap.insert(crear_tarea(1, "Lejana", 2, date(2026, 12, 1)))
    heap.insert(crear_tarea(2, "Cercana", 2, date(2026, 7, 20)))
    heap.insert(crear_tarea(3, "Sin fecha", 2))

    orden = [heap.extract_max().id for _ in range(3)]
    assert orden == [2, 1, 3]
    print("OK: desempate por fecha de vencimiento")


def test_eliminacion_mantiene_estructura():
    # Prueba de eliminación del PDF: extraer y comprobar que el montículo se mantiene
    heap = MaxHeap()
    prioridades = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    for i, p in enumerate(prioridades, start=1):
        heap.insert(crear_tarea(i, f"T{i}", p))

    extraidas = []
    while not heap.is_empty():
        assert es_max_heap(heap)  # la propiedad de montículo se mantiene antes de sacar
        extraidas.append(heap.extract_max().priority)

    assert extraidas == sorted(prioridades, reverse=True)
    print("OK: eliminación mantiene la propiedad de montículo")


def test_remove_by_id():
    heap = MaxHeap()
    for i in [101, 102, 103, 104]:
        heap.insert(crear_tarea(i, f"T{i}", i % 3))

    assert heap.remove_by_id(102) is True
    assert heap.remove_by_id(102) is False  # ya no existe
    assert heap.size() == 3
    assert es_max_heap(heap)

    ids_restantes = sorted(t.id for t in heap.get_all())
    assert ids_restantes == [101, 103, 104]
    print("OK: remove_by_id conserva la estructura")


if __name__ == "__main__":
    test_heap_vacio()
    test_insercion_y_orden_de_extraccion()
    test_desempate_por_fecha()
    test_eliminacion_mantiene_estructura()
    test_remove_by_id()
    print("\nTodas las pruebas del heap pasaron.")
