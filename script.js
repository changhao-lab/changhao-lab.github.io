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

const doiItems = Array.from(document.querySelectorAll('.pub-doi'));

const copyText = async (text) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const helper = document.createElement('textarea');
  helper.value = text;
  helper.setAttribute('readonly', '');
  helper.style.position = 'absolute';
  helper.style.left = '-9999px';
  document.body.appendChild(helper);
  helper.select();
  document.execCommand('copy');
  document.body.removeChild(helper);
};

let copyToastTimer;
const copyToast = document.createElement('div');
copyToast.className = 'copy-toast';
copyToast.setAttribute('aria-live', 'polite');
document.body.appendChild(copyToast);

const showCopyToast = (message) => {
  copyToast.textContent = message;
  copyToast.classList.add('show');

  window.clearTimeout(copyToastTimer);
  copyToastTimer = window.setTimeout(() => {
    copyToast.classList.remove('show');
  }, 1200);
};

doiItems.forEach((item) => {
  item.setAttribute('role', 'button');
  item.setAttribute('tabindex', '0');
  item.setAttribute('title', 'Click to copy DOI');

  const runCopy = async () => {
    const doi = item.textContent.replace(/^\s*DOI:\s*/i, '').trim();
    if (!doi) return;

    try {
      await copyText(doi);
      item.classList.add('copied');
      showCopyToast('DOI copied');

      window.setTimeout(() => {
        item.classList.remove('copied');
      }, 1200);
    } catch (error) {
      console.error('Failed to copy DOI:', error);
    }
  };

  item.addEventListener('click', runCopy);
  item.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      runCopy();
    }
  });
});
