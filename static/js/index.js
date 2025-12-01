  // Show active subscriptions for logged-in user
  function showSubscriptions() {
    var email = getUser();
    var subsDiv = document.getElementById('activeSubscriptions');
    var subsList = document.getElementById('subscriptionsList');
    if (!subsDiv || !subsList) return;
    if (!email) {
      subsDiv.style.display = 'none';
      return;
    }
    subsDiv.style.display = 'block';
    subsList.textContent = 'Loading...';
    fetch('/api/get_subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
      let html = '';
      html += `<table style="width:100%;border-collapse:collapse;">`;
      html += `<tr style="background:#f3f3f3;"><th style="padding:8px 10px;text-align:left;">Event Name</th><th>Type</th><th>Date</th></tr>`;
      let hasSubs = false;
      if (data.weather) {
        html += `<tr><td style="padding:8px 10px;">${data.weather.location}</td><td>Weather</td><td>${data.weather.date_added ? data.weather.date_added.split('T')[0] : ''}</td></tr>`;
        hasSubs = true;
      }
      if (data.countdowns && data.countdowns.length > 0) {
        data.countdowns.forEach(cd => {
          html += `<tr><td style="padding:8px 10px;">${cd.name}</td><td>Countdown</td><td>${cd.date}</td></tr>`;
        });
        hasSubs = true;
      }
      html += `</table>`;
      if (!hasSubs) {
        html += '<div style="padding:12px;color:#dc3545;">No active subscriptions found.</div>';
      }
      // Debug output
      html += `<pre style='margin-top:16px;background:#f8f9fa;color:#333;padding:8px;border-radius:6px;font-size:0.95em;'>API Response: ${JSON.stringify(data, null, 2)}</pre>`;
      subsList.innerHTML = html;
    })
    .catch(() => {
      subsList.innerHTML = '<span style="color:#dc3545;">Error loading subscriptions.</span>';
    });
  }

  // Call showSubscriptions whenever header is rendered
  function renderHeader() {
    var email = getUser();
    if (!userHeader) {
      console.error('userHeader div not found!');
      return;
    }
    if (email) {
      userHeader.innerHTML = `
        <button id="logoutBtn" class="btn" style="background:#b3c7f9;color:#333;margin-right:10px;">Log Out</button>
        <span style="font-weight:600;color:#333;">${email}</span>
      `;
      document.getElementById('logoutBtn').onclick = function() {
        clearUser();
        renderHeader();
      };
    } else {
      userHeader.innerHTML = `
        <button id="loginBtn" class="btn" style="background:#b3c7f9;color:#333;">Log In</button>
      `;
      document.getElementById('loginBtn').onclick = function() {
        loginModal.style.display = 'flex';
        loginEmail.value = '';
      };
    }
    showSubscriptions();
  }
// ...existing code...
document.addEventListener('DOMContentLoaded', function() {
  var userHeader = document.getElementById('userHeader');
  var loginModal = document.getElementById('loginModal');
  var loginEmail = document.getElementById('loginEmail');
  var loginSubmit = document.getElementById('loginSubmit');
  var closeLoginModal = document.getElementById('closeLoginModal');

  function getUser() {
    return sessionStorage.getItem('userEmail');
  }
  function setUser(email) {
    sessionStorage.setItem('userEmail', email);
  }
  function clearUser() {
    sessionStorage.removeItem('userEmail');
  }

  function renderHeader() {
    var email = getUser();
    if (!userHeader) {
      console.error('userHeader div not found!');
      return;
    }
    if (email) {
      userHeader.innerHTML = `
        <button id="logoutBtn" class="btn" style="background:#b3c7f9;color:#333;margin-right:10px;">Log Out</button>
        <span style="font-weight:600;color:#333;">${email}</span>
      `;
      document.getElementById('logoutBtn').onclick = function() {
        clearUser();
        renderHeader();
      };
    } else {
      userHeader.innerHTML = `
        <button id="loginBtn" class="btn" style="background:#b3c7f9;color:#333;">Log In</button>
      `;
      document.getElementById('loginBtn').onclick = function() {
        loginModal.style.display = 'flex';
        loginEmail.value = '';
      };
    }
  }

  // Modal logic
  if (loginModal && closeLoginModal) {
    closeLoginModal.onclick = function() {
      loginModal.style.display = 'none';
    };
    loginModal.onclick = function(e) {
      if (e.target === loginModal) {
        loginModal.style.display = 'none';
      }
    };
  }
  if (loginSubmit) {
    loginSubmit.onclick = function() {
      var email = loginEmail.value.trim();
      if (email && email.includes('@')) {
        setUser(email);
        renderHeader();
        loginModal.style.display = 'none';
      } else {
        loginEmail.style.borderColor = '#dc3545';
        loginEmail.focus();
      }
    };
  }

  // Initial render
  renderHeader();

  // Persist login/logout state across tabs/windows
  window.addEventListener('storage', function(e) {
    if (e.key === 'userEmail') {
      renderHeader();
    }
  });

  // Debug: log if script is running
  console.log('index.js loaded, userHeader:', userHeader);
});
