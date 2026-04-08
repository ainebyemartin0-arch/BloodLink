/* ================================================
   BLOODLINK.JS — Complete JavaScript
   BloodLink v2.0 | St. Francis Hospital Nsambya
   ================================================ */

'use strict';

document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. AUTO-DISMISS ALERTS (5 seconds) ── */
  document.querySelectorAll('.bl-alert').forEach(function (el) {
    const closeBtn = el.querySelector('.bl-alert-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismissAlert(el));
    setTimeout(() => dismissAlert(el), 5500);
  });

  function dismissAlert(el) {
    el.style.transition = 'opacity 0.45s ease, transform 0.45s ease, max-height 0.45s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-10px)';
    el.style.maxHeight = el.offsetHeight + 'px';
    setTimeout(() => {
      el.style.maxHeight = '0';
      el.style.padding = '0';
      el.style.margin = '0';
      setTimeout(() => el.remove(), 300);
    }, 450);
  }

  /* ── 2. BLOOD TYPE BADGES — auto-render ── */
  document.querySelectorAll('[data-blood-type]').forEach(function (el) {
    const bt = el.getAttribute('data-blood-type');
    el.innerHTML = `<span class="bt-badge" data-type="${bt}">${bt}</span>`;
  });

  /* ── 3. STATUS PILLS — auto-render ── */
  document.querySelectorAll('[data-status]').forEach(function (el) {
    const st = el.getAttribute('data-status').toLowerCase().replace('_', '-').replace(' ', '-');
    const label = el.getAttribute('data-status-label') || el.getAttribute('data-status');
    el.innerHTML = `<span class="status-pill ${st}"><span class="dot"></span>${label}</span>`;
  });

  /* ── 4. STAT COUNTER ANIMATION ── */
  function animateCounter(el) {
    const raw = el.textContent.replace(/,/g, '').trim();
    const target = parseInt(raw, 10);
    if (isNaN(target) || target === 0) return;
    const duration = 900;
    const start = performance.now();
    function step(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // cubic ease out
      el.textContent = Math.round(ease * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  const statObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  document.querySelectorAll('.sc-number, .donor-stat-num, .hero-stat-num').forEach(function (el) {
    statObserver.observe(el);
  });

  /* ── 5. SCROLL REVEAL ANIMATIONS ── */
  const revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach(function (el) {
    revealObserver.observe(el);
  });

  /* ── 6. ACTIVE NAV LINK HIGHLIGHT ── */
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link, .donor-nav-links a').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    }
  });

  /* ── 7. FORM VALIDATION ── */
  document.querySelectorAll('form.bl-validate').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      let firstError = null;
      form.querySelectorAll('[required]').forEach(function (field) {
        if (!field.value.trim()) {
          field.classList.add('error');
          if (!firstError) firstError = field;
        } else {
          field.classList.remove('error');
        }
      });

      // Password match
      const p1 = form.querySelector('[name="password1"]');
      const p2 = form.querySelector('[name="password2"]');
      if (p1 && p2 && p1.value !== p2.value) {
        p2.classList.add('error');
        if (!firstError) firstError = p2;
      }

      if (firstError) {
        e.preventDefault();
        firstError.focus();
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return false;
      }
    });

    form.querySelectorAll('.bl-input, .bl-select, .bl-textarea').forEach(function (field) {
      field.addEventListener('input', function () {
        if (field.value.trim()) field.classList.remove('error');
      });
    });
  });

  /* ── 8. CONFIRM BEFORE DESTRUCTIVE ACTIONS ── */
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const msg = el.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  /* ── 9. SUBMIT BUTTON LOADING STATE ── */
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      const btn = form.querySelector('button[type="submit"]:not(.no-loading)');
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="bl-spinner"></span> Processing...';
        btn.disabled = true;
        setTimeout(function () {
          btn.innerHTML = orig;
          btn.disabled = false;
        }, 10000);
      }
    });
  });

  /* ── 10. TABLE ROW CLICK NAVIGATION ── */
  document.querySelectorAll('tr[data-href]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function (e) {
      if (!e.target.closest('a, button, form')) {
        window.location.href = row.getAttribute('data-href');
      }
    });
  });

  /* ── 11. SIDEBAR MOBILE TOGGLE ── */
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.staff-sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  /* ── 12. BOOTSTRAP TOOLTIPS ── */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });

  /* ── 13. PHONE NUMBER HINT ── */
  document.querySelectorAll('input[name="phone_number"]').forEach(function (input) {
    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('bl-field-hint')) {
      const hint = document.createElement('span');
      hint.className = 'bl-field-hint';
      hint.textContent = 'Format: 07XXXXXXXX or +256XXXXXXXXX (Uganda)';
      input.parentNode.insertBefore(hint, input.nextSibling);
    }
  });

});

/* ================================================
   CHART FUNCTIONS — call in templates
   ================================================ */

window.BloodLink = {

  /* Doughnut chart for blood type distribution */
  renderBloodTypeChart: function(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: ['#FADBD8','#EBDEF0','#D5F5E3','#D6EAF8','#FEF9E7','#EAECEE','#FDEDEC','#641E16'],
          borderColor:      ['#C0392B','#7D3C98','#1E8449','#1A5276','#D68910','#566573','#C0392B','#922B21'],
          borderWidth: 2,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { font: { family: 'DM Sans', size: 12 }, padding: 16, usePointStyle: true }
          },
          tooltip: {
            backgroundColor: '#2C3E50',
            titleFont: { family: 'Playfair Display', size: 13 },
            bodyFont:  { family: 'DM Sans', size: 12 },
            padding: 12, cornerRadius: 8,
          }
        },
        cutout: '68%',
      }
    });
  },

  /* Bar chart for requests by blood type */
  renderRequestsChart: function(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Emergency Requests',
          data: data,
          backgroundColor: 'rgba(192,57,43,0.12)',
          borderColor: '#C0392B',
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#2C3E50',
            titleFont: { family: 'Playfair Display', size: 13 },
            bodyFont:  { family: 'DM Sans', size: 12 },
            padding: 12, cornerRadius: 8,
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { family: 'JetBrains Mono', size: 11 } } },
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' },
               ticks: { font: { family: 'DM Sans', size: 11 }, stepSize: 1 } }
        }
      }
    });
  },

  /* SMS delivery line chart */
  renderSmsChart: function(canvasId, labels, sentData, failedData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Sent', data: sentData,
            borderColor: '#1E8449', backgroundColor: 'rgba(30,132,73,0.08)',
            borderWidth: 2, tension: 0.4, fill: true, pointRadius: 4,
            pointBackgroundColor: '#1E8449',
          },
          {
            label: 'Failed', data: failedData,
            borderColor: '#C0392B', backgroundColor: 'rgba(192,57,43,0.05)',
            borderWidth: 2, tension: 0.4, fill: true, pointRadius: 4,
            pointBackgroundColor: '#C0392B',
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { font: { family: 'DM Sans', size: 12 }, usePointStyle: true } },
          tooltip: {
            backgroundColor: '#2C3E50',
            titleFont: { family: 'Playfair Display', size: 13 },
            bodyFont:  { family: 'DM Sans', size: 12 },
            padding: 12, cornerRadius: 8, mode: 'index',
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { family: 'DM Sans', size: 11 } } },
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' },
               ticks: { font: { family: 'DM Sans', size: 11 }, stepSize: 1 } }
        }
      }
    });
  }
};
