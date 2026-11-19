# Mapa y costos por trayecto · Ampliación de ManzaDocker

## Comportamiento

El mapa conserva la selección original de dos establecimientos DENUE y agrega un catálogo de referencia de cinco organizaciones: OCUPA Puerto, Estacionamiento de OCUPA, Terminal de Servicios HAZESA, Transportes HAZESA y SSA México. Todas sus coordenadas proceden de registros reales del DENUE Colima. Sus nombres son etiquetas públicas de organizaciones identificadas; no se incorporan representantes, personas, contactos ni domicilios. La clasificación del catálogo es de referencia y no certifica que un punto sea un acceso de carga.

El usuario elige origen, hasta dos destinos y si el servicio incluye regreso. Puede consultar un recorrido vial o introducir kilómetros que haya validado para su operación. La introducción manual se aplica a un único destino y representa los kilómetros totales; no se duplican automáticamente al seleccionar regreso.

Los recorridos consultados son de **OSRM/FOSSGIS con perfil de automóvil**. No verifican peso, altura, acceso portuario, permisos, horarios ni tráfico en tiempo real. La app muestra distancias de referencia y ajuste de los puntos a la red vial; no ofrece navegación certificada para tractocamiones ni promete tiempos de espera.

## Conexión con el cálculo económico

```text
costo variable sin esperas = km del servicio × costo variable por km
                            + otros cargos que absorba la empresa
costo de espera = horas de espera × costo por hora
margen de contribución = cobro por servicio − costo sin esperas − costo de espera
```

El costo por kilómetro y los otros cargos son entradas del usuario, no tarifas obtenidas del mapa. Las horas de espera y el cobro se toman del escenario económico. Si faltan esas entradas, se conserva desconocido el costo total o margen; no se sustituye por cero. Los costos fijos y el precio de la app se descuentan únicamente en el escenario mensual.

El botón **Usar este costo sin esperas en el escenario mensual** actualiza solo el costo variable. La espera conserva su campo separado para evitar duplicarla. No modifica cantidad de servicios, capacidad, tarifas, costos fijos ni precio de la app. El usuario debe excluir del costo/km partidas ya consideradas como fijas.

Se comparan recorridos a lugares diferentes; menor costo estimado no significa que dos patios ofrezcan el mismo servicio, tengan disponibilidad o sean intercambiables. La app no asume convenios ni relaciones comerciales con las organizaciones mostradas.

## Procedencia y privacidad

El catálogo tiene una proyección mínima y explícita en `data/bronce/catalogo_logistico/`, con URL del ZIP oficial, SHA-256 del ZIP, CSV fuente, posición del registro, identificador DENUE, actividad, coordenadas y fecha de ingesta. El puntero en `data/referencias/catalogo_logistico.json` verifica el hash de ese archivo antes de usarlo. No se guarda el ZIP íntegro. La edición del directorio se distingue de la fecha de descarga.

Los recorridos y cálculos interactivos se mantienen en sesión y no se incorporan como nuevas filas históricas de Oro. Las ocho salidas de Oro existentes mantienen su verificación de linaje. El mapa actual no se añade a meses pasados del pronóstico.

La consulta externa envía únicamente las coordenadas de los puntos públicos del catálogo. No se envían costos, ingresos, nombres de clientes ni ubicaciones privadas introducidas libremente. FOSSGIS registra peticiones según su política. Una consulta por segundo como máximo por proceso, sin paralelismo, máximo dos destinos por acción, un intento y caché de 24 horas. No hay consultas automáticas al abrir el tablero. Para una operación comercial intensiva o validación de camiones se requiere un proveedor apropiado o infraestructura propia.

El mapa base utiliza CARTO/OpenStreetMap; los establecimientos proceden de INEGI/DENUE; los recorridos derivados de OSM conservan atribución ODbL. Son fuentes distintas.

## Fuentes

- [INEGI, descarga DENUE Colima](https://www.inegi.org.mx/contenidos/masiva/denue/denue_06_csv.zip) y [Términos de Libre Uso](https://www.inegi.org.mx/inegi/terminos.html).
- [OSRM/FOSSGIS: condiciones, privacidad y límite de uso](https://routing.openstreetmap.de/about.html).
- [OSRM, servicio de rutas](https://project-osrm.org/docs/v26.6.1/http.html).
- [OpenStreetMap, licencia y atribución](https://www.openstreetmap.org/copyright).

## Verificación

Pruebas de catálogo e integridad, error del motor, ida y regreso solicitados como tramos completos, costos con campos desconocidos y transferencia sin doble contabilización. Las pruebas de interfaz y CI usan respuestas sintéticas o kilómetros manuales; no consultan la API pública. La comprobación real del servicio se documenta por separado y sus parámetros económicos se identifican como ficticios.

Esta ampliación se desarrolla después del tag `e2` publicado. No reescribe esa etiqueta ni declara terminado el piloto comercial o el paquete de las tres materias.
