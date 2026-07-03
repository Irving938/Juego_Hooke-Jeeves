# Juego_Hooke-Jeeves

Estado del proyecto

Versión 0.1 – Prototipo inicial

Actualmente el proyecto incluye:

Ventana principal desarrollada con Pygame.
Interfaz completamente dibujada con figuras geométricas (sin uso de imágenes o assets).
Representación de una forja y una espada.
Implementación inicial del algoritmo Hooke-Jeeves.

Exploración de dos variables:
Temperatura de la forja.
Tiempo de enfriamiento.
Implementación del Pattern Move.
Reducción manual del parámetro Δ.
Sistema de calidad de la espada basado en una función objetivo.
Recurso limitado de lingotes.
Condición de victoria basada en el criterio matemático del algoritmo.

Mecánica:
· Empiezas con temperatura=6, enfriamiento=-4 y un paso (Δ) de 2.

· Los botones Temp ± y Enfriar ± exploran sumando/restando Δ a la mejor solución actual. Si mejora, se actualiza la solución y se activa el pattern move.

· Repetir técnica ejecuta un movimiento de patrón: salta en la misma dirección del último éxito, acelerando la búsqueda.

· Cuando ningún vecino mejora, pulsas Reducir Δ para dividir el paso a la mitad y seguir afinando.

· El proceso termina cuando Δ es menor que ε = 0.10 (espada legendaria) o se agotan los 20 lingotes.

