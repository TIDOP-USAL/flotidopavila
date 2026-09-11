/**
 * Funcion para cargar todas las capas del webgis
 */
async function loadLayers() {
    $(".loader").fadeIn(300);

    paralelosMeridianos();
    let botones = '';
    for (i=0; i<puntos.length; i++){
        visible = checkIfVisible(puntos[i].nombreCapa, puntos[i].mostrar);
        addLayerPoint(puntos[i].imagen, puntos[i].nombreImagen, puntos[i].nombreSource, puntos[i].nombreCapa, puntos[i].nombreJson, visible);
        botones +=  addButton(puntos[i].texto, puntos[i].nombreCapa, puntos[i].imagen, visible);
    }
    for (i=0; i<lineas.length; i++) {
        visible = checkIfVisible(lineas[i].nombreCapa, lineas[i].mostrar);
        addLayerLines(lineas[i].nombreSource, lineas[i].nombreCapa, lineas[i].nombreJson, lineas[i].color, visible, lineas[i].grosor);
        botones += addButton(lineas[i].texto,  lineas[i].nombreCapa, lineas[i].imagen, visible);
    }
    addLayerLines("Rios", "Rios-layer", "static/datos/cuencas.geojson", "#0000FF", "visible", 2);
    for (i=0; i<rellenos.length; i++) {
        visible = checkIfVisible(rellenos[i].nombreCapa, rellenos[i].mostrar);
        addLayerFill(rellenos[i].nombreSource, rellenos[i].nombreCapa, rellenos[i].nombreJson, rellenos[i].color,  visible);
        botones += addButton(rellenos[i].texto, rellenos[i].nombreCapa, rellenos[i].imagen, visible);
    }

    visible = checkIfVisible("Regadio-layer", 'none');
    addLayerRegadio("Regadio","Regadio-layer", visible);
    botones += addButton("Regadio","Regadio-layer", "static/img/regadio.png", visible);
    $(control_botones).html(botones);
    map.once('idle', () => {
        $(".loader").fadeOut(300);
    });

}



function addLayerRegadio(nombre_source, nombre_capa, mostrar) {

    if (map.getSource(nombre_source) || mostrar == 'none') { return;}
    map.addSource(nombre_source, {
        "type": "image",
        "url": "/static/datos/cultivos.png",
        "coordinates": [
            [-5.756169013, 41.175912336],
            [-4.152273713, 41.175912336],
            [-4.152273713, 40.072198304],
            [-5.756169013, 40.072198304]
        ]
    });
    map.addLayer({
        id:  nombre_capa,
        'type': 'raster',
        'source': nombre_source,
        'paint': {
            'raster-fade-duration': 0
        }
    });
     map.setLayoutProperty(nombre_capa,'visibility', visible);
}

 /**
 * Tenemos el problema que al cambiar el estilo del mapa se borran todas las capas que hemos puesto, pues al cambiar el estilo se
 * vuelven a cargar todas las capas porque sino se borran, con esta funcion lo que
 * hacemos es comprobar si ya se han cargado anteriormente y si es asi entonces se muestran o no dependiendo de si ya se estaban mostrando
 * @param id nombre de la capa a comprobar
 * @param visible valor que tiene por defecto la capa si es none o visible
 * @returns {string} valor que devuelve si dicha capa se debe o no mostrar
 */
function checkIfVisible(id, visible){
        //let visible = valor;
        if (document.getElementById(id) != null) {
            var isChecked = document.getElementById(id).checked;
            if (isChecked)
                visible ='visible';
            else
                visible='none';
        }
        return visible;
}
/**
 * Añade los diferentes botones del aeropuerto para mostrar u ocultar las diferentes capas
 * @param text texto que se muestra en el boton
 * @param Id id del boton
 * @param nombre_foto nombre de la foto que se muestra en el boton
 * @param marcar si se debe marcar o no el boton
 * @returns {string} devuelve el texto del boton
 */
