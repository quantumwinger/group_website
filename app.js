document.addEventListener('DOMContentLoaded', () => {

    // --- Mobile Menu Toggle ---
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }));
    }

    // --- Navbar Scroll Effect ---
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.padding = "0.5rem 2rem";
            navbar.style.backgroundColor = "rgba(10, 15, 24, 0.95)";
            navbar.style.boxShadow = "0 4px 30px rgba(0, 0, 0, 0.5)";
        } else {
            navbar.style.padding = "1rem 2rem";
            navbar.style.backgroundColor = "rgba(10, 15, 24, 0.85)";
            navbar.style.boxShadow = "none";
        }
    });

    // --- Publications Abstract Click Toggle ---
    const pubItems = document.querySelectorAll('.pub-item');
    pubItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Do not toggle if the user clicks on a link
            if (e.target.tagName.toLowerCase() === 'a') return;

            // Toggle active class on this item
            const isActive = item.classList.contains('active');
            
            // Optional: close other open tooltips
            pubItems.forEach(p => p.classList.remove('active'));
            
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

});
