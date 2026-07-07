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

# Version 0.2.4

CAMBIOS PRINCIPALES
1. Arquitectura y Organización
Reestructuración completa: El código pasó de ser un monolito a una estructura modular con clases y funciones bien definidas.

Separación de responsabilidades: Se creó una clase ForgeGame que encapsula toda la lógica del juego.

2. Motor de Optimización - Hooke-Jeeves
Nuevo algoritmo: Se implementó el método de optimización Hooke-Jeeves (importado de hooke_jeeves.py), reemplazando la lógica de exploración manual.

Funciones objetivo: Ahora se selecciona aleatoriamente entre múltiples funciones de optimización.

Evaluaciones automáticas: El algoritmo gestiona las exploraciones y movimientos patrón de forma más inteligente.

3. Interfaz de Usuario
Resolución: Cambió de 1000×700 a 1280×720, con soporte para redimensionamiento.

Diseño moderno: Panel de cliente, panel de algoritmo, historial de movimientos y panel de acciones.

Mejor organización visual: Layout con paneles rectangulares y bordes redondeados.

4. Sistema de Clientes
Más variedad: Se agregaron nombres de clientes (Caballero, Mercader, Rey, etc.).

Dificultad ajustable: La calidad requerida varía entre 80 y 96 (antes era 60-100).

5. Registro y Persistencia
Historial de movimientos: Se guarda un registro de las últimas acciones realizadas.

Exportación CSV: Los datos de cada partida se guardan en historial_partidas.csv con:

Fecha/hora

Nombre del cliente

Función utilizada

Valor objetivo

Calidad final

Número de evaluaciones, movimientos, movimientos patrón y reducciones de Δ

Puntuación

6. Mecánicas de Juego
Fases del algoritmo: Ahora se visualiza explícitamente la fase actual (Exploración, Movimiento patrón, Reduciendo Δ, Finalizado).

Mejora en la calidad: La calidad se calcula en tiempo real y se muestra con barra visual.

Sistema de puntuación: Se calcula una puntuación al finalizar que incluye bonus por eficiencia.

7. Sistema de Partículas
Nuevas partículas/chispas: Se agregó la clase Spark para efectos visuales de forja.

8. Eliminación de Características
Botones de tienda: Se eliminó el sistema de tienda con lingotes y mejoras de martillo.

Animaciones específicas: Se removieron las animaciones del martillo, cubo de agua y lava.

Eventos aleatorios: Se eliminaron los eventos de "fuego bajo", "chispa" y movimiento de pieza.

9. Manejo de Estado
Menú principal: Se simplificó, ahora inicia directamente en la forja.

Fin del juego: Al terminar todas las espadas, se guarda automáticamente el progreso.

10. Mejoras Técnicas
Escalado automático: Soporte para diferentes resoluciones con escalado uniforme.

Carga de fuentes: Función dedicada para cargar fuentes.

Manejo de eventos: Mejor organización del bucle principal.