function addButton(text, Id,  nombre_foto, marcar) {
    let checked = "";
    let nombre_capa = Id;
    if (marcar == "visible")
        checked = "checked";
    let boton = "<div class=\"vc-toggle-container\">\n" +
        "   <div><span class=\"text\">" + text + "</span> <label class=\"vc-switch\">\n" +
        "        <input type=\"checkbox\" class=\"vc-switch-input\" id=\"" + Id + "\" onchange=\"cambioEstado('" + Id + "','" + nombre_capa + "');\" " + checked + ">\n" +
        "        <span class=\"vc-switch-label\" data-on=\"Si\" data-off=\"No\"></span>\n" +
        "        <span class=\"vc-handle\"></span>\n" +
        "    </label>\n" +
        "    <div class=\"leyenda\"><img src=\"" + nombre_foto + "\" width='24' height='24' alt='" + text + "'> </div></div>\n" +
        "</div>";
    return boton;
}

/**
 * Función para cambiar el estado del boton
 * @param Id: id del boton que se ha pulsado
 * @param nombre_capa: nombre de la capa del boton pulsado
 */
async function cambioEstado(Id, nombre_capa){
	var isChecked = $("#"+Id).is(":checked");
    //para coprobar si metemos una capa con relleno y bordes
    let existe = rellenos.some(item => item.nombreCapa === nombre_capa);
	if(isChecked){
        if ( $("#Embalses-layer").is(":checked") || $("#Lagunas-layer").is(":checked"))
            $(".cuencas").css({"display": "block"});
        await loadLayers(puntos, lineas, rellenos);
        if(existe) {
            map.setLayoutProperty(nombre_capa + "-fill", 'visibility', 'visible');
            map.setLayoutProperty(nombre_capa + "-borders", 'visibility', 'visible');
        }else
            map.setLayoutProperty(nombre_capa,'visibility', 'visible');
        //Si se añade embalses o lagunas entonces se cambia la cuenca a la que esta seleccionada
        if (nombre_capa == "Embalses-layer" || nombre_capa == "Lagunas-layer")
            cambiarCuenca(cuenca);
	}else{
        if ( !$("#Embalses-layer").is(":checked") && !$("#Lagunas-layer").is(":checked")) {
            //$(".cuencas").css({"display": "none"});
            map.setFilter("Rios-layer", null);
        }
        if(existe) {
            map.setLayoutProperty(nombre_capa + "-fill", 'visibility', 'none');
            map.setLayoutProperty(nombre_capa + "-borders", 'visibility', 'none');
        }else
			map.setLayoutProperty(nombre_capa,'visibility', 'none');
	}

}



/**
 * Funcion para poner los paralelos y meridianos en el mapa
 */
function paralelosMeridianos(){
    if (!map.getLayer('parallels'))
        map.addLayer({
          'id': 'parallels',
          'type': 'line',
          'source': {
            'type': 'geojson',
            'data': {
              'type': 'Feature',
              'geometry': {
                'type': 'MultiLineString',
                'coordinates': [
                  [[-10, 36], [4, 36]],
                  [[-10, 38], [4, 38]],
                  [[-10, 40], [4, 40]],
                  [[-10, 42], [4, 42]],
                  [[-10, 44], [4, 44]],
                ]
              }
            }
          },
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#a3a3a3',
            'line-width': 0.3
          }
        });
    if (!map.getLayer('meridians'))
        map.addLayer({
          'id': 'meridians',
          'type': 'line',
          'source': {
            'type': 'geojson',
            'data': {
              'type': 'Feature',
              'geometry': {
                'type': 'MultiLineString',
                'coordinates': [
                    [[4, 36], [4, 44]]  ,
                    [[2, 36], [2, 44]]  ,
                    [[0, 36], [0, 44]]  ,
                    [[-2, 36], [-2, 44]],
                    [[-4, 36], [-4, 44]],
                    [[-6, 36], [-6, 44]],
                    [[-8, 36], [-8, 44]],
                    [[-10, 36], [-10, 44]],
                ]
              }
            }
          },
          'layout': {
            'line-join': 'round',
            'line-cap': 'round'
          },
          'paint': {
            'line-color': '#a3a3a3',
            'line-width': 0.3
          }
        });
}

