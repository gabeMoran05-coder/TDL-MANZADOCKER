# Prompt de trabajo para Emilio · Cierre y mejora de E2

Repositorio: https://github.com/gabeMoran05-coder/TDL-MANZADOCKER

Estado comprobado el 17 de noviembre de 2026: el tag `e2` apunta a `f1fb6d9` y la implementación está en `codex/e2-fuente-linaje`. `main` mantiene la captura E1; integrar la rama E2 sigue pendiente. El tablero público no tiene URL verificada. Existe un prototipo local y no debe presentarse su enlace localhost como publicación para los docentes.

## Prompt listo para copiar

Actúa como Emilio y continúa la entrega E2 de Ingeniería de Datos del observatorio ManzaDocker, ponderada con 20 % de la Unidad 4. Usa este repositorio y revisa el PDF del proyecto y los cambios de Gabriel antes de editar. Conserva el trabajo existente y sus atribuciones.

La base ya implementada en `codex/e2-fuente-linaje`, tag `e2`, incluye: DENUE Colima minimizado antes de Bronce; GeoPandas y mapa; ocho productos Oro con 522 registros y manifiesto de linaje; declaración de ética; ficha y relatoría E2; simulador de capacidad y margen. Hay 71 pruebas aprobadas, cobertura 95.48 % y CI aprobada, incluido gitleaks y pip-audit. Estos números corresponden a esa versión, no se deben copiar como resultado de una nueva ejecución sin comprobarlos.

Trabaja por prioridades:

1. **Revisar e integrar.** Compara la rama E2 con el `main` actualizado, que sigue recibiendo capturas diarias. Integra mediante el proceso de revisión y CI del equipo; conserva los datos y las nuevas bitácoras de Gabriel. No desactives protecciones ni sobrescribas avances del compañero. La integración anterior no creó pull request porque la conexión de GitHub respondió 403 por permisos; la rama sí está subida. Revisa también los issues docentes vigentes.

2. **Mejorar la utilidad de DENUE y del mapa.** La selección conservadora actual produce solo dos establecimientos y no representa el mercado. Revisa los filtros de municipio, actividad y forma societaria; amplía o justifica la muestra con evidencia. Si necesitas incluir más unidades, diseña anonimización o agregación antes de persistir, conservando cero datos personales. No guardes nombres, razones sociales, contactos ni domicilios particulares. Las cuatro celdas actuales son de estudio, no zonas oficiales; considera una unión espacial con polígonos oficiales útiles para la operación y muestra fecha de edición, fecha de ingesta, fuente y límites. No inventes establecimientos ni infieras demanda de software por aparecer en DENUE.

3. **Precisar el linaje.** Hoy DENUE se enlaza uno a uno, pero E1 combina referencias por periodo con grupos amplios de dependencias válidas. Haz que se puedan identificar las filas Bronce que realmente explican cada registro y sus transformaciones, incluyendo agregaciones de Banxico, imputaciones, ventanas, escalas y pronóstico. Conserva URL, fecha real de ingesta, selector, versión de transformación y SHA-256. No sustituyas ingesta por fecha del manifiesto. Verifica revisiones de fuente, pronósticos desactualizados, registros eliminados, datos alterados y reproducción en un checkout limpio. Los conjuntos amplios actuales no deben describirse como linaje exacto por celda.

4. **Cerrar ética y condiciones de uso.** Revisa `docs/etica-datos.md` y la evidencia HTTP/robots por fuente. INEGI y Banxico tienen condiciones documentadas; la autorización comercial de los informes ASIPONA no se ha acreditado. Sustenta el uso permitido con evidencia o adapta la fuente y lo que se publica. No declares licencia abierta, autorización o consentimiento inexistentes. Mantén atribución, minimización, análisis de sesgos, pausas y reintentos. Corrige los acentos dañados o caracteres `?` en documentación y verifica UTF-8.

5. **Publicar y comprobar la app.** Despliega la versión integrada en una cuenta autorizada, por ejemplo Streamlit Community Cloud, y entrega una URL pública real. Comprueba desde fuera de la computadora de Gabriel que funcionan pronóstico, mapa, datos de procedencia y escenarios; actualiza README y `docs/E2/ENTREGA.md`. El enlace local `http://127.0.0.1:8501` solo sirve en la computadora que ejecuta Streamlit.

6. **Mantener una dirección comercial concreta.** El segmento inicial son transportistas que retiran contenedores de importación, con varias empresas posibles del mismo tipo. El producto ayuda a cotizar y planear capacidad y margen; TEU es contexto mensual y no equivale a viajes, dinero, citas ni esperas diarias. El simulador ya existe, pero faltan datos agregados autorizados de una transportista, validar necesidad, comprador, costos y precio. Prepara un piloto y un indicador de éxito medible; no presentes ahorros hipotéticos, clientes, entrevistas o ventas como reales. SSA, OCUPA, HAZESA, ASIPONA y Ferromex requieren evaluar problemas y datos distintos antes de abrir otras líneas del producto.

7. **Actualizar evidencia y registros.** Completa ficha y relatoría con lo que efectivamente hagas, sus seis preguntas, fechas, decisiones, incidencias, enlaces y uso de IA. Registra tu propio trabajo en `calidad/tiempo-emilio.csv` y `calidad/defectos-emilio.csv`. Gabriel ya tiene registros de su trabajo asistido; no añadas tus horas a sus archivos ni inventes tiempos no medidos. Verifica que toda la documentación coincida con el código, los datos y el estado de publicación.

8. **Verificar y preparar la entrega.** Ejecuta los checks correspondientes a tus cambios: pipeline sin red desde Bronce versionado, linaje, pruebas, Ruff, pip-audit y gitleaks; conserva resultados nuevos y exige CI aprobada. Mantén al menos el umbral configurado de cobertura (90 %). Actualiza los conteos automáticamente si cambian los datos. El tag `e2` ya está publicado: prepara el cierre y coordina con Gabriel la etiqueta final, sin reescribirla silenciosamente. El formulario oficial no se ha proporcionado ni se ha registrado; entrega el enlace correcto para que se registre cuando se tenga el formulario.

Al terminar, entrega un resumen de cambios, URL pública comprobada, commits y comprobaciones, pendientes reales y enlace de la versión de entrega. No declares que está completo si falta un requisito.

## Si también te corresponde el paquete de las tres materias

Estos pendientes son adicionales a Ingeniería de Datos:

- **Estadística:** ejecutar el factorial 2³ real con aleatorización y al menos dos réplicas por tratamiento; diseño de dos factores con interacción; matrices completo/fraccionado y alias; ANOVA, residuos y corrida de confirmación. El experimento de ingeniería se hace sobre archivos o servicios propios, sin saturar sitios ajenos.
- **Calidad:** evaluación medida ISO/IEC 25010 e ISO/IEC 25012; antecedentes normativos; auditoría cruzada real con el equipo asignado, evidencia, severidad y recomendaciones. Las pruebas existentes no sustituyen estas evaluaciones y no se puede inventar una auditoría de terceros.

Conserva estos estados separados en la ficha. La petición principal de esta revisión es E2 de Ingeniería de Datos.
