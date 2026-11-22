# Dirección del producto · De TEU a decisiones del transportista

Fecha de decisión: 17 de noviembre de 2026. Hipótesis comercial por validar; no hay venta, ahorro ni precio confirmado.

## La decisión

Enfocar la primera versión en **empresas de autotransporte que retiran contenedores de importación en Manzanillo**, con un servicio principal: planeación de capacidad y margen de esos retiros. Podemos atender a varias empresas del mismo segmento; no significa trabajar exclusivamente para una. Tampoco significa ofrecer todos los servicios del puerto.

Comprador por entrevistar: dueño o responsable de operaciones. Usuario: quien cotiza y programa servicios. Producto propuesto: **ManzaDocker · Planeación y margen para transportistas**.

Propuesta: «Conoce cuánto te deja cada retiro, cuánto cuestan las esperas y qué capacidad tienes disponible; consulta el contexto del puerto para preparar el siguiente mes». La utilidad del pronóstico público es contexto mensual. La decisión económica requiere datos agregados de la operación del cliente.

## Dónde se mueve el dinero

El dinero relevante para este primer cliente entra por servicios efectivamente contratados y realizados. Sale por combustible, casetas, personal, mantenimiento, esperas y costos fijos. La unidad comercial es **un servicio de transporte**, no un TEU.

| Actor | Flujo económico que habría que medir | Decisión y encaje en el arranque |
|---|---|---|
| Transportista | Cobro por servicio menos costos variables, espera y costos fijos | Cotizar, aceptar servicios y prever capacidad. Primer segmento, porque ya existe acceso a entrevistados del sector en E0. Falta validar números. |
| SSA / OCUPA / otras terminales | Servicios de maniobra, patio, almacenamiento y otros conceptos específicos | Capacidad y operación de terminal. Posibles fuentes/contexto y entrevistas; propuesta comercial distinta, con datos internos que hoy no tenemos. |
| HAZESA | Servicios específicos de su terminal y patio, según tarifario y contrato | Evaluar después de confirmar qué servicio y carga interesa. No suponer que toda su actividad está explicada por nuestra serie TEU. |
| ASIPONA | Uso de infraestructura y servicios portuarios según conceptos tarifarios | Contexto y posible interlocutor institucional. No presumir acceso a contratación ni que sus ingresos son la suma de TEU multiplicada por una tarifa. |
| Ferromex | Servicios ferroviarios y capacidad intermodal | Requiere flujos ferroviarios, equipo y tiempos propios; segunda vertical, no parte de la primera versión. |
| APASCO / sector cementero | Confirmar razón social, carga, unidad facturable y problema | No asumir compatibilidad con contenedores. El directorio tarifario distingue una terminal de granel mineral/cemento; requeriría otra serie y otro cliente. |

Esta comparación es una **inferencia comercial del equipo**, no evidencia de que estas empresas quieran comprar.

## Primera versión: tres pantallas, un mismo cliente

1. **Mi operación:** demanda mensual propia, capacidad, tarifa por retiro, costo variable sin espera, horas de espera, costo/hora y costos fijos. Calcula servicios atendibles, faltante de capacidad, margen de contribución y resultado operativo estimado. El escenario está implementado en el tablero; las entradas se conservan solo en la sesión y no se publican.
2. **Contexto del puerto:** serie TEU, pronóstico mensual e intervalo, terminales de la serie y fecha de actualización. Ya existe la base E1. No convierte automáticamente un incremento del puerto en el mismo incremento de viajes del cliente.
3. **Mapa de contexto:** establecimientos de transporte, servicios relacionados y almacenamiento del DENUE y su procedencia. Integra la fuente especializada de E2. Los centros cartográficos no son accesos para camiones, rutas legales, clientes verificados ni tiempos de traslado.

La captura operativa semanal y la comparación por terminal son el siguiente desarrollo, **pendiente de un piloto con datos autorizados**. Hoy el simulador no optimiza rutas, asigna citas ni pronostica esperas. La primera versión no es una plataforma de compraventa de fletes ni un directorio de todos los servicios.