/**
 * Funcion para poner en el mapa las capas que son lineas
 * @param nombre_source: nombre del source de la capa usado en map.addSource
 * @param nombre_capa: nombre de la capa usado en map.addLayer es el nombre con el que se va a identificar la capa
 * @param nombre_json: archivo json o geojson que se va a mostrar
 * @param color: color en hexadecimal en el que se van a pintar las lineas
 * @param mostrar: si se muetra u oculta la capa
 * @param grosor: grosos de las lineas
 */
function addLayerLines(nombre_source, nombre_capa, nombre_json, color, mostrar, grosor=1) {
    if (map.getSource(nombre_source) || mostrar == 'none') { return;}
    map.addSource(nombre_source, {
            type: 'geojson',
// Use a URL for the value for the `data` property.
            data: nombre_json
        });
        map.addLayer({
            'id': nombre_capa,
            'type': 'line',
            'source': nombre_source,
            'layout': {
                'line-join': 'round',
                'line-cap': 'round'
            },
            'paint': {
                'line-color': color,
                //'line-width': 4
                'line-width': ['interpolate', ['linear'], ['zoom'], 5*grosor, 0.5*grosor, 10*grosor, 3.5*grosor, 12*grosor, 9*grosor]

            }
        });
        map.setLayoutProperty(nombre_capa,'visibility', mostrar);
}


/**
 * Funcion para poner en el mapa las capas que son puntos
 * @param imagen: es el nombre del fichero de la imagen que se va poner en el mapa donde van los puntos
 * @param nombre_imagen: es el nombre que se le da a la imagen en map.addImage
 * @param nombre_source:
 * @param nombre_capa: nombre de la capa usado en map.addLayer es el nombre con el que se va a identificar la capa
 * @param nombre_json: archivo json o geojson que se va a mostrar
 * @param color: color en hexadecimal en el que se van a pintar las lineas
 * @param mostrar: si se muetra u oculta la capa
 */
