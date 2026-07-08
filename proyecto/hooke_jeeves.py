import math

# ----------------------------------------------------------------------
# Funciones de prueba
# ----------------------------------------------------------------------
def sphere(x, y):
    """Funcion Sphere: minimo global en (0,0)."""
    return x**2 + y**2

def himmelblau(x, y):
    """Funcion Himmelblau: cuatro minimos globales."""
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

def rastrigin(x, y, A=10):
    """Funcion Rastrigin: muchos minimos locales, global en (0,0)."""
    return 2*A + (x**2 - A * math.cos(2*math.pi*x)) + (y**2 - A * math.cos(2*math.pi*y))

def rosenbrock(x, y):
    """Funcion Rosenbrock (2D): valle curvo, minimo en (1,1)."""
    return 100*(y - x**2)**2 + (1 - x)**2

FUNCTIONS = {
    "sphere":     sphere,
    "himmelblau": himmelblau,
    "rastrigin":  rastrigin,
    "rosenbrock": rosenbrock,
}

# Nombre bonito y dificultad para mostrar en el menu
FUNCTION_INFO = {
    "sphere":     ("Sphere",     "Facil"),
    "himmelblau": ("Himmelblau", "Media"),
    "rastrigin":  ("Rastrigin",  "Dificil"),
    "rosenbrock": ("Rosenbrock", "Experto"),
}

# Escala para convertir f(x,y) en calidad 0-100: calidad = 100 * exp(-f/escala)
QUALITY_SCALE = {
    "sphere":     8.0,
    "himmelblau": 30.0,
    "rastrigin":  15.0,
    "rosenbrock": 60.0,
}

# Rango del punto inicial aleatorio (para que el reto sea justo en cada funcion)
START_RANGE = {
    "sphere":     8.0,
    "himmelblau": 5.0,
    "rastrigin":  4.5,
    "rosenbrock": 2.2,
}

# Semilado del dominio cuadrado que se dibuja en el mapa de contorno
MAP_DOMAIN = {
    "sphere":     10.0,
    "himmelblau": 6.0,
    "rastrigin":  5.5,
    "rosenbrock": 3.0,
}

# Minimos conocidos (se marcan en el mapa como referencia)
KNOWN_MINIMA = {
    "sphere":     [(0.0, 0.0)],
    "himmelblau": [(3.0, 2.0), (-2.805118, 3.131312),
                   (-3.779310, -3.283186), (3.584428, -1.848126)],
    "rastrigin":  [(0.0, 0.0)],
    "rosenbrock": [(1.0, 1.0)],
}


# ----------------------------------------------------------------------
# Clase del optimizador Hooke-Jeeves
# ----------------------------------------------------------------------
class HookeJeeves:
    """
    Implementacion interactiva del algoritmo de Hooke-Jeeves.
    El usuario controla manualmente los pasos: exploracion, patron y reduccion.
    """
    def __init__(self, x0=6.0, y0=-4.0, delta=2.0, epsilon=0.10, func_name="sphere"):
        # Punto inicial y mejor punto actual
        self.x0, self.y0 = x0, y0
        self.bx, self.by = x0, y0

        # Parametros del algoritmo
        self.delta = delta
        self.epsilon = epsilon

        # Seleccionar funcion objetivo
        if func_name not in FUNCTIONS:
            raise ValueError(f"Funcion '{func_name}' no soportada. Usa: {list(FUNCTIONS.keys())}")
        self.func_name = func_name
        self.func = FUNCTIONS[func_name]
        self.q_scale = QUALITY_SCALE[func_name]

        # Evaluar el punto inicial
        self.best_value = self.evaluate(self.bx, self.by)
        self.evaluations = 1

        # Historial de puntos aceptados: [(x, y, f), ...]  -> para el mapa
        self.history = [(self.bx, self.by, self.best_value)]

        # Estado de la exploracion
        self.explored = {"temp+": False, "temp-": False, "cool+": False, "cool-": False}
        # Candidatos evaluados en la ronda actual: [(x, y, mejoro), ...]
        self.candidates = []
        self.exploration_success = False
        self.last_direction = None
        self.message = "Explora las cuatro direcciones."

    # ------------------------------------------------------------------
    def evaluate(self, x, y):
        """Evalua la funcion objetivo en (x, y)."""
        return self.func(x, y)

    def quality(self, value):
        """
        Convierte el valor de f en una 'calidad' 0-100.
        Escala exponencial: 100 cuando f=0 y decae segun la funcion elegida.
        """
        try:
            return 100.0 * math.exp(-max(0.0, value) / self.q_scale)
        except OverflowError:
            return 0.0

    # ------------------------------------------------------------------
    def reset_exploration(self):
        """Reinicia el estado de exploracion para una nueva ronda."""
        self.explored = {"temp+": False, "temp-": False, "cool+": False, "cool-": False}
        self.candidates = []
        self.exploration_success = False
        self.last_direction = None

    def explore_direction(self, dx, dy):
        """
        Evalua un movimiento en la direccion (dx, dy) desde el mejor punto actual.
        Marca la direccion como explorada.
        Retorna True si mejoro, False en caso contrario.
        """
        if dx > 0:   key = "temp+"
        elif dx < 0: key = "temp-"
        elif dy > 0: key = "cool+"
        else:        key = "cool-"

        if self.explored[key]:
            self.message = f"Direccion {key} ya explorada."
            return False

        nx, ny = self.bx + dx, self.by + dy
        val = self.evaluate(nx, ny)
        self.evaluations += 1
        self.explored[key] = True

        if val < self.best_value:
            self.bx, self.by = nx, ny
            self.best_value = val
            self.history.append((nx, ny, val))
            self.candidates.append((nx, ny, True))
            self.exploration_success = True
            self.last_direction = (dx, dy)
            self.message = f"Mejoro! Nueva f = {val:.4f}"
            return True
        else:
            self.candidates.append((nx, ny, False))
            self.message = f"No mejoro. f = {val:.4f}"
            return False

    def all_explored(self):
        """Verifica si las cuatro direcciones ya fueron exploradas."""
        return all(self.explored.values())

    def pattern_move(self):
        """
        Realiza un salto de patron si la exploracion fue exitosa.
        Tras el salto (exitoso o no) se reinicia la exploracion, como dicta
        el algoritmo: patron -> nueva exploracion alrededor del punto base.
        Retorna True si el patron mejoro, False en caso contrario.
        """
        if not self.exploration_success or self.last_direction is None:
            self.message = "Exploracion sin exito: no se puede hacer patron."
            return False

        dx, dy = self.last_direction
        nx, ny = self.bx + dx, self.by + dy
        val = self.evaluate(nx, ny)
        self.evaluations += 1

        if val < self.best_value:
            self.bx, self.by = nx, ny
            self.best_value = val
            self.history.append((nx, ny, val))
            self.reset_exploration()
            self.message = f"Patron exitoso! f = {val:.4f}. Explora de nuevo."
            return True
        else:
            self.reset_exploration()
            self.message = "Patron sin mejora. Explora de nuevo."
            return False

    def reduce_delta(self):
        """Reduce delta a la mitad y reinicia la exploracion.
        Retorna True si el algoritmo debe terminar (delta < epsilon)."""
        self.delta /= 2.0
        self.reset_exploration()
        self.message = f"Delta reducido a {self.delta:.4f}"
        if self.delta < self.epsilon:
            self.message += "  |  Algoritmo terminado (delta < epsilon)."
            return True
        return False
# IRONEDIT:1783482987:87ea91712158e1cbce4f21aef3ade021b4ec7ea490c95097d2183aedc3fc9a1a
