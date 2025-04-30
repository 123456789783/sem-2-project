const offScreenMenu = document.querySelector('.off-screen-menu');
const hamMenu = document.querySelector('.ham-menu');
hamMenu.addEventListener('click',() => {
    offScreenMenu.classList.toggle('show');
}) 


setTimeout(() => {
    const overlay = document.getElementById('overlay-container');
     if (overlay) {
        overlay.classList.remove('active');
    }
}, 5000);
