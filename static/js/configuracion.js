function mostrarMapa(){
     map = new maplibregl.Map({
        container: 'map',
        style: "https://api.maptiler.com/maps/positron/style.json?key="+accessToken,
        center:  [-4.704075, 40.655347],//[-87.61694, 41.86625],
        zoom: 8,
        pitch: 40,
        bearing: 10,
        antialias: true,
        preserveDrawingBuffer: true
    });

    map.once('style.load', () => {
            loadLayers();
    });
    menuPrincipal();
    changeStyleMap();
}
/**
 * Funcion para configurar un dialogo de mensaje para poder visualizar avisos o datos de capas
 */
$(document).ready(function(){
    $("#dialogo-mensaje").dialog({
        modal: true,
        title: "Informacion",
        autoOpen: false,
        width: 'auto',
        buttons: {
            Cerrar: function () {
                $(this).dialog("close");

            }
        }
    });
    /**
     * Esta funcion permite que el calendario de flatpickr se pueda usar dentro de un dialogo de jquery ui,
     * ya que por defecto sale un error en la consola aunque si que funciona correctamente
     */
    $.widget("ui.dialog", $.ui.dialog, {
        _allowInteraction: function(event) {
            if ($(event.target).closest(".flatpickr-calendar").length) {
                return true;
            }
            return this._super(event);
        }
    });
    $("#dialogo-multicriterio").dialog({
        modal: true,
        title: "Informacion",
        autoOpen: false,
        width: 'auto',
        buttons: {
            Cerrar: function () {
                $(this).dialog("close");

            }
        }
    });
    $("#dialogo-embalse").dialog({
        modal: true,
        title: "Informacion",
        autoOpen: false,
        width: 'auto',
        buttons: {
            Cerrar: function () {
                $(this).dialog("close");

            }
        }
    });


    calendarTime = flatpickr("#dia-hora", {
            enableTime: true,
            dateFormat: "d/m/Y H:i",
            time_24hr: true,

        });
    const calendar = flatpickr("#fecha", {
        mode: "range",
        dateFormat: "d/m/Y",
        ariaDateFormat: "Y-m-d",
        clickOpens: true,
        allowInput: false,
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                // Habilitamos el input
                calendarTime._input.disabled = false;
                // Pasamos fechas individuales, NO el array completo
                calendarTime.set("minDate", selectedDates[0]); // Fecha inicio
                calendarTime.set("maxDate", selectedDates[1]); // Fecha fin
            }
        }
    });


});

