/**
 * Funciones para cambiar las opciones de marca y modelo de panel dependiendo de si es bifacial o no
 */
function cambiarMarcaPanel(multi = ''){
    let bifacial = $("#bifacial"+multi).val();
    let texto = '';
    for (i=0 ; i < nombreCompaniaPanel.length; i++){
        if(nombreCompaniaPanel[i].split(";")[1] === bifacial)
            texto += '<option value="'+nombreCompaniaPanel[i].split(";")[0]+'">'+nombreCompaniaPanel[i].split(";")[0]+'</option>';
    }
    $("#marcaPanel"+multi).html('<option value="">-- Elige una marca --</option>'+texto); // Reiniciar opciones
    $("#modeloPanel"+multi).html('<option value="">-- Elige un modelo --</option>'); // Reiniciar opciones
}

/**
 * Función para cambiar las opciones de modelo de panel dependiendo de la marca y si es bifacial o no
 */
function cambiarModelosPanel(multi=''){
    const marcaSeleccionada = $("#marcaPanel"+multi).val();
    let bifacial = $("#bifacial"+multi).val();
    let texto='';
    $("#modeloPanel"+multi).html('<option value="">-- Elige un modelo --</option>'); // Reiniciar opciones
    for (i=0 ; i < datosPaneles.length; i++){
        if(datosPaneles[i]["Manufacturer"] === marcaSeleccionada && datosPaneles[i]["BIPV"] === bifacial){
            texto += '<option value="'+i+'">'+datosPaneles[i]["Model Number"]+'</option>';

        }
    }
     $("#modeloPanel"+multi).append(texto); // Reiniciar opciones

}


/***
 *
 * se utiliza para mostrar el cuadro de dialogo con los datos a introducir de fecha, paneles.. para el calculo y el boton de calcular
 */
function DialogCalcularDatos() {
    $("#mensaje-embalse").css({"display":"none"});
    $("#dialogo-multicriterio").dialog("open");
    $(".solo-anio").css({"display": "grid"});
    $(".nombre-analisis input").focus();

}
/***
 * Funcion que se llama desde el boton para calcular los datos de los embalses usando multicriterio
 */
async function CalcularDatos()  {

    let  datos={};

    //El area del modelo lo devuelve en porcentaje no en metros como en la otra funcion
    datos["nombre"] = $("#nombre-analisis").val();
    if ( datos["nombre"] === "") {
        $("#mensaje-embalse").html("Por favor, introduce nombre para guardar el estudio.");
        $("#mensaje-embalse").css({"display": "block"});
        return -1;
    }
    datos["metodo"] = $("input[name='metodo']:checked").val();
    datos["ponderacion"] = $("input[name='ponderacion']:checked").val();
    datos["cuenca"] = cuenca;


    let mensaje = true;
    if (datos["ponderacion"]=="AHP")
        mensaje = false;

    const criterios = await calculoCriterios(mensaje);
    if (criterios == -1)
        return;
    else
        datos["criterios"] = criterios;

    if (datos["ponderacion"]=="AHP" || datos["ponderacion"]=="MetodoA") {
        datos["AHP"] = await metodoAHP(datos["ponderacion"]);
        console.log(datos["AHP"]);
        if (datos["AHP"]==-1)
            return;
    }
    //DialogCalcularDatos();
    datosPanelesMulticriterio = recuperarDatosPanelesMulticriterio();
    if (datosPanelesMulticriterio == -1)
        return;
    datos["paneles"] = datosPanelesMulticriterio;
    datos["paneles"]["horaDelAnio"] = 10; //valor por defecto se usa en embalse y ahora espera un valor
    $(".loader").css({"display":"block"});
    //console.log(datos);
    const response = await fetch("/calcularEmbalsesAvila", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        // En jQuery, 'data' con un objeto se envía como form-urlencoded por defecto
        body: JSON.stringify(datos)
    });

    const data = await response.json();

    $(".loader").css({"display": "none"});
    if (!response.ok){
        $("#mensaje-embalse").html("Error:"+ data.geoJson);
        $("#mensaje-embalse").css({"display": "block"});
        return;
    }
    console.log(data.geoJson);
    pintarResultados(data);
    $("#dialogo-multicriterio").dialog("close");
}

