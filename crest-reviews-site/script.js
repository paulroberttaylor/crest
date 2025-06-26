// Single Page Application Navigation
document.addEventListener('DOMContentLoaded', function() {
    // Navigation handling
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Show corresponding section
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Development search functionality
    const searchInput = document.getElementById('development-search');
    const developmentCards = document.querySelectorAll('.development-card');
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            
            developmentCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Contact form handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // In a real implementation, this would send to a backend
            alert('Thank you for sharing your experience. We will review your submission and contact you if we need any additional information.');
            contactForm.reset();
        });
    }
    
    // Add smooth scrolling for any anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Animate stats on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe stat cards
    document.querySelectorAll('.stat-card h3').forEach(stat => {
        observer.observe(stat);
    });
    
    function animateValue(element) {
        const target = element.textContent;
        const isNumber = /^\d+/.test(target);
        
        if (isNumber) {
            const match = target.match(/^(\d+)(.*)$/);
            const num = parseInt(match[1]);
            const suffix = match[2] || '';
            const duration = 1500;
            const steps = 50;
            const increment = num / steps;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= num) {
                    element.textContent = num + suffix;
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current) + suffix;
                }
            }, duration / steps);
        }
    }
    
    // Add development data (in real app, this would come from a database)
    const developments = [
        { name: 'Campbell Wharf', location: 'Milton Keynes, MK9', issues: 3 },
        { name: 'Windsor Gate', location: 'Windsor, Berkshire', issues: 2 },
        { name: 'Finberry', location: 'Ashford, Kent', issues: 5 },
        { name: 'Henley Gate', location: 'Ipswich, Suffolk', issues: 1 },
        { name: 'Brooklands Park', location: 'Bristol', issues: 4 },
        { name: 'Nobel Park', location: 'Oxfordshire', issues: 2 },
        { name: 'Newlands Place', location: 'Arborfield Green, Berkshire', issues: 3 },
        { name: 'Cringleford Heights', location: 'Norwich, Norfolk', issues: 0 },
        { name: 'Curbridge Meadows', location: 'Whiteley, Hampshire', issues: 2 },
        { name: 'Claybourne', location: 'Steeple Claydon, Buckinghamshire', issues: 1 }
    ];
    
    // Populate developments if we're on that section
    const developmentsGrid = document.querySelector('.developments-grid');
    if (developmentsGrid && developments.length > 6) {
        // Clear existing cards
        developmentsGrid.innerHTML = '';
        
        // Add all developments
        developments.forEach(dev => {
            const card = document.createElement('div');
            card.className = 'development-card';
            card.innerHTML = `
                <h4>${dev.name}</h4>
                <p>${dev.location}</p>
                <p style="color: ${dev.issues > 0 ? '#dc2626' : '#16a34a'}">
                    ${dev.issues > 0 ? dev.issues + ' reported issues' : 'No issues reported'}
                </p>
                <a href="#" class="dev-link">View Details →</a>
            `;
            developmentsGrid.appendChild(card);
        });
    }
    
    // Add warning banner for financial news
    const createWarningBanner = () => {
        const banner = document.createElement('div');
        banner.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #fef3c7;
            color: #92400e;
            padding: 1rem;
            text-align: center;
            z-index: 1000;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
        `;
        banner.innerHTML = `
            <p><strong>Latest:</strong> Crest Nicholson warned of potential loan covenant breach by April 2025. 
            <a href="https://www.reuters.com/world/uk/uk-homebuilder-crest-nicholson-sees-trading-stability-second-half-2025-2025-02-04/" 
               target="_blank" style="color: #dc2626;">Read more</a>
            <button onclick="this.parentElement.remove()" style="margin-left: 1rem; padding: 0.25rem 0.5rem; 
                    background: #92400e; color: white; border: none; border-radius: 4px; cursor: pointer;">×</button>
            </p>
        `;
        document.body.appendChild(banner);
    };
    
    // Show warning banner after 3 seconds
    setTimeout(createWarningBanner, 3000);
});

// Google Analytics or similar tracking would go here
// gtag('config', 'GA_MEASUREMENT_ID');