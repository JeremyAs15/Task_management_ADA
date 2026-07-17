# gui/app.py
# Interfaz estilo Notion: notas, fecha/hora, AVL/Heap visibles

import calendar
import datetime
import math
import tkinter as tk
from tkinter import messagebox

from services.task_manager import TaskManager


# Paleta tipo Notion
BG = "#F7F6F3"
CARD = "#FFFFFF"
INK = "#37352F"
MUTED = "#787774"
LINE = "#E9E9E7"
ACCENT = "#2383E2"
ACCENT_SOFT = "#E7F3FC"
DANGER = "#EB5757"
DANGER_SOFT = "#FDECEC"
OK = "#0F7B6C"
OK_SOFT = "#E8F5F2"

PRIORITY_SOFT = {
    0: "#F1F1EF",  # baja
    1: "#FBF3DB",  # media
    2: "#FDEBEC",  # alta
}

# Tipografía más legible
FONT_TITLE = ("Segoe UI Semibold", 24)
FONT_SECTION = ("Segoe UI Semibold", 13)
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)
FONT_META = ("Segoe UI", 9)
FONT_BTN = ("Segoe UI Semibold", 10)
FONT_CARD = ("Segoe UI", 13)


def round_rect(canvas, x1, y1, x2, y2, r=14, **kwargs):
    """Rectángulo redondeado en un Canvas."""
    points = [
        x1 + r, y1,
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class SoftButton(tk.Frame):
    """Botón soft estilo Notion."""

    def __init__(self, parent, text, command, variant="ghost", **kwargs):
        bg = parent.cget("bg") if parent.cget("bg") else BG
        super().__init__(parent, bg=bg, **kwargs)
        self.command = command
        self.variant = variant

        styles = {
            "primary": (ACCENT, "#FFFFFF", ACCENT),
            "ghost": (CARD, INK, LINE),
            "soft": (ACCENT_SOFT, ACCENT, ACCENT_SOFT),
            "danger": (DANGER_SOFT, DANGER, DANGER_SOFT),
            "ok": (OK_SOFT, OK, OK_SOFT),
        }
        self.bg0, self.fg0, self.bd0 = styles.get(variant, styles["ghost"])
        self.bg1 = {
            "primary": "#1B6FC2",
            "ghost": "#EFEFEF",
            "soft": "#D6EAF8",
            "danger": "#FAD4D4",
            "ok": "#D3EEE8",
        }.get(variant, "#EFEFEF")

        self.btn = tk.Label(
            self,
            text=text,
            font=FONT_BTN,
            bg=self.bg0,
            fg=self.fg0,
            padx=12,
            pady=7,
            cursor="hand2",
            highlightbackground=self.bd0,
            highlightthickness=1 if variant == "ghost" else 0,
        )
        self.btn.pack(fill=tk.X)
        # ButtonRelease es más fiable que Button-1 en Labels
        self.btn.bind("<ButtonRelease-1>", self._fire)
        self.bind("<ButtonRelease-1>", self._fire)
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=self.bg1))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=self.bg0))

    def _fire(self, _event=None):
        if callable(self.command):
            self.command()