function addLayerPoint(imagen, nombre_imagen, nombre_source, nombre_capa, nombre_json, mostrar="visible"){
    if (map.getSource(nombre_source) || mostrar == 'none') { return;}

    new Promise((resolve, reject) => {

        if (map.hasImage(nombre_imagen)) return resolve();
        const img = new Image();
        img.onload = () => {
            map.addImage(nombre_imagen, img);
            resolve();
        };
        img.onerror = () => {
            console.error('Error cargando:', url);
            resolve();
        };
        img.src = imagen;
    });

    map.addSource(nombre_source, {
        type: 'geojson',
        data: nombre_json
    });

    map.addLayer({
        'id': nombre_capa,
        'type': 'symbol',
        'source': nombre_source,
        'layout': {
            'icon-image': nombre_imagen, // reference the image
            'icon-size': ['interpolate', ['linear'], ['zoom'], 5, 0.4, 10, 0.6, 14, 0.8]
        },

    });
    map.setLayoutProperty(nombre_capa,'visibility', mostrar);


    map.on('mouseenter', nombre_capa, () => {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('click', nombre_capa, (e) => {

        let description="";

        if (e.features[0].properties.id_opte__1!=null)
            description +="<b>"+e.features[0].properties.id_opte__1+"</b><br/>";
        else{
        }

        if(description != "") {
            console.log(description);
            $(".mensaje").html(description);
            $("#dialogo-mensaje").dialog("open");
        }

    });

    map.on('mouseleave', nombre_capa, () => {
            map.getCanvas().style.cursor = '';
    });

}

/**
 * Funcion para poner en el mapa las capas que son tienen rellenos y bordes
 * @param nombre_source: nombre del source de la capa usado en map.addSource
 * @param nombre_capa: nombre de la capa usado en map.addLayer es el nombre con el que se va a identificar la capa
 * @param nombre_json: archivo json o geojson que se va a mostrar
 * @param color: color en hexadecimal en el que se van a pintar las lineas
 * @param mostrar: si se muetra u oculta la capa
 */
function addLayerFill(nombre_source, nombre_capa, nombre_json, color, mostrar) {
    if (map.getSource(nombre_source) || mostrar == 'none') { return;}
    map.addSource(nombre_source, {
            type: 'geojson',
// Use a URL for the value for the `data` property.
            data: nombre_json
        });
        map.addLayer({
            'id': nombre_capa+"-borders",
            'type': 'line',
            'source': nombre_source,
            'layout': {
                'line-join': 'round',
                'line-cap': 'round'
            },
            'paint': {
                'line-color': color,
                //'line-width': 4
                'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.5, 10, 3.5, 12, 9]

            }
        });
        map.addLayer({
            'id': nombre_capa+"-fill",
            'type': 'fill',
            'source': nombre_source,
            'paint': {
                'fill-color':color,//'#ffdddd',
                'fill-opacity': 0.7
                //'line-width': 4
            }
        });
        map.on('mouseenter', nombre_capa+'-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', nombre_capa+'-fill', () => {
        map.getCanvas().style.cursor = '';
    });

    map.on('click', nombre_capa+'-fill', (e) => {
        let nombre = ''
        if (e.features[0].properties.NOMBRE != null)
           nombre = e.features[0].properties.NOMBRE;
        else
            nombre = '-';
        nombre += ' (' + e.features[0].properties.cuenca + ')';
        nombre += ' (' + e.features[0].properties.Tipo + ')';
        $(".nombre").html(nombre);
        const area = e.features[0].properties.area;
        if (area != null)
            $(".area-embalse").html(area);
        let description = '<div class="boton-calcular">' +
            '<button id="btnCalcular" onclick="calcularProduccionMasaDeAgua(' + e.lngLat.lng + ',' + e.lngLat.lat + ',' + area + ')" >' +
            'Calcular' +
            '</button>' +
            '</div>';
        description += '<div id="mensaje-embalse"></div></div>';
        $(".boton-info-embalse").html(description);
        $("#dialogo-embalse").dialog("open");
    });
        map.setLayoutProperty(nombre_capa+"-fill",'visibility', mostrar);
        map.setLayoutProperty(nombre_capa+"-borders",'visibility', mostrar);
}


$(document).ready(function(event) {
    $(".input-cuencas").on("change", function () {
        cuenca = $(this).val();
        cambiarCuenca(cuenca);
    });
});
function cambiarCuenca(cuenca) {
    if (cuenca === "Todos") {
        if (map.getLayer("Embalses-layer-fill")) {
            map.setFilter("Embalses-layer-fill", null);
            map.setFilter("Embalses-layer-borders", null);
        }
        if (map.getLayer("Lagunas-layer-fill")) {
            map.setFilter("Lagunas-layer-fill", null);
            map.setFilter("Lagunas-layer-borders", null);
        }
        if (map.getLayer("Rios-layer")) {
            map.setFilter("Rios-layer", null);
        }
    } else {
        if (map.getLayer("Embalses-layer-fill")) {
            map.setFilter("Embalses-layer-fill", ["==", ["get", "cuenca"], cuenca]);
            map.setFilter("Embalses-layer-borders", ["==", ["get", "cuenca"], cuenca]);
        }
        if (map.getLayer("Lagunas-layer-fill")) {
            map.setFilter("Lagunas-layer-fill", ["==", ["get", "cuenca"], cuenca]);
            map.setFilter("Lagunas-layer-borders", ["==", ["get", "cuenca"], cuenca]);
        }
        if (map.getLayer("Rios-layer")) {
            map.setFilter("Rios-layer", ["==", ["get", "cuenca"], cuenca]);
        }
    }
}