/**
 * Recupera los datos de los paneles a partir de los datos introducidos en el formulario del cuadro de dialogo
 * @returns {{fechaInicio: string, fechaFin: string, numPaneles: number, orientacion: *|jQuery, inclinacion: *|jQuery, panel: *, area, modeloSeleccionado: *|jQuery}}
 */
function recuperarDatosPanelesMulticriterio(){
    // Obtener los valores del formulario
    let fechaInicio= "01/01/"+$("#anio-multi").val();
    let fechaFin = "31/12/"+$("#anio-multi").val();
    let numPaneles=-1;

    const orientacion = $("#orientacion-multi").val();
    const inclinacion = $("#inclinacion-multi").val();
    const ocupacion = $("#ocupacion-multi").val();
    const numDePanel = $("#modeloPanel-multi").val();
    const panelSeleccionado = datosPaneles[numDePanel];
    //uso slice para quitar el -multi del id
    const modeloSeleccionado = $('input[name="modelo-solar-multi"]:checked').attr('id').slice(0,-6);


    // Validar que todos los campos estén completos
    if ( !orientacion || !inclinacion || !numDePanel || !ocupacion) {
        $("#mensaje-embalse").html("Por favor, complete todos los campos antes de calcular.");
        $("#mensaje-embalse").css({"display": "block"});
        return -1;
    }

    if (orientacion < 0 || orientacion > 360) {
        $("#mensaje-embalse").html("La orientación debe estar entre 0 y 360 grados.");
        $("#mensaje-embalse").css({"display": "block"});
        return -1;
    }

    if (inclinacion < 0 || inclinacion > 90) {
        $("#mensaje-embalse").html("La inclinación debe estar entre 0 y 90 grados.");
        $("#mensaje-embalse").css({"display": "block"});
        return -1;
    }
    const datos={
        fechaInicio: fechaInicio,
        fechaFin: fechaFin,
        numPaneles: numPaneles,
        orientacion: orientacion,
        inclinacion: inclinacion,
        panel: panelSeleccionado,
        area: ocupacion/100,
        modeloSeleccionado: modeloSeleccionado
    }
    return datos;
}

/**
 * Devuelve si el checkbox esta presionadao o no
 * @param nombre nombre del checkbox a comproba
 * @returns {string} Si o No dependiendo si esta o no pulsado
 */
function valorInput(nombre){
     if($(nombre).is(':checked')) {
         return 'Si';
     }else
         return 'No'
}

/**
 * Recupera todos los valores de los criterios de los  y comprueba si la suma de los valores es 1
 * @returns {Promise<{}|number>} devuelve los criterios o -1 si el usuario no ha metido la
 * suma de los criterios a 1 y quiere modificarlo
 */
async function  calculoCriterios(mensaje){

    let criteriosValores = [];
    let criteriosPesos = [];
    for (let i=0; i< criteriosId.length; i++) {
        const valorCriterio = valorInput("#" + criteriosId[i]);
        const nombreCriterioPeso = "#input" + criteriosId[i];
        criteriosValores.push(valorCriterio);
        criteriosPesos.push(Number($(nombreCriterioPeso).val()));
    }
    const datos={}
    datos['Criterios'] = criteriosValores;
    datos['OmegaC'] = criteriosPesos;

    error = comprobarPesos(criteriosValores, criteriosPesos);
    if (error == ""){
        return datos;
    }else{
        if (mensaje) {
            $("#dialog-message").html(error);
            const result = await showDialog();
            if (result) {
                return datos;
            } else {
                return -1;
            }
        }else{
            return datos;
        }
    }
}
/*********
 Función para comprobar si los pesos de los criterio, subcriterios y movilidad de  estan bien.
 ********/
function comprobarPesos(criteriosValores, criteriosPesos){
    let sumaCritriosPesos=0;
    let sumaSubcriteriosPesos = [0, 0, 0, 0];
    for ( let i = 0; i < criteriosValores.length; i ++){
        if (criteriosValores[i] == 'Si') {
            sumaCritriosPesos += Number(criteriosPesos [i]);


        }
    }
    sumaCritriosPesos = sumaCritriosPesos.toFixed(2);
    let mensajeError="";
    if (sumaCritriosPesos !=1 ){
        mensajeError =" La suma de los pesos de los criterios tiene que ser igual a 1<br>";
    }

    return mensajeError;
}

