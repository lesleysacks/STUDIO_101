/**
 * STUDIO 101 - GSAP & Progressive Enhancement Motion Controller
 */
export function initAnimations() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        console.info('STUDIO 101: GSAP motion library not present. Falling back to native CSS layout.');
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // Hero Text Timeline Reveal
    const heroTL = gsap.timeline({ defaults: { ease: 'power4.out', duration: 1.2 } });
    if (document.querySelector('.hero-title')) {
        heroTL.from('.hero-subbrand', { y: -20, opacity: 0, delay: 0.1 })
              .from('.hero-title', { y: 40, opacity: 0 }, '-=0.8')
              .from('.hero-desc', { y: 25, opacity: 0 }, '-=0.6')
              .from('.hero-actions', { y: 20, opacity: 0 }, '-=0.5');
    }

    // ScrollTrigger Card Animations
    const animatedCards = document.querySelectorAll('.card, .service-card, .gallery-item, .pricing-card');
    animatedCards.forEach(card => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 88%',
                toggleActions: 'play none none reverse'
            },
            y: 35,
            opacity: 0,
            duration: 0.9,
            ease: 'power3.out'
        });
    });
}
