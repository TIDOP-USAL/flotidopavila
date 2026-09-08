let map;
const accessToken= 'CXYEP8Nfe44zGcei0GvU';
const control_botones = '#botones';
let cuenca = "Todas";
const puntos = [
    //{texto:'Consumo', imagen:'./static/img/consumo.png', nombreImagen:'consumoImg', nombreSource:'Consumo', nombreCapa:'Consumo-layer', nombreJson:'./static/datos/centros_consumo.geojson', checked:'visible'},
];
const lineas=[
    {texto: 'Red Electrica', imagen:'./static/img/electricidad.png', nombreSource:'RedElectrica', nombreCapa: 'RedElectrica-layer', nombreJson: './static/datos/red_electrica.geojson', color:'#050', mostrar: 'none', grosor: 0.1, checked:true}
];
const rellenos=[
    {texto: 'Embalses', imagen:'./static/img/embalses.png', nombreSource:'Embalses', nombreCapa: 'Embalses-layer', nombreJson: '/static/datos/embalses.geojson', color:'#ff0000', mostrar: 'none', grosor: 0.5, checked:false},
    {texto: 'Lagunas', imagen:'./static/img/lagunas.png', nombreSource:'Lagunas', nombreCapa: 'Lagunas-layer', nombreJson: '/static/datos/lagunas.geojson', color:'#00ff00', mostrar: 'none', grosor: 0.5, checked:false},
    ];

const criteriosNombre=["CF", "Variacion", "Viento", "LCOE",  "Distancia Red", "Emisiones Evitadas", "Comunidades Energeticas", "Regadios"];
const criteriosId=["CF", "Variacion", "Viento", "LCOE", "Distancia", "EmisionesEvitadas",  "NumMasasAgua", "Regadios"];
const criteriosValue=[0.12,0.12,0.12,0.12,0.13,0.13,0.13,0.13];
let subcriteriosNombre=[];
let subcriteriosId=[ ];
let subcriteriosValue=[];

const nombreTablas=    ['tbCriterios']
const valuesCriteriosAHP=[["1","3","5","1","4","5","5"],["1/3","1","1/2","1/2","3","3","3"],["1/5","2","1","1/3","2","3","3"],
    ["1","2","3","1","4","5","5"],["1/4","1/3","1/2","1/4","1","2","2"],["1/5","1/3","1/3","1/5","1/2","1","1"],
    ["1/5","1/3","1/3","1/5","1/2","1","1"]];
let datosPaneles, nombreCompaniaPanel;
