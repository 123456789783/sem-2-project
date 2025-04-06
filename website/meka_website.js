const offScreenMenu = document.querySelector('.off-screen-menu');
const hamMenu = document.querySelector('.ham-menu');
hamMenu.addEventListener('click',() => {
    offScreenMenu.classList.toggle('show');
}) 