## Cálculo económico implementado

Todo se expresa en MXN sin IVA y para el mismo mes:

```text
servicios atendibles = mínimo(servicios solicitados, capacidad propia)
costo de espera por servicio = horas de espera × costo por hora
margen por servicio = tarifa − costo variable sin espera − costo de espera
resultado operativo estimado = servicios atendibles × margen
                              − costos fijos asignados − costo de la app
```

Es un escenario antes de impuestos e intereses; no una utilidad neta comprobada. Evitar doble contabilización: si el costo por hora incorpora combustible u operador, no volver a incluir esas partidas en el costo variable de espera. Los servicios de mayor tamaño o condiciones diferentes se calculan por separado. La app no debe recomendar aceptar operaciones con margen negativo.

**No se puede calcular el tamaño de mercado como TEU × precio de flete.** Un contenedor de 40 pies equivale a 2 TEU; transbordos, movimientos vacíos, dobles registros de operación y carga ferroviaria no equivalen uno a uno a retiros terrestres contratables. Las tarifas máximas publicadas tampoco acreditan el precio realmente cobrado ni el margen de una empresa.

## Cómo comprobar que alguien pagaría

Piloto propuesto de cuatro semanas con una transportista que acepte participar. No está acordado ni iniciado. Solicitar agregados por semana, terminal y tipo de servicio: servicios solicitados/realizados, capacidad, ingreso medio, costos, horas de espera y cancelaciones. Sin nombres, placas, correos, teléfonos, identificadores de contenedores ni recorridos de operadores.

Medir una línea base comparable y después el uso de la herramienta. Indicadores: margen por servicio, horas de espera por servicio, utilización de capacidad y servicios rechazados. Registrar cambios en mezcla de carga, demanda y horarios; una diferencia antes/después no prueba por sí sola causalidad. No atribuir ahorro al pronóstico sin un diseño que lo sostenga.

Preguntas para el comprador:

- ¿Qué decisión tomó la semana pasada con información insuficiente y cuánto le costó?
- ¿Quién autoriza el precio de un retiro y el gasto de software?
- ¿Qué costo por hora de espera pueden documentar sin duplicar partidas?
- ¿Con qué anticipación programan flota y qué datos agregados pueden compartir?
- ¿Qué resultado medido justificaría continuar pagando después del piloto?

Modelo de cobro por validar: suscripción por empresa con reporte y acompañamiento, sin fijar todavía precio. Cotizar después de medir uso y beneficio conservador; no presentar los costos del cliente, el ahorro hipotético o un monto arbitrario como disposición de pago confirmada. Hasta validar necesidad y precio, la aplicación es un prototipo comercial.

## Evidencia pública revisada

- [Servicios portuarios de ASIPONA](https://www.puertomanzanillo.com.mx/esps/2110587/servicios-portuarios.html): distingue maniobras y otros servicios; incluye SSA y OCUPA. El directorio no prueba demanda por software.
- [Servicios conexos](https://www.puertomanzanillo.com.mx/esps/2110588/servicios-conexos.html): distingue inspección, reparación, lavado y otros servicios. No se incorpora su contenido de contactos personales al pipeline.
- [Tarifas publicadas por ASIPONA](https://puertomanzanillo.com.mx/esps/0000207/tarifas.html): separa infraestructura, cesionarios y distintos servicios. Los tarifarios no son ingresos realizados.
- [Información oficial de SSA Manzanillo](https://www.ssamarine.mx/manzanillo.html): ya ofrece consulta, forecast, citas y portales de servicio. Nuestra propuesta debe complementar la economía del transportista; duplicar un portal público no constituye por sí solo valor diferencial.

La recomendación prioriza acceso al cliente y encaje con la evidencia existente, no una afirmación de que este sea el segmento más rentable de todo el puerto.
