# tests/test_avl.py
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task
from structures.avl_tree import AVLTree


def crear_tarea(task_id, desc="Tarea", prioridad=1):
    return Task(task_id, desc, prioridad, date(2026, 7, 20))


def test_arbol_vacio():
    avl = AVLTree()
    assert avl.search(1) is None
    assert avl.delete(1) is False
    assert avl.inorder() == []
    assert avl.is_balanced() is True
    print("OK: árbol vacío")


def test_insercion_y_busqueda():
    avl = AVLTree()
    avl.insert(crear_tarea(101, "Estudiar", 2))
    avl.insert(crear_tarea(102, "Comprar", 1))
    avl.insert(crear_tarea(103, "Correos", 0))

    t = avl.search(102)
    assert t is not None
    assert t.id == 102
    assert t.description == "Comprar"
    assert avl.search(999) is None
    print("OK: inserción y búsqueda")


def test_inorder_ordenado_por_id():
    avl = AVLTree()
    avl.insert(crear_tarea(103))
    avl.insert(crear_tarea(101))
    avl.insert(crear_tarea(102))

    ids = [t.id for t in avl.inorder()]
    assert ids == [101, 102, 103]
    print("OK: inorder por ID")


def test_eliminacion():
    avl = AVLTree()
    for i in [101, 102, 103]:
        avl.insert(crear_tarea(i))

    assert avl.delete(102) is True
    assert avl.search(102) is None
    assert avl.delete(102) is False  # ya no existe
    assert avl.is_balanced() is True

    ids = [t.id for t in avl.inorder()]
    assert ids == [101, 103]
    print("OK: eliminación")


def test_equilibrio_secuencia_desbalanceada():
    # Caso del PDF: insertar 1,2,3,4,5 en orden
    avl = AVLTree()
    for i in range(1, 6):
        avl.insert(crear_tarea(i))

    assert avl.is_balanced() is True

    # todos los factores deben estar en -1, 0 o 1
    for node_id, height, balance in avl.get_balance_report():
        assert -1 <= balance <= 1, f"ID {node_id} desbalanceado: {balance}"
        assert height >= 1

    print("OK: equilibrio (secuencia 1..5)")
    print("Reporte:", avl.get_balance_report())


def test_actualizar_id_duplicado():
    avl = AVLTree()
    avl.insert(crear_tarea(101, "Vieja", 0))
    avl.insert(crear_tarea(101, "Nueva", 2))

    t = avl.search(101)
    assert t.description == "Nueva"
    assert t.priority == 2
    print("OK: actualizar tarea con mismo ID")


if __name__ == "__main__":
    test_arbol_vacio()
    test_insercion_y_busqueda()
    test_inorder_ordenado_por_id()
    test_eliminacion()
    test_equilibrio_secuencia_desbalanceada()
    test_actualizar_id_duplicado()
    print("\nTodas las pruebas AVL pasaron.")