/**
 * Funcion para mostrar las tablas de los  para el metodo jerarquizado
 **/
async function metodoAHP(metodo){
    if (metodo == "AHP") {
        const result = await showAHP(metodo);
        if (result) {
            /**recupero todos los datos de las tablas*/
            datosConsumo = recuperarDatosTabla();
            return datosConsumo;
        } else {
            return -1;
        }
    }else{
        datos = recuperarDatosTabla();
        return datos;
    }


}

/**
 * Muestra un cuadro de dialogo con las tablas de los metodos jerarquizados de los
 * @returns {Promise<unknown>}
 */
function showAHP(metodo) {
      return new Promise((resolve, reject) => {
        calcularDatosTabla();
        console.log("show AHP");
        if(metodo=="AHP") {
            $("#dialog-jerarquizado").dialog({
                modal: true,
                title: "Comprueba los datos de la tabla",
                autoOpen: true,
                width: '80vw',
                buttons: {
                    Si: function () {
                        $(this).dialog("close");
                        resolve(true);
                    },
                    No: function () {
                        $(this).dialog("close");
                        resolve(false);
                    }
                }
            });
        }else{
            resolve(true);
        }
      });
    }


    /**
    * Funcion para buscar los criterios del menu criterios/restricciones y muestrar u ocultar los input de las tablas de lso
    **/
function calcularDatosTabla(){

        const nombreBotones=    ['tbCriterios']
        $("#dialog-jerarquizado .tabla input").prop("disabled",false);
        /*Bloqueo las celdas por debajo de la diagonal de la tabla de criterios*/

        for (i = 0; i< criteriosId.length; i++) {
            for (k = 0; k< criteriosId.length; k++) {
                let fila ="#dialog-jerarquizado .tbCriterios .fil"+(i+2)+" .cel"+(k+2)+ " input";
                $(fila).val(valuesCriteriosAHP[i][k]);
                if (k <= i){
                    $(fila).prop("disabled",true);

                }
            }
        }

        /*pongo en rojo las filas y columnas deshabilitadas de los criterios*/
        $("#dialog-jerarquizado>input").prop("disabled",false);
        $("#dialog-jerarquizado input").removeClass("oculto");
        for (i = 0; i< criteriosId.length; i++){
            let criterioValor =valorInput("#" + criteriosId[i]);
            if (criterioValor =="No"){
                let fila ="#dialog-jerarquizado .tbCriterios .fil"+(i+2)+ " input";
                let cel ="#dialog-jerarquizado .tbCriterios .cel"+(i+2)+ " input";
                $(fila).prop("disabled",true);
                $(cel).prop("disabled",true);
                $(fila).addClass("oculto");
                $(cel).addClass("oculto");
                $(fila).val("-1");
                $(cel).val("-1");
                const nombreBtn="."+nombreBotones[i+1];
                $(nombreBtn).prop("disabled", true);
            }
        }


    }
/**
 * Funcion para que al cambiar un valor de la tabla se cambien su opuesto por el inverso
 * @param nombreTabla nombre de la tabla en la que se ha cambiado el valor
 * @param fila fila donde se encuentra el valor
 * @param columna columna donde se encuentra el valor
 */
function cambiarValorCelda(nombreTabla, fila, columna){
        const nombreCelda="."+nombreTabla+" .fil"+fila+" .cel"+columna+ " input";
        const nombreCeldaCambio="."+nombreTabla+" .fil"+columna+" .cel"+fila+ " input";

        const valorCelda =$(nombreCelda).val();

        if (valorCelda.length>0) {
            var fraccionSplit = valorCelda.split("/");

            if (fraccionSplit.length > 1 ){
                var numerador = parseFloat(fraccionSplit[0]);
                var denominador = parseFloat(fraccionSplit[1]);
                if (fraccionSplit[1].length >0)
                    $(nombreCeldaCambio).val(fraccionSplit[1] +"/"+ fraccionSplit[0]);
                else
                    $(nombreCeldaCambio).val("1/" +fraccionSplit[0]);
            }else {
                $(nombreCeldaCambio).val("1/" + valorCelda);
            }
        }else
            $(nombreCeldaCambio).val("");
    }
/**
 * Muestra un  dialogo cuando la suma de los criterios es diferente de 1
 * @returns {Promise<unknown>} devuelve true si el usuario quiere modificar los criterios porque esten mal
 * y false en el caso de que quiera continuar
 */