function changeStyleMap(){
   const inputs = $('#botones-terreno input');
    for (const input of inputs) {
        input.onchange = (layer) => {
            $(".loader").fadeIn(300);
            const layerId = layer.target.id;
            if(layerId === 'google') {
                //map.setStyle( "https://api.maptiler.com/maps/hybrid/style.json?key="+accessToken);
                // Opción para Google Maps Satelital
                map.addSource('google-satellite', {
                    type: 'raster',
                    tiles: [
                        'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                    ],
                    tileSize: 256
                });
                map.addLayer({
                    id: 'google-satellite-layer',
                    type: 'raster',
                    source: 'google-satellite',
                    minzoom: 0,
                    maxzoom: 22
                });
                map.moveLayer('google-satellite-layer', 'parallels'); // Mover la capa antes de la primera que ponemos que son los paralelos
            } else {
                // Eliminar capa de Google si existe
                if (map.getLayer('google-satellite-layer')) {
                    map.removeLayer('google-satellite-layer');
                    map.removeSource('google-satellite');
                }
                map.setStyle("https://api.maptiler.com/maps/" + layerId + "/style.json?key=" + accessToken);
                //la primera vez que se cambia el estilo del mapa no carga las capas, por eso se añade un retardo
                setTimeout(() => {
                        loadLayers();
                        map.once('idle', () => {
                             $(".loader").fadeOut(300);
                        });
                    }, 200);


            }
        };
    }
}

/***Botones del MENU en modo movil y modo pc**/
function menuPrincipal()
{
    $("#main-menu ul li").on("mouseover", function (e) {
        if ($(window).width() >= 768) {
            if ($(this).find(".submenu").css("display") == "none")
                $(".submenu").css({"display": "block"});
            $("#main-menu ul li").not($(this)).find(".submenu").css({"visibility": "hidden", "opacity": "0"});
            $(this).find(".submenu").css({"visibility": "visible", "opacity": "0.9"});
        }
    });
    $("#main-menu ul li").on("mouseout", function (e) {
        if ($(window).width() >= 768) {
            $(this).find(".submenu").css({"visibility": "hidden", "opacity": "0"});
        }
    });

    $("#main-menu ul li").on("click", function (e) {
        if ($(window).width() < 768) {
            $("#main-menu ul li").not($(this)).find(".submenu").css({
                "visibility": "hidden",
                "opacity": "0",
                "display": "none"
            });
            if ($(this).find(".submenu").css("visibility") == "visible")
                $(this).find(".submenu").css({"visibility": "hidden", "opacity": "0", "display": "none"});
            else
                $(this).find(".submenu").css({"visibility": "visible", "opacity": "0.9", "display": "block"});
        }
    });
    $(".movil").on("click", function (e) {
        if ($("#main-menu .listaMenu").css("display") == "none")
            $("#main-menu .listaMenu").css("display", "flex");
        else
            $("#main-menu .listaMenu").css("display", "none");
    });
    $(window).resize(function (e) {
        if ($(window).outerWidth() >= 768) {
            $("#main-menu .listaMenu").css("display", "flex");
        } else {
            $("#main-menu .listaMenu").css("display", "none");
        }
        $("#main-menu ul li .submenu").css({"visibility": "hidden", "opacity": "0", "display": "none"});
    });
}
/***FIN MENU**/


/*********
Funcion para mostrar los botones de los criterios, estos se muestran en funcion de los arrays definidos como
criteriosNombre, subcriteriosNombre sus correspondiente Id
*********/
function loadCriterios(){

let texto = "<div class='criterio' style='text-align:center'><span class='text-criterios'>Nombre</span><span class='input-criterios'>Selección</span><span class='input-criterios'>Pesos</span></div>";
for (let i=0; i< criteriosNombre.length; i++){
        texto+="<div class='criterio'><span class='text-criterios'>"+criteriosNombre[i]+"</span>"+
                "<span class='input-criterios'>"+
                "     <div class='vc-toggle-container'>"+
                "        <div><label class='vc-switch'>"+
                "            <input type='checkbox' class='vc-switch-input' id='"+criteriosId[i]+"' onChange='criterios($(this),"+i+");' checked>"+
                "            <span class='vc-switch-label' data-on='Si' data-off='No'></span>"+
                "            <span class='vc-handle'></span>"+
                "            </label>"+
                "        </div>"+
                "    </div>"+
                "</span>"+
                "<input type='text' id='input"+criteriosId[i]+"' value='"+criteriosValue[i].toFixed(3)+"'>"+
                "</div>";
        if (subcriteriosNombre.length)
            for (let k=0; k< subcriteriosNombre[i].length; k++){
                texto+="<div class='subcriterio "+criteriosId[i]+"'><span class='text-criterios'>"+subcriteriosNombre[i][k]+"</span>"+
                    "<span class='input-criterios'>"+
                    "     <div class='vc-toggle-container'>"+
                    "        <div><label class='vc-switch'>"+
                    "            <input type='checkbox' class='vc-switch-input' id='"+subcriteriosId[i][k]+"' checked";
                    //if (subcriteriosNombre[i][k] == "Movilidad") {
                        texto+=" onChange='subcriterio($(this),"+i+","+k+");'"
                   //}
                    texto+=">"+
                    "            <span class='vc-switch-label' data-on='Si' data-off='No'></span>"+
                    "            <span class='vc-handle'></span>"+
                    "            </label>"+
                    "        </div>"+
                    "    </div>"+
                    "</span>"+
                    "<input type='text' id='input"+subcriteriosId[i][k]+"' value='"+subcriteriosValue[i][k].toFixed(2)+"'>"+
                    "</div>";

            }
    }

$("#botones-criterios").append(texto);

}

/* Leo los datos del csv de los paneles para mostrar en el menu de seleccion de paneles y para comprobar si el panel es bifacial o no*/
async function leerDatosCSV(){
    const response2 = await fetch('/csv-pv-modules');

    datosPaneles= await response2.json();

    nombreCompaniaPanel =[];
    for (let i=0; i<datosPaneles.length; i++){
        if (!nombreCompaniaPanel.includes(datosPaneles[i].Manufacturer+";"+ datosPaneles[i].BIPV)){
            nombreCompaniaPanel.push(datosPaneles[i].Manufacturer+";"+ datosPaneles[i].BIPV);
            //panelBifacial.push(datosPaneles[i].BIPV);
        }

    }

}