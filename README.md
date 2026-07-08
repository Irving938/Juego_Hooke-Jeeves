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

# Version 0.2.5

Inicio con lingotes: ahora empiezas con 20 lingotes (antes 0).

Acumulación de lingotes: los lingotes sobrantes se conservan para el siguiente cliente (antes se perdían al terminar cada nivel).

Recarga automática de lingotes: cuando te quedas sin lingotes, el juego gasta oro automáticamente para comprar la cantidad necesaria (hasta un máximo de 20). Ya no se compran manualmente en la tienda.

Precio de lingote progresivo: cada vez que se realiza una recarga automática, el precio por lingote aumenta, encareciendo futuras reposiciones.

Tienda simplificada: solo puedes mejorar el martillo; se eliminó la opción de comprar lingotes.

Condición de derrota: Game Over ocurre en cualquier momento si te quedas sin lingotes y no tienes oro suficiente para comprar al menos uno. Antes solo sucedía al intentar iniciar un nuevo cliente sin oro suficiente para pagar el coste de entrada.

Sin victoria definida: el juego es infinito; ya no existe una pantalla de victoria tras 5 clientes.

Panel de información mejorado: muestra “Lingotes: X/20” y “Precio lingote: Y”, para que el jugador vea la capacidad máxima y el coste de reposición.

Historial más claro: en la pantalla de Game Over se muestra una tabla con las últimas 5 partidas, con encabezados (Fecha, Nivel, Oro, Req, Reward, Mejora). Además, cada entrada incluye la etiqueta “Game Over”.z

# Version 0.2.6
Menú principal rediseñado:
Título "THE PERFECT BLADE" más grande (HUGE_FONT), centrado y en negro (TITLE_BLACK).
Subtítulo "Algoritmo Hooke-Jeeves en acción" en amarillo, centrado debajo.

Dos botones: "Jugar" y "Tutorial".

Pantalla de tutorial:
Explica qué es el algoritmo, cómo funciona en el juego, qué hace cada botón y la dinámica general.
Texto dentro de un panel translúcido, ajustado para no salirse de los márgenes.
Botón "Volver" para regresar al menú.

Historial simplificado:
Eliminada la columna "Mejora" (d_upgrade) de la tabla de Game Over.
Las columnas restantes (Fecha, Nivel, Oro, Req, Reward) se muestran centradas correctamente usando anchos calculados.

Ajustes menores:
La fuente HUGE_FONT agregada para el título.
Las escenas menu y tutorial se dibujan correctamente en el bucle principal.
El botón "Volver" en el tutorial usa coordenadas adaptables.

# Version 0.3.0
Rediseño mayor: el juego pasó de ser una interfaz de botones a una visualización real del algoritmo Hooke-Jeeves.
Mapa de contorno de la función objetivo: se dibuja el paisaje de f(x, y) en tiempo real (zonas doradas = valores bajos, oscuras = valores altos). Sobre el mapa se muestran:

La trayectoria de puntos aceptados por el algoritmo (línea celeste).
El cuadrado de alcance de Δ alrededor del punto base.
Los 4 candidatos de exploración pulsando en amarillo (o grises si ya se exploraron).
El mejor punto actual pulsando en verde.
Los mínimos globales conocidos marcados con cruces.

Selección de función objetivo en el menú: ahora se elige entre Sphere (fácil), Himmelblau (media), Rastrigin (difícil) y Rosenbrock (experto). Cada tarjeta muestra una vista previa del contorno y su dificultad. El punto inicial se resamplea si nace demasiado cerca del mínimo, para que la partida no sea trivial.
Escala de calidad reformulada: antes se usaba calidad = 100 − f, lo que hacía que Rosenbrock (con valores de f en cientos) diera calidad 0 casi siempre. Ahora se usa calidad = 100 · exp(−f / escala) con una escala ajustada por función, y todas dan barras jugables de 0 a 100.
Fix del algoritmo: tras un salto de patrón (pattern_move) ahora se reinicia el estado de exploración. Antes las 4 direcciones quedaban marcadas como exploradas para siempre y bloqueaban el flujo. También se guarda el historial completo de puntos aceptados y el contador de evaluaciones de f.
Efectos de sonido sintetizados: martillo, sizzle de lava, splash de agua, campana de venta, fallo. Se generan en tiempo real con numpy (no requiere archivos de audio). Si numpy no está instalado, el juego corre igual en silencio.
Partículas: chispas al mejorar en el yunque, brasas ambientales flotando por la escena.
Atajos de teclado completos:

Flechas ←→↑↓: explorar en las 4 direcciones.
ESPACIO: repetir técnica (patrón).
R: reducir Δ.
ENTER: entregar la espada.
T o clic derecho: tienda.
F11: pantalla completa.

Interfaz: botones con estados hover / deshabilitado / sombra, paneles con títulos, línea de meta en la barra de calidad marcando el requisito. Layout reorganizado en 3 columnas (horno + cliente | mapa + estado | botones + recursos).
Tienda mejorada: se reintrodujo la compra manual de 5 lingotes por precio actual, y el costo del martillo escala con el nivel. Al vender una espada se regalan +3 lingotes extra.
Game Over con salida: pantalla final con botones "Reintentar" y "Salir" (antes solo salía). Se muestra la tabla del historial reciente.
Historial CSV rediseñado (historial.csv): ahora incluye función usada, resultado (VENDIDA / RECHAZADA / GAME OVER), valor final de f, calidad, oro y evaluaciones de f. Se registra al final de cada espada, no solo al morir.
Requisitos: Pygame (obligatorio) y NumPy (opcional, solo para sonido)
