window.CustomerPage = (function () {
  const els = {};

  function cacheDom() {
    els.overlay = document.getElementById('customerModalOverlay');
    els.closeBtn = els.overlay?.querySelector('.modal-close');
    els.name = document.getElementById('customerName');
    els.email = document.getElementById('customerEmail');
    els.phone = document.getElementById('customerPhone');
    els.bookings = document.getElementById('totalBookings');
    els.spent = document.getElementById('totalSpent');
    els.since = document.getElementById('memberSince');
  }
  function formatDate(dateString) {
    if (!dateString) return "";

    const date = new Date(dateString);
    if (isNaN(date)) return "";

    const options = { year: "numeric", month: "long", day: "numeric" };
    return date.toLocaleDateString(undefined, options);
  }
  function open(data) {
    if (!els.overlay) return;
    els.name.textContent = data.name || '';
    els.email.textContent = data.email || '';
    els.phone.textContent = data.phone || '';
    els.bookings.textContent = data.bookings || '0';
    els.spent.textContent = `Rs ${data.spent || 0}`;
    els.since.textContent = formatDate(data.registered);
    els.overlay.style.display = 'flex';
  }

  function close() {
    if (els.overlay) els.overlay.style.display = 'none';
  }

  function bindEvents() {
    // open buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation(); // don't bubble to sidebar/global handlers
        const data = {
          id: btn.dataset.id,
          name: btn.dataset.name,
          email: btn.dataset.email,
          phone: btn.dataset.phone,
          bookings: btn.dataset.bookings,
          spent: btn.dataset.spent,
          registered: btn.dataset.registered,
        };
        open(data);
      });
    });

    // close button
    els.closeBtn?.addEventListener('click', (e) => {
      e.preventDefault();
      close();
    });

    // close on ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') close();
    });

    // click outside modal to close (only when clicking the overlay itself)
    els.overlay?.addEventListener('click', (e) => {
      if (e.target === els.overlay) close();
    });
  }

  function init() {
    cacheDom();
    bindEvents();
  }

  // init after DOM is ready
  document.addEventListener('DOMContentLoaded', init);

  // Expose only what we need (no generic global openModal!)
  return { open, close };
})();