function showDialog() {
      return new Promise((resolve, reject) => {

        $("#dialog-message").dialog({
			modal: true,
            title: "Desea Continuar",
            autoOpen: true,
            width: 'auto',
            height: 200,
			buttons: {
				Si: function() {
					$( this ).dialog("close");
					resolve(true);
				},
				No: function() {
					$( this ).dialog( "close" );
                    resolve(false);
				}
			}
		});
      });
    }

/**
 * Funcion para mostrar la tabla del metodo jerarquizado que se pincha en el boton dee los
 * @param nombre nombre de la tabla a mostrar
 */
function mostrarTabla(nombre){
        $("#dialog-jerarquizado .tabla").hide();
        const nombreTabla ="#dialog-jerarquizado ."+nombre;
        const nombreboton ="#dialog-jerarquizado .btTabla"+nombre.substring(2);
        $(nombreTabla).show();

        $("#dialog-jerarquizado>input").removeClass("active");
        $(nombreboton).addClass("active");
    }


/**
* Funcion para recuperar los datos escritos en las tablas del criterio AHP
**/
function recuperarDatosTabla(){

    /*recopilo los datos de la tabla criterios*/
    let valores = [];
    let fila="";

    for (i = 0; i< criteriosId.length; i++){
        if (i < criteriosId.length-1)
            fila +="."+nombreTablas[0]+" .fil"+(i+2)+", ";
        else
            fila +="."+nombreTablas[0]+" .fil"+(i+2);
    }

    $(fila).each(function() {
        let valoresfila = [];
        $(this).find("input[type='text']").each(function() {
            valoresfila.push(Number(eval($(this).val())));
        });
        valores.push(valoresfila);
    });

    let datostabla={}
    datostabla['Criterios'] = valores
    return  datostabla;

}


/**
 * Funcion para crear la tabla para el dialogo jerarquizado que se mostrara al elegir el metodo de ponderación AHP
 */
function crearTablaDialogoJerarquizado(){
    //creamos los botones de la parte superior
    let html = "";
    // Botón criterios
    html += `<input type="button" value="Tabla Criterios" class="tablatbCriterios active" onclick="mostrarTabla('tbCriterios')">`;
    /*criteriosNombre.forEach((c,i)=>{
        let clase =  nombreTablas[i+1];
        let claseTabla = "tabla"+nombreTablas[i+1];
        html += `<input type="button" value="Tabla ${c}" class="${claseTabla}" onclick="mostrarTabla('${clase}')">`;
    });*/
    //creamos la tabla criterios
    html += crearTabla("tbCriterios", criteriosNombre);
    //creamos el resto de tablas
    /*criteriosNombre.forEach((c,i)=>{
        let clase = nombreTablas[i+1];
        if(subcriteriosNombre[i])
            html += crearTabla(clase, subcriteriosNombre[i]);
    });*/

    $("#dialog-jerarquizado").html(html);
}


/**
 * creamos una tabla para el dialogo jerarquizado, hay que crear una por cada criterio
 * @param id identiticativo de la tabla
 * @param nombres nombre de la categoria o subcategoria
 * @returns {string} html de la tabla
 */
function crearTabla(id, nombres) {

    let html = `<div class="tabla ${id}">`;

    // Cabecera
    html += `<div class="fil1">`;
    html += `<div class="cel1">&nbsp;</div>`;
    nombres.forEach((nombre, i) => {
        html += `<div class="cel${i+2}">${nombre}</div>`;
    });

    html += `</div>`;

    // Filas
    for(let i=0;i<nombres.length;i++){
        html += `<div class="fil${i+2}">`;
        html += `<div class="cel1">${nombres[i]}</div>`;
        for(let j=0;j<nombres.length;j++){
            let evento="";
            if(j>i){
                evento=`onkeyup="cambiarValorCelda('${id}','${i+2}','${j+2}')"`
            }
            html+=`
                <div class="cel${j+2}">
                    <input type="text" size="5" value="1" ${evento}>
                </div>
            `;
        }
        html+=`</div>`;
    }

    html+=`</div>`;

    return html;
}