class DateTimePicker(tk.Frame):
    """Selector compacto de fecha + hora con popup de calendario."""

    def __init__(self, parent, initial=None, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        now = initial or datetime.datetime.now().replace(second=0, microsecond=0)
        self.value = now

        row = tk.Frame(self, bg=CARD)
        row.pack(fill=tk.X)

        self.lbl = tk.Label(
            row,
            text=self.value.strftime("%Y-%m-%d  %H:%M"),
            font=FONT_BODY,
            bg=BG,
            fg=INK,
            padx=10,
            pady=8,
            anchor="w",
            cursor="hand2",
            highlightbackground=LINE,
            highlightthickness=1,
        )
        self.lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl.bind("<Button-1>", lambda e: self.open_picker())

        SoftButton(row, "Fecha", self.open_picker, variant="soft").pack(side=tk.LEFT, padx=(8, 0))

        self._popup = None

    def get(self):
        return self.value

    def set(self, dt):
        self.value = dt
        self.lbl.config(text=self.value.strftime("%Y-%m-%d  %H:%M"))

    def open_picker(self):
        if self._popup is not None and self._popup.winfo_exists():
            self._popup.lift()
            return

        self._popup = tk.Toplevel(self)
        self._popup.title("Fecha y hora")
        self._popup.configure(bg=CARD)
        self._popup.resizable(False, False)
        self._popup.transient(self.winfo_toplevel())

        # Centrar cerca del botón
        self._popup.geometry("+%d+%d" % (self.winfo_rootx(), self.winfo_rooty() + 40))

        body = tk.Frame(self._popup, bg=CARD, padx=16, pady=14)
        body.pack()

        self._cal_year = self.value.year
        self._cal_month = self.value.month
        self._hour = tk.IntVar(value=self.value.hour)
        self._minute = tk.IntVar(value=self.value.minute)

        nav = tk.Frame(body, bg=CARD)
        nav.pack(fill=tk.X, pady=(0, 8))
        SoftButton(nav, "‹", self._prev_month, variant="ghost").pack(side=tk.LEFT)
        self.month_lbl = tk.Label(nav, font=FONT_SECTION, bg=CARD, fg=INK)
        self.month_lbl.pack(side=tk.LEFT, expand=True)
        SoftButton(nav, "›", self._next_month, variant="ghost").pack(side=tk.RIGHT)

        self.days_frame = tk.Frame(body, bg=CARD)
        self.days_frame.pack()

        time_row = tk.Frame(body, bg=CARD)
        time_row.pack(fill=tk.X, pady=(12, 8))
        tk.Label(time_row, text="Hora", font=FONT_SMALL, bg=CARD, fg=MUTED).pack(side=tk.LEFT)
        tk.Spinbox(
            time_row, from_=0, to=23, width=3, textvariable=self._hour,
            font=FONT_BODY, justify="center",
        ).pack(side=tk.LEFT, padx=(10, 4))
        tk.Label(time_row, text=":", font=FONT_BODY, bg=CARD, fg=INK).pack(side=tk.LEFT)
        tk.Spinbox(
            time_row, from_=0, to=59, width=3, textvariable=self._minute,
            font=FONT_BODY, justify="center",
        ).pack(side=tk.LEFT, padx=4)

        SoftButton(body, "Listo", self._confirm, variant="primary").pack(fill=tk.X, pady=(4, 0))
        self._render_calendar()

    def _prev_month(self):
        if self._cal_month == 1:
            self._cal_month = 12
            self._cal_year -= 1
        else:
            self._cal_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self._cal_month == 12:
            self._cal_month = 1
            self._cal_year += 1
        else:
            self._cal_month += 1
        self._render_calendar()

    def _render_calendar(self):
        for w in self.days_frame.winfo_children():
            w.destroy()

        nombres = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        self.month_lbl.config(text=f"{nombres[self._cal_month]} {self._cal_year}")

        for i, d in enumerate(["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]):
            tk.Label(self.days_frame, text=d, font=FONT_META, bg=CARD, fg=MUTED, width=3).grid(
                row=0, column=i, padx=1, pady=2
            )

        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(self._cal_year, self._cal_month)
        for r, week in enumerate(weeks, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self.days_frame, text="", width=3, bg=CARD).grid(row=r, column=c)
                    continue
                selected = (
                    day == self.value.day
                    and self._cal_month == self.value.month
                    and self._cal_year == self.value.year
                )
                lbl = tk.Label(
                    self.days_frame,
                    text=str(day),
                    width=3,
                    font=FONT_SMALL,
                    bg=ACCENT if selected else CARD,
                    fg="#FFFFFF" if selected else INK,
                    cursor="hand2",
                )
                lbl.grid(row=r, column=c, padx=1, pady=1)
                lbl.bind("<Button-1>", lambda e, d=day: self._pick_day(d))

    def _pick_day(self, day):
        h = max(0, min(23, int(self._hour.get())))
        m = max(0, min(59, int(self._minute.get())))
        self.value = datetime.datetime(self._cal_year, self._cal_month, day, h, m)
        self._render_calendar()

    def _confirm(self):
        h = max(0, min(23, int(self._hour.get())))
        m = max(0, min(59, int(self._minute.get())))
        self.value = self.value.replace(hour=h, minute=m, second=0, microsecond=0)
        self.set(self.value)
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes")
        self.root.geometry("1040x720")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self.tree_window = None
        self.tree_canvas = None
        self.heap_window = None
        self.heap_canvas = None

        self.manager = TaskManager()
        self.priority_var = tk.IntVar(value=1)

        self._build()
        self.refresh_notes()

    def _build(self):
        # Header siempre visible (aquí van AVL / Heap)
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, padx=28, pady=(18, 6))

        left_h = tk.Frame(header, bg=BG)
        left_h.pack(side=tk.LEFT)
        tk.Label(left_h, text="Notes", font=FONT_TITLE, bg=BG, fg=INK).pack(anchor="w")
        self.lbl_urgent = tk.Label(left_h, text="Sin pendientes", font=FONT_SMALL, bg=BG, fg=MUTED)
        self.lbl_urgent.pack(anchor="w", pady=(2, 0))

        tools = tk.Frame(header, bg=BG)
        tools.pack(side=tk.RIGHT)
        # Botones nativos: abren las gráficas AVL / Heap como en main
        tk.Button(
            tools, text="Ver Árbol AVL", command=self.show_avl_tree,
            font=FONT_BTN, bg=ACCENT_SOFT, fg=ACCENT, relief=tk.FLAT,
            padx=12, pady=8, cursor="hand2", activebackground="#D6EAF8",
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            tools, text="Ver Montículo Heap", command=self.show_heap_tree,
            font=FONT_BTN, bg=OK_SOFT, fg=OK, relief=tk.FLAT,
            padx=12, pady=8, cursor="hand2", activebackground="#D3EEE8",
        ).pack(side=tk.LEFT, padx=4)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=(10, 22))

        self._build_composer(body)
        self._build_notes_area(body)

    def _build_composer(self, parent):
        # Panel izquierdo con canvas redondeado de fondo
        wrap = tk.Frame(parent, bg=BG, width=300)
        wrap.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 18))
        wrap.pack_propagate(False)

        self.side_canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, width=300)
        self.side_canvas.pack(fill=tk.BOTH, expand=True)

        self.side_inner = tk.Frame(self.side_canvas, bg=CARD)
        self._side_win = self.side_canvas.create_window((0, 0), window=self.side_inner, anchor="nw")

        def _sync_side(event):
            self.side_canvas.itemconfig(self._side_win, width=event.width)
            self._paint_side_card()

        self.side_canvas.bind("<Configure>", _sync_side)
        self.side_inner.bind("<Configure>", lambda e: self._paint_side_card())

        inner = tk.Frame(self.side_inner, bg=CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        tk.Label(inner, text="Nueva nota", font=FONT_SECTION, bg=CARD, fg=INK).pack(anchor="w")
        tk.Label(inner, text="ID automático", font=FONT_META, bg=CARD, fg=MUTED).pack(anchor="w", pady=(2, 10))

        self.txt_desc = tk.Text(
            inner,
            height=5,
            font=FONT_BODY,
            bg=BG,
            fg=INK,
            relief=tk.FLAT,
            padx=12,
            pady=10,
            wrap=tk.WORD,
            insertbackground=INK,
            highlightthickness=1,
            highlightbackground=LINE,
        )
        self.txt_desc.pack(fill=tk.X)

        tk.Label(inner, text="Prioridad", font=FONT_META, bg=CARD, fg=MUTED).pack(anchor="w", pady=(14, 6))
        prio_row = tk.Frame(inner, bg=CARD)
        prio_row.pack(fill=tk.X)
        self._prio_buttons = []
        for value, label in ((0, "Baja"), (1, "Media"), (2, "Alta")):
            b = tk.Label(
                prio_row, text=label, font=FONT_SMALL, padx=12, pady=6,
                cursor="hand2", bg=PRIORITY_SOFT[value], fg=INK,
            )
            b.pack(side=tk.LEFT, padx=(0, 6))
            b.bind("<Button-1>", lambda e, v=value: self._set_priority(v))
            self._prio_buttons.append((value, b))
        self._set_priority(1)

        tk.Label(inner, text="Fecha y hora", font=FONT_META, bg=CARD, fg=MUTED).pack(
            anchor="w", pady=(14, 6)
        )
        self.dt_picker = DateTimePicker(inner)
        self.dt_picker.pack(fill=tk.X)

        SoftButton(inner, "Agregar nota", self.add_task, variant="primary").pack(fill=tk.X, pady=(16, 6))
        SoftButton(inner, "Completar urgente", self.complete_urgent, variant="ok").pack(fill=tk.X, pady=4)

        tk.Frame(inner, bg=LINE, height=1).pack(fill=tk.X, pady=14)
        tk.Label(inner, text="Buscar por ID", font=FONT_META, bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_action_id = tk.Entry(
            inner, font=FONT_BODY, bg=BG, fg=INK, relief=tk.FLAT,
            insertbackground=INK, highlightthickness=1, highlightbackground=LINE,
        )
        self.entry_action_id.pack(fill=tk.X, ipady=8, ipadx=8, pady=(6, 8))
        row = tk.Frame(inner, bg=CARD)
        row.pack(fill=tk.X)
        SoftButton(row, "Buscar", self.search_task, variant="ghost").pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4)
        )
        SoftButton(row, "Completar", self.complete_by_id, variant="ghost").pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0)
        )

    def _paint_side_card(self):
        self.side_canvas.delete("bg")
        w = self.side_canvas.winfo_width()
        h = max(self.side_inner.winfo_reqheight(), self.side_canvas.winfo_height())
        if w < 10:
            return
        round_rect(self.side_canvas, 1, 1, w - 2, h - 2, r=16, fill=CARD, outline=LINE, tags="bg")
        self.side_canvas.tag_lower("bg")
        self.side_canvas.configure(scrollregion=(0, 0, w, h))
        self.side_canvas.itemconfig(self._side_win, height=h)

    def _build_notes_area(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        scroll = tk.Scrollbar(right, orient=tk.VERTICAL, command=self.canvas.yview, width=10)
        self.notes_frame = tk.Frame(self.canvas, bg=BG)

        self.notes_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._canvas_window = self.canvas.create_window((0, 0), window=self.notes_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _set_priority(self, value):
        self.priority_var.set(value)
        for v, btn in self._prio_buttons:
            if v == value:
                btn.config(bg=ACCENT, fg="#FFFFFF")
            else:
                btn.config(bg=PRIORITY_SOFT[v], fg=INK)

    # ---------- notes ----------

    def refresh_notes(self):
        for child in self.notes_frame.winfo_children():
            child.destroy()

        tasks = self.manager.list_tasks()
        urgent = self.manager.get_most_urgent()

        if urgent:
            self.lbl_urgent.config(text=f"Urgente · #{urgent.id}  {urgent.description[:48]}")
        else:
            self.lbl_urgent.config(text="Sin pendientes")

        if not tasks:
            tk.Label(
                self.notes_frame,
                text="No hay notas.\nCrea una a la izquierda.",
                font=FONT_BODY,
                bg=BG,
                fg=MUTED,
                justify=tk.LEFT,
            ).pack(anchor="w", pady=48, padx=8)
            self.draw_tree()
            self.draw_heap()
            return

        cols = 2
        for i, task in enumerate(tasks):
            r, c = divmod(i, cols)
            card = self._make_card(self.notes_frame, task, is_urgent=(urgent and task.id == urgent.id))
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)

        self.notes_frame.columnconfigure(0, weight=1)
        self.notes_frame.columnconfigure(1, weight=1)
        self.draw_tree()
        self.draw_heap()

    def _make_card(self, parent, task, is_urgent=False):
        """Tarjeta redondeada con Editar / Eliminar / Completar."""
        wrap = tk.Frame(parent, bg=BG)
        canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, height=168)
        canvas.pack(fill=tk.BOTH, expand=True)

        content = tk.Frame(canvas, bg=CARD)
        win = canvas.create_window((12, 12), window=content, anchor="nw")

        def paint(event=None):
            canvas.delete("card")
            w = max(canvas.winfo_width(), 200)
            h = max(content.winfo_reqheight() + 24, 150)
            canvas.configure(height=h)
            outline = ACCENT if is_urgent else LINE
            fill = CARD
            round_rect(canvas, 4, 4, w - 4, h - 4, r=16, fill=fill, outline=outline, width=1, tags="card")
            canvas.tag_lower("card")
            canvas.itemconfig(win, width=w - 28)

        canvas.bind("<Configure>", paint)
        content.bind("<Configure>", paint)

        top = tk.Frame(content, bg=CARD)
        top.pack(fill=tk.X)

        badge_bg = PRIORITY_SOFT.get(task.priority, LINE)
        tk.Label(
            top,
            text=task.priority_label(),
            font=FONT_META,
            bg=badge_bg,
            fg=INK,
            padx=8,
            pady=2,
        ).pack(side=tk.LEFT)

        if is_urgent:
            tk.Label(top, text="Urgente", font=FONT_META, bg=ACCENT_SOFT, fg=ACCENT, padx=8, pady=2).pack(
                side=tk.LEFT, padx=(6, 0)
            )

        tk.Label(top, text=f"#{task.id}", font=FONT_META, bg=CARD, fg=MUTED).pack(side=tk.RIGHT)

        tk.Label(
            content,
            text=task.description,
            font=FONT_CARD,
            bg=CARD,
            fg=INK,
            wraplength=280,
            justify=tk.LEFT,
            anchor="w",
        ).pack(anchor="w", fill=tk.X, pady=(10, 6))

        tk.Label(
            content,
            text=task.due_label(),
            font=FONT_META,
            bg=CARD,
            fg=MUTED,
        ).pack(anchor="w")

        actions = tk.Frame(content, bg=CARD)
        actions.pack(fill=tk.X, pady=(12, 4))

        SoftButton(actions, "Editar", lambda tid=task.id: self._edit_description(tid), variant="ghost").pack(
            side=tk.LEFT, padx=(0, 4)
        )
        SoftButton(actions, "Eliminar", lambda tid=task.id: self._delete_task(tid), variant="danger").pack(
            side=tk.LEFT, padx=4
        )
        SoftButton(actions, "Completar", lambda tid=task.id: self._complete_card(tid), variant="ok").pack(
            side=tk.RIGHT
        )

        paint()
        return wrap

    # ---------- actions ----------

    def _center_window(self, win, width, height):
        """Centra una ventana Toplevel respecto a la pantalla (o al root)."""
        win.update_idletasks()
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + max((rw - width) // 2, 0)
            y = ry + max((rh - height) // 2, 0)
        except tk.TclError:
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - width) // 2
            y = (sh - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.lift()
        win.focus_force()

    def add_task(self):
        desc = self.txt_desc.get("1.0", tk.END).strip()
        if not desc:
            messagebox.showerror("Notes", "Escribe una descripción.")
            return
        due = self.dt_picker.get()
        task = self.manager.create_task(desc, self.priority_var.get(), due)
        self.txt_desc.delete("1.0", tk.END)
        self.refresh_notes()
        self.root.title(f"Notes — #{task.id}")

    def complete_urgent(self):
        task = self.manager.complete_urgent()
        if task:
            self.refresh_notes()
        else:
            messagebox.showinfo("Notes", "No hay tareas pendientes.")

    def search_task(self):
        try:
            task_id = int(self.entry_action_id.get().strip())
        except ValueError:
            messagebox.showerror("Notes", "ID inválido.")
            return

        n = len(self.manager.list_tasks())
        log_n = math.ceil(math.log2(n)) if n > 1 else (0 if n == 0 else 1)
        height = self.manager.avl.root.height if self.manager.avl.root else 0

        task = self.manager.find_task(task_id)
        self._show_search_result(task_id, task, n, log_n, height)

    def _show_search_result(self, task_id, task, n, log_n, height):
        """Ventana de resultado de búsqueda con complejidad O(log N)."""
        win = tk.Toplevel(self.root)
        win.title(f"Búsqueda · ID {task_id}")
        win.configure(bg=CARD)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        box = tk.Frame(win, bg=CARD, padx=22, pady=20)
        box.pack(fill=tk.BOTH, expand=True)

        found = task is not None
        status_bg = OK_SOFT if found else DANGER_SOFT
        status_fg = OK if found else DANGER
        status_txt = "Tarea encontrada" if found else "No encontrada"

        tk.Label(
            box, text=status_txt, font=FONT_SECTION, bg=status_bg, fg=status_fg,
            padx=12, pady=6,
        ).pack(anchor="w")

        # Complejidad (diseño anterior)
        comp = tk.Frame(box, bg=BG, highlightbackground=LINE, highlightthickness=1)
        comp.pack(fill=tk.X, pady=(14, 12))
        inner = tk.Frame(comp, bg=BG)
        inner.pack(fill=tk.X, padx=14, pady=12)

        tk.Label(inner, text="Complejidad de búsqueda (AVL)", font=FONT_META, bg=BG, fg=MUTED).pack(anchor="w")
        tk.Label(
            inner, text="O(log N)", font=("Segoe UI Semibold", 18), bg=BG, fg=ACCENT
        ).pack(anchor="w", pady=(4, 10))

        grid = tk.Frame(inner, bg=BG)
        grid.pack(fill=tk.X)
        rows = [
            ("N (tareas actuales)", str(n)),
            ("log₂(N) ≈", str(log_n)),
            ("Altura AVL", str(height)),
        ]
        for i, (label, value) in enumerate(rows):
            tk.Label(grid, text=label, font=FONT_SMALL, bg=BG, fg=MUTED).grid(
                row=i, column=0, sticky="w", pady=2
            )
            tk.Label(grid, text=value, font=FONT_BODY, bg=BG, fg=INK).grid(
                row=i, column=1, sticky="e", padx=(24, 0), pady=2
            )
        grid.columnconfigure(1, weight=1)

        tk.Label(
            inner,
            text="En el peor caso ≈ log₂(N) comparaciones.",
            font=FONT_META, bg=BG, fg=MUTED,
        ).pack(anchor="w", pady=(10, 0))

        # Detalle de la tarea
        if found:
            detail = tk.Frame(box, bg=CARD)
            detail.pack(fill=tk.BOTH, expand=True, pady=(4, 12))

            tk.Label(detail, text=f"#{task.id}", font=FONT_META, bg=CARD, fg=MUTED).pack(anchor="w")
            tk.Label(
                detail, text=task.description, font=FONT_CARD, bg=CARD, fg=INK,
                wraplength=380, justify=tk.LEFT, anchor="w",
            ).pack(anchor="w", fill=tk.X, pady=(6, 8))

            meta = tk.Frame(detail, bg=CARD)
            meta.pack(fill=tk.X)
            tk.Label(
                meta, text=task.priority_label(), font=FONT_META,
                bg=PRIORITY_SOFT.get(task.priority, LINE), fg=INK, padx=8, pady=2,
            ).pack(side=tk.LEFT)
            tk.Label(meta, text=task.due_label(), font=FONT_META, bg=CARD, fg=MUTED).pack(
                side=tk.LEFT, padx=(10, 0)
            )

            actions = tk.Frame(box, bg=CARD)
            actions.pack(fill=tk.X)

            def complete_and_close():
                self.manager.complete_by_id(task.id)
                win.destroy()
                self.refresh_notes()

            SoftButton(actions, "Completar", complete_and_close, variant="ok").pack(
                side=tk.LEFT, padx=(0, 6)
            )
            SoftButton(actions, "Cerrar", win.destroy, variant="ghost").pack(side=tk.LEFT)
            self._center_window(win, 440, 420)
        else:
            tk.Label(
                box,
                text=f"No hay ninguna tarea con ID {task_id}.",
                font=FONT_BODY, bg=CARD, fg=MUTED,
            ).pack(anchor="w", pady=(8, 16))
            SoftButton(box, "Cerrar", win.destroy, variant="ghost").pack(anchor="w")
            self._center_window(win, 400, 280)

    def complete_by_id(self):
        try:
            task_id = int(self.entry_action_id.get().strip())
        except ValueError:
            messagebox.showerror("Notes", "ID inválido.")
            return
        task = self.manager.complete_by_id(task_id)
        if task:
            self.refresh_notes()
        else:
            messagebox.showinfo("Notes", f"No hay tarea con ID {task_id}.")

    def _complete_card(self, task_id):
        if self.manager.complete_by_id(task_id):
            self.refresh_notes()

    def _delete_task(self, task_id):
        task = self.manager.find_task(task_id)
        if not task:
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar la nota #{task_id}?"):
            self.manager.delete_task(task_id)
            self.refresh_notes()

    def _edit_description(self, task_id):
        task = self.manager.find_task(task_id)
        if not task:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Editar #{task_id}")
        win.configure(bg=CARD)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        box = tk.Frame(win, bg=CARD, padx=22, pady=18)
        box.pack(fill=tk.BOTH, expand=True)

        tk.Label(box, text="Descripción", font=FONT_SECTION, bg=CARD, fg=INK).pack(anchor="w")
        txt = tk.Text(
            box, height=5, font=FONT_BODY, bg=BG, fg=INK, relief=tk.FLAT,
            padx=12, pady=10, wrap=tk.WORD, insertbackground=INK,
            highlightthickness=1, highlightbackground=LINE,
        )
        txt.pack(fill=tk.BOTH, expand=True, pady=(10, 14))
        txt.insert("1.0", task.description)
        txt.focus_set()

        def save():
            new_text = txt.get("1.0", tk.END).strip()
            if not new_text:
                messagebox.showerror("Notes", "La descripción no puede quedar vacía.", parent=win)
                return
            self.manager.update_description(task_id, new_text)
            win.destroy()
            self.refresh_notes()

        SoftButton(box, "Guardar", save, variant="primary").pack(fill=tk.X, pady=(0, 4))
        self._center_window(win, 460, 280)

    # ---------- visualizadores (mismo estilo gráfico que main) ----------

    def _open_viewer(self, kind):
        """Crea o enfoca la ventana del visualizador AVL o Heap."""
        if kind == "avl":
            title = "Visualizador Árbol AVL"
            attr_win, attr_cv = "tree_window", "tree_canvas"
            draw_fn = self.draw_tree
        else:
            title = "Visualizador Montículo (Max-Heap)"
            attr_win, attr_cv = "heap_window", "heap_canvas"
            draw_fn = self.draw_heap

        win = getattr(self, attr_win)
        if win is None or not win.winfo_exists():
            win = tk.Toplevel(self.root)
            win.title(title)
            win.geometry("1000x700")
            win.configure(bg="white")
            canvas = tk.Canvas(win, bg="white", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            # Redibujar cuando la ventana ya tiene tamaño real
            canvas.bind("<Configure>", lambda e, d=draw_fn: d())
            setattr(self, attr_win, win)
            setattr(self, attr_cv, canvas)
            win.protocol("WM_DELETE_WINDOW", lambda w=win, a=attr_win: self._close_viewer(w, a))
        else:
            win.deiconify()

        draw_fn()
        win.lift()
        win.focus_force()
        win.attributes("-topmost", True)
        win.after(200, lambda w=win: w.attributes("-topmost", False))

    def _close_viewer(self, win, attr_name):
        win.destroy()
        setattr(self, attr_name, None)

    def show_avl_tree(self):
        self._open_viewer("avl")

    def show_heap_tree(self):
        self._open_viewer("heap")

    def _truncate(self, text, max_len=16):
        """Solo las primeras 2 palabras, para que quepan en el círculo."""
        text = (text or "").replace("\n", " ").strip()
        if not text:
            return ""
        words = text.split()
        short = " ".join(words[:2])
        if len(words) > 2:
            short += "…"
        if len(short) > max_len:
            return short[: max_len - 1] + "…"
        return short

    def draw_tree(self):
        if self.tree_window is None or not self.tree_window.winfo_exists():
            return
        if self.tree_canvas is None:
            return

        self.tree_canvas.delete("all")
        w = max(self.tree_canvas.winfo_width(), 900)
        h = max(self.tree_canvas.winfo_height(), 600)
        root_node = self.manager.avl.root

        self.tree_canvas.create_text(
            16, 16,
            text="AVL  ·  círculo: ID + 2 primeras palabras  ·  BF al lado = factor de equilibrio",
            font=("Arial", 10),
            fill="#555555",
            anchor="nw",
        )

        if root_node is None:
            self.tree_canvas.create_text(
                w // 2, h // 2,
                text="Árbol AVL vacío\nAgrega notas para ver la gráfica",
                font=("Arial", 14),
                fill="#666666",
                justify=tk.CENTER,
            )
            return

        self._draw_node(root_node, w // 2, 80, max(w // 4, 180), 120)

    def _draw_node(self, node, x, y, dx, dy):
        """Nodo AVL circular: ID + 2 palabras; BF fuera a un lado."""
        r = 42
        balance = self.manager.avl._get_balance(node)
        desc = self._truncate(node.task.description)

        if node.left:
            self.tree_canvas.create_line(x, y, x - dx, y + dy, fill="black", width=2)
            self._draw_node(node.left, x - dx, y + dy, dx / 1.65, dy)
        if node.right:
            self.tree_canvas.create_line(x, y, x + dx, y + dy, fill="black", width=2)
            self._draw_node(node.right, x + dx, y + dy, dx / 1.65, dy)

        self.tree_canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="lightblue", outline="black", width=2,
        )
        self.tree_canvas.create_text(
            x, y - 10, text=f"ID:{node.key}", font=("Arial", 10, "bold")
        )
        self.tree_canvas.create_text(
            x, y + 10, text=desc, font=("Arial", 9), fill="#222222"
        )
        # Factor de equilibrio fuera del círculo, a la derecha
        self.tree_canvas.create_text(
            x + r + 12, y,
            text=f"BF:{balance}",
            font=("Arial", 9, "bold"),
            fill="#0B5CAB",
            anchor="w",
        )

    def draw_heap(self):
        if self.heap_window is None or not self.heap_window.winfo_exists():
            return
        if self.heap_canvas is None:
            return

        self.heap_canvas.delete("all")
        w = max(self.heap_canvas.winfo_width(), 900)
        h = max(self.heap_canvas.winfo_height(), 600)
        items = self.manager.heap.items

        self.heap_canvas.create_text(
            16, 16,
            text="Max-Heap  ·  círculo: ID + 2 primeras palabras  ·  W = peso (prioridad)",
            font=("Arial", 10),
            fill="#555555",
            anchor="nw",
        )

        if not items:
            self.heap_canvas.create_text(
                w // 2, h // 2,
                text="Montículo vacío\nAgrega notas para ver la gráfica",
                font=("Arial", 14),
                fill="#666666",
                justify=tk.CENTER,
            )
            return

        self._draw_heap_node(0, items, w // 2, 80, max(w // 4, 180), 120)

    def _draw_heap_node(self, index, items, x, y, dx, dy):
        """Nodo Heap circular: ID, 2 palabras y peso."""
        r = 42
        task = items[index]
        desc = self._truncate(task.description)
        n = len(items)
        left_idx = 2 * index + 1
        right_idx = 2 * index + 2

        if left_idx < n:
            self.heap_canvas.create_line(x, y, x - dx, y + dy, fill="black", width=2)
            self._draw_heap_node(left_idx, items, x - dx, y + dy, dx / 1.65, dy)
        if right_idx < n:
            self.heap_canvas.create_line(x, y, x + dx, y + dy, fill="black", width=2)
            self._draw_heap_node(right_idx, items, x + dx, y + dy, dx / 1.65, dy)

        self.heap_canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="lightgreen", outline="black", width=2,
        )
        self.heap_canvas.create_text(
            x, y - 14, text=f"ID:{task.id}", font=("Arial", 10, "bold")
        )
        self.heap_canvas.create_text(
            x, y + 2, text=desc, font=("Arial", 9), fill="#222222"
        )
        self.heap_canvas.create_text(
            x, y + 16, text=f"W:{task.weight}", font=("Arial", 8, "bold"), fill="#1B5E20"
        )
