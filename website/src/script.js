/**
 * ApexAurum Website - Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }

    // Navbar scroll effect
    const nav = document.querySelector('.nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            nav.style.background = 'rgba(10, 10, 11, 0.95)';
        } else {
            nav.style.background = 'rgba(10, 10, 11, 0.8)';
        }

        lastScroll = currentScroll;
    }, { passive: true });

    // Smooth reveal animations on scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const revealCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    };

    const revealObserver = new IntersectionObserver(revealCallback, observerOptions);

    // Observe elements for reveal
    document.querySelectorAll('.feature-card, .agent-card, .protocol-list li').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        revealObserver.observe(el);
    });

    // Add revealed class styles
    const style = document.createElement('style');
    style.textContent = `
        .revealed {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);

    // Stagger animation for grid items
    document.querySelectorAll('.features-grid, .agents-grid').forEach(grid => {
        const items = grid.querySelectorAll('.feature-card, .agent-card');
        items.forEach((item, index) => {
            item.style.transitionDelay = `${index * 0.1}s`;
        });
    });

    // Form submission handler (placeholder - update with real endpoint)
    const betaForm = document.querySelector('.beta-form');

    if (betaForm) {
        betaForm.addEventListener('submit', async (e) => {
            const action = betaForm.getAttribute('action');

            // If using formspree placeholder, show helpful message
            if (action.includes('your-form-id')) {
                e.preventDefault();
                alert('Form endpoint not configured yet.\n\nTo enable signups:\n1. Create a free account at formspree.io\n2. Replace "your-form-id" in index.html with your actual form ID');
                return;
            }

            // Otherwise let the form submit normally to Formspree
        });
    }

    // Subtle parallax on hero glyph
    const heroGlyph = document.querySelector('.hero-glyph');

    if (heroGlyph && window.innerWidth > 768) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.3;
            heroGlyph.style.transform = `translateY(calc(-50% + ${rate}px))`;
        }, { passive: true });
    }

    // Agent card hover effects - subtle glow
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            const symbol = card.querySelector('.agent-symbol');
            if (symbol) {
                symbol.style.transform = 'scale(1.1)';
                symbol.style.transition = 'transform 0.3s ease';
            }
        });

        card.addEventListener('mouseleave', () => {
            const symbol = card.querySelector('.agent-symbol');
            if (symbol) {
                symbol.style.transform = 'scale(1)';
            }
        });
    });

    // Active nav link highlighting
    const sections = document.querySelectorAll('section[id]');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        document.querySelectorAll('.nav-links a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }, { passive: true });

    // Add active link style
    const activeLinkStyle = document.createElement('style');
    activeLinkStyle.textContent = `
        .nav-links a.active {
            color: var(--gold) !important;
        }
    `;
    document.head.appendChild(activeLinkStyle);

    console.log('ApexAurum: Site initialized');
});