/*****
 Los valores devueltos por index.py contienen un json con valores de los  ordenados
 con pintarResultados pinta esos valores en el mapa
 @param data datos a pintar que contienen las coordenadas de los municipios y los valores para pintar cada municipio de un color
******/
async function pintarResultados(data){
    //console.log(data);

    const valores=data["geoJson"];

    if (map.getSource('resultado_source')) {
        // Si la capa ya está añadida, la eliminamos
        if (map.getLayer('resultado'))
            map.removeLayer('resultado'); // Elimina la capa
        map.removeSource('resultado_source'); // Elimina la fuente
    }else{
        botones=$(".resultadoEmbalses").html();
    botones += "<div class=\"vc-toggle-container\">\n" +
        "   <div><span class=\"text\">Resultados</span> <label class=\"vc-switch\">\n" +
        "        <input type=\"checkbox\" class=\"vc-switch-input\" id='resultadoEmbalse' onchange=\"cambioEstado('resultadoEmbalse','resultado');\" checked>\n" +
        "        <span class=\"vc-switch-label\" data-on=\"Si\" data-off=\"No\"></span>\n" +
        "        <span class=\"vc-handle\"></span>\n" +
        "    </label>\n" +
        "   </div>\n"+
        "</div>" +
        "<div><div><img src='./static/img/resultado0.png' width='20' height='20' alt='Resultados Criterios'> Best</div>"+
        "<div><img src='./static/img/resultado1.png' width='20' height='20' alt='Resultados'> Strongly Suitable</div>"+
        "<div><img src='./static/img/resultado2.png' width='20' height='20' alt='Resultados'> Moderately Suitable</div>"+
        "<div><img src='./static/img/resultado3.png' width='20' height='20' alt='Resultados'> Low Suitable</div>"+
        "<div><img src='./static/img/resultado4.png' width='20' height='20' alt='Resultados'> Very Low Suitable</div></div>";
    //botones += addButtonsAirport('Resultado', 'resultadoAirports', 'resultado_','/static/img/plane.png', 'visible');
    $(".resultadoEmbalses").html(botones);
    $(".resultadoEmbalses").css({"display":"flex"});
    }
    map.addSource('resultado_source', {
        type: 'geojson',
        data: valores
    });

    map.addLayer({
        'id': 'resultado',
        'type': 'circle',
        'source': 'resultado_source',
        paint: {
            "circle-radius":  [
              "match",
              ["get", "orden"],
              0, 8,
              1, 6,
              2, 5,
              4
            ],
            "circle-color": [
              "match",
              ["get", "orden"],
              0, "#2ca02c",   // verde
              1, "#1f77b4",   // azul
              2, "#ffff00",   // amarillo
              3, "#ff7f0e",   // naranja
              4, "#d62728",   // rojo
              "#cccccc"       // valor por defecto
            ]
          }
        //'filter': ['==', 'Categoria', 1]
    });

    map.setLayoutProperty('resultado','visibility', 'visible');

}

/**
 * Función para mostrar u ocultar los campos de fecha y número de paneles dependiendo de si se quiere calcular el número de paneles o no
 */
function calcularPaneles(){
    if ($("#checkCalcularPaneles").is(':checked')) {
        $(".fecha").hide();
        $(".num-paneles").hide();
        $(".solo-anio").css({"display": "grid"});
    }else{
        $(".fecha").show();
        $(".num-paneles").show();
        $(".solo-anio").css({"display": "none"});
    }
}
/**
 * Función para cambiar el rango de fechas del calendario dependiendo del año que se introduzca
 * solo se usa cuando se marca calcular el numero de paneles
 */
function cambioAnio(){
    const fechaInicio = flatpickr.parseDate("01/01/" +$("#anio").val(), "d/m/Y");
    const fechaFin = flatpickr.parseDate("31/12/" +$("#anio").val(), "d/m/Y");
    calendarTime.set("minDate", fechaInicio);
    calendarTime.set("maxDate", fechaFin);
}

/**
 * Función para calcular la producción de un embalse en base a los datos introducidos en el formulario
 * @param longitud
 * @param latitud
 * @param area
 * @returns {Promise<void>}
 */
