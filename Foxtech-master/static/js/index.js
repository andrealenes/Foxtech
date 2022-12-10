'use strict';

const btnMainMenuCategories = document.getElementById('button-toggle-main-menu-categories');
const containerMainMenuCategories = document.getElementById('container-toggle-main-menu-categories');
const btnMainMenuOptionsUser = document.getElementById('button-toggle-menu-options-user');
const containerMainMenuOptionsUser = document.getElementById('container-toggle-main-menu-options-user');
const containerFigureMainHeader = document.getElementById('container-figure-main-header');
const navMainMenu = document.getElementById('main-menu');
const addProduct = document.getElementById("add_product");
const removeProduct = document.getElementById("remove_product");
const quantity = document.getElementById("quantity");
const body = document.getElementById('body');
const containerModal = document.getElementById('containerModal');
const btnDashboardUser = document.getElementById('button-toggle-dashboard');
const menuDashboardUser = document.getElementById('menu-dashboard-user');
const containerOptionsAddress = document.getElementById('container-direcciones');
const optionHomeDelivery = document.getElementById('entrega-domicilio');
const optionStoreDelivery = document.getElementById('recoge-en-tienda')


// Comprobar si la captura del elemento es null
if (btnMainMenuCategories) {
    btnMainMenuCategories.addEventListener('click', () => {
        containerMainMenuCategories.classList.toggle('container-list-categories-main-menu--show');
    });
}

// Comprobar si la captura del elemento es null
if (btnMainMenuOptionsUser) {
    btnMainMenuOptionsUser.addEventListener('click', () => {
        containerMainMenuOptionsUser.classList.toggle('container-options-user-main-menu--show');
    });
}

// Comprobar si la captura del elemento es null
if (containerFigureMainHeader) {
    navMainMenu.style.backgroundColor = 'transparent';
    window.addEventListener('scroll', () => {
        if (window.scrollY > (containerFigureMainHeader.clientHeight - 60)) {
            navMainMenu.style.backgroundColor = '#0d2c46';
        } else {
            navMainMenu.style.backgroundColor = 'transparent';
        }
    })
}

// Preloader
window.addEventListener('load', () => {
    const contenedorLoader = document.getElementById('preload');
    contenedorLoader.classList.toggle('container-preload--show');
    body.classList.toggle('preload-hidden');
});

// Modificar la cantidad de productos que vamos a agregar al carrito de compras
if (addProduct) {
    addProduct.addEventListener("click", () => {
        quantity.value = parseInt(quantity.value) + 1;
    });
}

if (removeProduct) {
    removeProduct.addEventListener("click", () => {
        if (parseInt(quantity.value) !== 1) {
            quantity.value = parseInt(quantity.value) - 1;
        }
    });
}

// Funciones del modal
if (containerModal) {
    if (!(containerModal.classList.contains('container-modal--hidden'))) {
        body.style.overflow = 'hidden';
    }
}

function cerrarModal() {
    containerModal.classList.add('container-modal--hidden');
    body.style.overflow = 'auto';
}

if (btnDashboardUser) {
    btnDashboardUser.addEventListener('click', () => {
        menuDashboardUser.classList.toggle('container-menu-dashboard-user--show');
    });
}

// Mostrar direcciones de envio en la orden de compra
function mostrarDirecciones(elemento) {
    if (elemento.value == 'Entrega a domicilio') {
        containerOptionsAddress.classList.add('container-select-address-home-delivery--show');
    } else {
        containerOptionsAddress.classList.remove('container-select-address-home-delivery--show');
    }
}