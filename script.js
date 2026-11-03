const menuBtn = document.getElementById('menuBtn');
const navMenu = document.getElementById('navMenu');
const navLinks = navMenu ? Array.from(navMenu.querySelectorAll('a[href^="#"]')) : [];

if (menuBtn && navMenu) {
  menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });

  navMenu.querySelectorAll('a').forEach((anchor) => {
    anchor.addEventListener('click', () => navMenu.classList.remove('open'));
  });
}

if (navLinks.length) {
  const sections = navLinks
    .map((link) => {
      const sectionId = link.getAttribute('href').slice(1);
      const section = document.getElementById(sectionId);
      return section ? { link, section } : null;
    })
    .filter(Boolean);

  const setActiveLink = (activeLink) => {
    navLinks.forEach((link) => {
      link.classList.toggle('active', link === activeLink);
    });
  };

  const updateActiveByScroll = () => {
    const scrollPosition = window.scrollY + 120;
    let current = sections[0];

    sections.forEach((entry) => {
      if (entry.section.offsetTop <= scrollPosition) {
        current = entry;
      }
    });

    if (current) {
      setActiveLink(current.link);
    }
  };

  navLinks.forEach((link) => {
    link.addEventListener('click', () => setActiveLink(link));
  });

  window.addEventListener('scroll', updateActiveByScroll, { passive: true });
  updateActiveByScroll();
}