async function calcularProduccionMasaDeAgua(longitud, latitud, area) {
    // Obtener los valores del formulario
    let fechaInicio;
    let fechaFin;
    let numPaneles;
    let inicioAno;
    let horaDelAnio;
    if ($("#checkCalcularPaneles").is(':checked')) {

        fechaInicio = "01/01/"+$("#anio").val();
        fechaFin = "31/12/"+$("#anio").val();
        inicioAno = new Date($("#anio").val(), 0, 1, 0, 0, 0);
        numPaneles = -1;
        const fechaSeleccionada =flatpickr.parseDate($(".calendar-dia-hora").val(), "d/m/Y H:i");
        const diferenciaMs =fechaSeleccionada - flatpickr.parseDate(inicioAno, "d/m/Y H:i");
        if (inicioAno.getFullYear() != fechaSeleccionada.getFullYear() ) {
            $("#mensaje-embalse-produccion").html("Los años de las fechas son diferentes");
            $("#mensaje-embalse-produccion").css({"display": "block"});

            return;
        }
        horaDelAnio = Math.floor(diferenciaMs / (1000 * 60 * 60)) + 1;
    }else{
        fechaInicio = $("#fecha").val().split(" to ")[0];
        fechaFin = $("#fecha").val().split(" to ")[1];
        numPaneles = $("#numPaneles").val();

        const diferenciaMs =flatpickr.parseDate($(".calendar-dia-hora").val(), "d/m/Y H:i") -  flatpickr.parseDate(fechaInicio, "d/m/Y H:i");
        horaDelAnio = Math.floor(diferenciaMs / (1000 * 60 * 60)) + 1;
    }
    const orientacion = $("#orientacion").val();
    const inclinacion = $("#inclinacion").val();
    const ocupacion = $("#ocupacion").val();
    const numDePanel = $("#modeloPanel").val();
    const panelSeleccionado = datosPaneles[numDePanel];
    const modeloSeleccionado = $('input[name="modelo-solar"]:checked').attr('id');

    // Validar que todos los campos estén completos
    if (!fecha || !numPaneles || !orientacion || !inclinacion || !numDePanel || !ocupacion) {
        $("#mensaje-embalse-produccion").html("Por favor, complete todos los campos antes de calcular.");
        $("#mensaje-embalse-produccion").css({"display": "block"});
        return;
    }

    // Validar rangos
    if (numPaneles < 1 && numPaneles != -1) {
        $("#mensaje-embalse-produccion").html("El número de paneles debe ser mayor a 0.");
        $("#mensaje-embalse-produccion").css({"display": "block"});
        return;
    }

    if (orientacion < 0 || orientacion > 360) {
        $("#mensaje-embalse-produccion").html("La orientación debe estar entre 0 y 360 grados.");
        $("#mensaje-embalse-produccion").css({"display": "block"});
        return;
    }

    if (inclinacion < 0 || inclinacion > 90) {
        $("#mensaje-embalse-produccion").html("La inclinación debe estar entre 0 y 90 grados.");
        $("#mensaje-embalse-produccion").css({"display": "block"});
        return;
    }
    const datos={
        fechaInicio: fechaInicio,
        fechaFin: fechaFin,
        numPaneles: numPaneles,
        orientacion: orientacion,
        inclinacion: inclinacion,
        panel: panelSeleccionado,
        longitud: longitud,
        latitud: latitud,
        area: area*ocupacion/100,
        modeloSeleccionado: modeloSeleccionado,
        horaDelAnio: horaDelAnio
    }
    $(".loader").css({"display":"block"});

    const responseProduccion = await fetch('/calcular_produccion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
    })
    const dataProduccion = await responseProduccion.json();
    if (!responseProduccion.ok) {
        $("#mensaje-embalse-produccion").html("Error: " + (dataProduccion.info || "Error al calcular la producción"))
            .css("display", "block");
        $(".loader").css({"display": "none"});
        return;
    }

    window.location.href = `/calcular_produccion_vista?id=${dataProduccion.resultado_id}`;

}


async function pintarResultadosAnalisis(url, cuenca){

    const url_geojson = url.replace(".csv",".geojson");
    const response = await fetch(url_geojson);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const resultadosDisco = await response.json();
    let data=[];
    data["geoJson"] =resultadosDisco;
    pintarResultados(data);
    if (cuenca == "Todos")
        map.setFilter("Rios-layer", null);
    else
        map.setFilter("Rios-layer", ["==", ["get", "cuenca"], cuenca]);
    $("#rio"+cuenca).attr("checked","checked");
}