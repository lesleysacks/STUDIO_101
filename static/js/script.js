document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // 1. ACTIVE PAGE LINK HIGHLIGHTING
    // ==========================================
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinksList = document.querySelectorAll('.nav-links a');
    
    navLinksList.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '' && href === 'index.html')) {
            link.classList.add('active');
        } else if (!link.classList.contains('nav-cta')) {
            link.classList.remove('active');
        }
    });

    // ==========================================
    // 2. MOBILE NAVIGATION DRAWER
    // ==========================================
    const menuToggle = document.getElementById('mobile-menu');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            const isActive = navLinks.classList.toggle('active');
            menuToggle.classList.toggle('is-active');
            menuToggle.setAttribute('aria-expanded', isActive);
            document.body.style.overflow = isActive ? 'hidden' : '';
        });

        // Close menu when clicking link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                menuToggle.classList.remove('is-active');
                document.body.style.overflow = '';
            });
        });
    }

    // ==========================================
    // 3. LUXURY LIGHTBOX MODAL VIEWER
    // ==========================================
    let lightbox = document.getElementById('lightbox');
    if (!lightbox) {
        lightbox = document.createElement('div');
        lightbox.id = 'lightbox';
        lightbox.className = 'lightbox';
        lightbox.setAttribute('role', 'dialog');
        lightbox.setAttribute('aria-hidden', 'true');
        lightbox.innerHTML = `
            <button class="lightbox-close" aria-label="Close Lightbox">&times;</button>
            <div class="lightbox-dialog">
                <img class="lightbox-content" src="" alt="Studio 101 Preview">
                <div class="lightbox-caption"></div>
            </div>
        `;
        document.body.appendChild(lightbox);
    }

    const lightboxImg = lightbox.querySelector('.lightbox-content');
    const lightboxCaption = lightbox.querySelector('.lightbox-caption');
    const lightboxClose = lightbox.querySelector('.lightbox-close');

    function openLightbox(imgSrc, captionText) {
        lightboxImg.src = imgSrc;
        lightboxCaption.textContent = captionText || 'Studio 101 Luxury Facility';
        lightbox.classList.add('open');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('open');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // Attach click triggers to images with class lightbox-trigger or within gallery items
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('.lightbox-trigger') || e.target.closest('.gallery-item');
        if (trigger) {
            e.preventDefault();
            const img = trigger.tagName === 'IMG' ? trigger : trigger.querySelector('img');
            if (img) {
                const imgSrc = img.getAttribute('src');
                const captionText = img.getAttribute('alt') || trigger.dataset.caption || 'Studio 101 Luxury Facility';
                openLightbox(imgSrc, captionText);
            }
        }
    });

    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox || e.target.classList.contains('lightbox-dialog')) {
            closeLightbox();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox.classList.contains('open')) {
            closeLightbox();
        }
    });

    // ==========================================
    // 4. FAQ ACCORDION HANDLER
    // ==========================================
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const faqItem = question.parentElement;
            const isOpen = faqItem.classList.contains('active');

            // Close all other accordions for single-open behavior
            document.querySelectorAll('.faq-item').forEach(item => {
                item.classList.remove('active');
                const btn = item.querySelector('.faq-question');
                if (btn) btn.setAttribute('aria-expanded', 'false');
            });

            if (!isOpen) {
                faqItem.classList.add('active');
                question.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // ==========================================
    // 5. BOOKING & CONTACT FORM HANDLER
    // ==========================================
    const bookingForm = document.getElementById('studio-booking-form');

    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const serviceSelect = document.getElementById('service');
            const name = nameInput ? nameInput.value : 'Valued Client';
            const serviceText = serviceSelect ? serviceSelect.options[serviceSelect.selectedIndex].text : 'Studio Hire';

            showSuccessModal(name, serviceText);
            bookingForm.reset();
        });
    }

    function showSuccessModal(name, service) {
        let modal = document.getElementById('booking-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'booking-modal';
            modal.className = 'lightbox open';
            modal.innerHTML = `
                <div class="lightbox-dialog" style="background: var(--bg-card); padding: 48px; border-radius: var(--radius-sm); border: 1px solid var(--border-burgundy); max-width: 500px; text-align: center;">
                    <div style="width: 70px; height: 70px; background: rgba(128, 0, 32, 0.2); border: 1px solid var(--primary-light); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 24px; color: #ff4d6d; font-size: 32px;">
                        <i class="fas fa-check"></i>
                    </div>
                    <h3 style="font-family: var(--font-heading); font-size: 24px; margin-bottom: 12px; color: #ffffff;">Booking Inquiry Received</h3>
                    <p style="color: var(--text-muted); font-size: 15px; margin-bottom: 24px;">Thank you, <strong style="color: #fff;">${name}</strong>. Our production team will contact you within 2 hours to confirm details for your <strong style="color: var(--primary-light);">${service}</strong> session.</p>
                    <button class="btn-primary" id="close-booking-modal" style="width: 100%;">Return to Studio 101</button>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            modal.classList.add('open');
        }

        const closeBtn = document.getElementById('close-booking-modal');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.remove('open');
            };
        }
    }
});
