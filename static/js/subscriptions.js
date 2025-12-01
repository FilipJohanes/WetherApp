document.addEventListener('DOMContentLoaded', function() {
  // Show active subscriptions when 'Active Subscriptions' tab is clicked
  var subscriptionsTab = document.getElementById('subscriptionsTab');
  var subscriptionsLayer = document.getElementById('subscriptionsLayer');
  var weatherLayer = document.getElementById('weatherLayer');
  var countdownLayer = document.getElementById('countdownLayer');
  var subsList = document.getElementById('subscriptionsList');

  function getUserEmail() {
    const email = sessionStorage.getItem('userEmail');
    console.log('[DEBUG] getUserEmail:', email);
    return email;
  }

  function fetchSubscriptions() {
    var email = getUserEmail();
    console.log('[DEBUG] fetchSubscriptions: email', email);
    if (!email) {
      subsList.innerHTML = '<p>No active subscriptions found.</p>';
      console.log('[DEBUG] No email found, abort fetchSubscriptions');
      return;
    }
      var subsCards = document.getElementById('subscriptionsCards');
      if (subsCards) subsCards.innerHTML = '<span>Loading...</span>';
    console.log('[DEBUG] Sending fetch to /api/get_subscriptions');
    fetch('/api/get_subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
      console.log('[DEBUG] API get_subscriptions response:', data);
      let html = '';
      console.log('[DEBUG] Building subscriptions HTML');
      // Only render subscription cards, not header or debug info
      let index = 0;
      let found = false;
      if (data.weather && Object.keys(data.weather).length > 0) {
          console.log('[DEBUG] Found weather subscription:', data.weather);
        const subId = `weather_${getUserEmail()}`;
        html += `<div class="subscription-card" style="border-bottom: 1px solid #e0e0e0; padding: 12px 0; display: flex; align-items: center; background: none; position: relative;">
          <div style="flex: 2;">${data.weather.location}</div>
          <div style="flex: 1;">Weather</div>
          <div style="flex: 1;">${data.weather.date_added ? data.weather.date_added.split('T')[0] : ''}</div>
          <div style="flex: 0 0 80px; display: flex; gap: 8px; justify-content: flex-end;">
            <button type="button" class="btn btn-primary btn-sm edit-btn" data-id="${subId}" data-type="weather" data-index="${index}" title="Edit" style="padding: 4px 8px; border-radius: 8px;">
              <img src="/static/icons/edit.svg" alt="Edit" style="width: 24px; height: 24px;">
            </button>
            <button type="button" class="btn btn-danger btn-sm delete-btn" data-id="${subId}" title="Delete" style="padding: 4px 8px; border-radius: 8px;">
              <img src="/static/icons/delete.svg" alt="Delete" style="width: 24px; height: 24px;">
            </button>
          </div>
        </div>
        <div class="edit-modal-backdrop" id="edit-modal-backdrop-${subId}"></div>
        <div class="edit-modal" id="edit-modal-${subId}">
          <h3>Edit Subscription</h3>
          <form class="edit-weather-form">
            <div class="form-group">
              <label>Email</label>
              <input type="email" name="email" value="${getUserEmail()}" required>
            </div>
            <div class="form-group">
              <label>Location</label>
              <input type="text" name="location" value="${data.weather.location}">
            </div>
            <div class="form-group">
              <label>Language</label>
              <select name="language">
                <option value="en" ${data.weather.language === 'en' ? 'selected' : ''}>English</option>
                <option value="es" ${data.weather.language === 'es' ? 'selected' : ''}>Spanish</option>
                <option value="sk" ${data.weather.language === 'sk' ? 'selected' : ''}>Slovak</option>
              </select>
            </div>
            <div class="form-group">
              <label>Personality</label>
              <select name="personality">
                <option value="neutral" ${data.weather.personality === 'neutral' ? 'selected' : ''}>Neutral</option>
                <option value="cute" ${data.weather.personality === 'cute' ? 'selected' : ''}>Cute</option>
                <option value="brutal" ${data.weather.personality === 'brutal' ? 'selected' : ''}>Brutal</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-success save-edit-btn" data-id="${subId}">Save Changes</button>
              <button type="button" class="btn btn-secondary cancel-edit-btn" data-id="${subId}">Cancel</button>
            </div>
          </form>
        </div>`;
        found = true;
        index++;
      }
      if (Array.isArray(data.countdowns) && data.countdowns.length > 0) {
          console.log('[DEBUG] Found countdown subscriptions:', data.countdowns);
        data.countdowns.forEach(cd => {
          const subId = `countdown_${cd.name}_${cd.date}`;
          html += `<div class="subscription-card" style="border-bottom: 1px solid #e0e0e0; padding: 12px 0; display: flex; align-items: center; background: none; position: relative;">
            <div style="flex: 2;">${cd.name}</div>
            <div style="flex: 1;">Countdown</div>
            <div style="flex: 1;">${cd.date}</div>
            <div style="flex: 0 0 80px; display: flex; gap: 8px; justify-content: flex-end;">
              <button type="button" class="btn btn-primary btn-sm edit-btn" data-id="${subId}" data-type="countdown" data-index="${index}" title="Edit" style="padding: 4px 8px; border-radius: 8px;">
                <img src="/static/icons/edit.svg" alt="Edit" style="width: 24px; height: 24px;">
              </button>
              <button type="button" class="btn btn-danger btn-sm delete-btn" data-id="${subId}" title="Delete" style="padding: 4px 8px; border-radius: 8px;">
                <img src="/static/icons/delete.svg" alt="Delete" style="width: 24px; height: 24px;">
              </button>
            </div>
          </div>
          <div class="edit-modal-backdrop" id="edit-modal-backdrop-${subId}"></div>
          <div class="edit-modal" id="edit-modal-${subId}">
            <h3>Edit Subscription</h3>
            <form class="edit-countdown-form">
              <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" value="${getUserEmail()}" required>
              </div>
              <div class="form-group">
                <label>Countdown Name</label>
                <input type="text" name="name" value="${cd.name}">
              </div>
              <div class="form-group">
                <label>Date</label>
                <input type="date" name="date" value="${cd.date}">
              </div>
              <div class="form-group">
                <label>Yearly event</label>
                <input type="checkbox" name="yearly" ${cd.yearly ? 'checked' : ''}>
              </div>
              <div class="form-group">
                <label>Message before event</label>
                <input type="text" name="message_before" value="${cd.message_before}">
              </div>
              <div class="modal-actions">
                <button type="button" class="btn btn-success save-edit-btn" data-id="${subId}">Save Changes</button>
                <button type="button" class="btn btn-secondary cancel-edit-btn" data-id="${subId}">Cancel</button>
              </div>
            </form>
          </div>`;
          found = true;
          index++;
        });
      }
      if (!found) {
          console.log('[DEBUG] No subscriptions found in API response');
        html += '<p>No active subscriptions found.</p>';
      }
        if (subsCards) subsCards.innerHTML = html;
        console.log('[DEBUG] Subscriptions HTML rendered to DOM');
      // Re-attach modal and button event listeners after rendering
        subsCards.querySelectorAll('.edit-modal').forEach(function(modal) {
          console.log('[DEBUG] Hiding all modals on render');
        modal.style.display = 'none';
      });
        subsCards.querySelectorAll('.edit-modal-backdrop').forEach(function(backdrop) {
        backdrop.style.display = 'none';
      });
        subsCards.querySelectorAll('.edit-btn').forEach(function(btn) {
          console.log('[DEBUG] Attaching edit-btn click listeners');
        btn.addEventListener('click', function() {
                    console.log('[DEBUG] Edit button clicked:', btn.dataset.id);
            subsCards.querySelectorAll('.edit-modal').forEach(function(modal) {
            modal.style.display = 'none';
          });
            subsCards.querySelectorAll('.edit-modal-backdrop').forEach(function(backdrop) {
            backdrop.style.display = 'none';
          });
          var modalId = 'edit-modal-' + btn.dataset.id;
          var backdropId = 'edit-modal-backdrop-' + btn.dataset.id;
          var modalEl = document.getElementById(modalId);
          var backdropEl = document.getElementById(backdropId);
          if (modalEl && backdropEl) {
            modalEl.style.display = 'block';
            backdropEl.style.display = 'block';
          }
        });
      });
        subsCards.querySelectorAll('.cancel-edit-btn').forEach(function(btn) {
          console.log('[DEBUG] Attaching cancel-edit-btn click listeners');
                  console.log('[DEBUG] Cancel edit button clicked:', btn.dataset.id);
        btn.addEventListener('click', function() {
          var modalId = 'edit-modal-' + btn.dataset.id;
          var backdropId = 'edit-modal-backdrop-' + btn.dataset.id;
          var modalEl = document.getElementById(modalId);
          var backdropEl = document.getElementById(backdropId);
          if (modalEl && backdropEl) {
            modalEl.style.display = 'none';
            backdropEl.style.display = 'none';
          }
        });
      });
        subsCards.querySelectorAll('.save-edit-btn').forEach(function(btn) {
          console.log('[DEBUG] Attaching save-edit-btn click listeners');
                  console.log('[DEBUG] Save edit button clicked:', btn.dataset.id);
        btn.addEventListener('click', function() {
          var modalId = 'edit-modal-' + btn.dataset.id;
          var modalEl = document.getElementById(modalId);
          if (!modalEl) return;
          var form = modalEl.querySelector('form');
                    console.log('[DEBUG] Found form in modal:', !!form);
          if (!form) return;
          var formData = {};
          Array.from(form.elements).forEach(function(el) {
                        console.log('[DEBUG] Form element:', el.name, el.value, el.type);
            if (el.name) {
              if (el.type === 'checkbox') {
                formData[el.name] = el.checked;
              } else {
                formData[el.name] = el.value;
              }
            }
          });
          formData['id'] = btn.dataset.id;
          console.log('[DEBUG] Sending update_subscription AJAX:', formData);
          fetch('/api/update_subscription', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
          })
          .then(response => response.json())
          .then(data => {
            console.log('[DEBUG] update_subscription response:', data);
            if (data.status === 'success') {
              alert('Subscription updated!');
              modalEl.style.display = 'none';
              var backdropEl = document.getElementById('edit-modal-backdrop-' + btn.dataset.id);
              if (backdropEl) backdropEl.style.display = 'none';
              location.reload();
            } else {
              alert('Error: ' + data.message);
            }
          })
          .catch(err => {
            alert('Error saving subscription: ' + err);
          });
        });
      });
        subsCards.querySelectorAll('.delete-btn').forEach(function(btn) {
          console.log('[DEBUG] Attaching delete-btn click listeners');
                  console.log('[DEBUG] Delete button clicked:', btn.dataset.id);
        btn.addEventListener('click', function() {
          if (!confirm('Are you sure you want to delete this subscription?')) return;
          console.log('[DEBUG] Sending delete_subscription AJAX:', btn.dataset.id);
          fetch('/api/delete_subscription', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: btn.dataset.id })
          })
            .then(async response => {
              let data;
              try {
                data = await response.json();
                console.log('[DEBUG] delete_subscription response:', data);
              } catch (e) {
                alert('Error deleting subscription: Server returned invalid response.');
                return;
              }
              if (data.status === 'success') {
                 alert('Subscription deleted!');
                 window.setTimeout(function() { location.reload(); }, 100);
              } else {
                alert('Error: ' + (data.message || 'Could not delete subscription.'));
              }
            })
            .catch(err => {
              alert('Error deleting subscription: ' + err);
            });
        });
      });
    })
    .catch(() => {
      subsList.innerHTML = '<span style="color:#dc3545;">Error loading subscriptions.</span>';
    });
  }

  if (subscriptionsTab) {
    subscriptionsTab.addEventListener('click', function() {
      if (weatherLayer) weatherLayer.style.display = 'none';
      if (countdownLayer) countdownLayer.style.display = 'none';
      if (subscriptionsLayer) subscriptionsLayer.style.display = 'block';
      fetchSubscriptions();
    });
  }
  // Hide all modals and backdrops on page load
  document.querySelectorAll('.edit-modal').forEach(function(modal) {
    modal.style.display = 'none';
  });
  document.querySelectorAll('.edit-modal-backdrop').forEach(function(backdrop) {
    backdrop.style.display = 'none';
  });
  document.querySelectorAll('.edit-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      // Hide all modals first
      document.querySelectorAll('.edit-modal').forEach(function(modal) {
        modal.style.display = 'none';
      });
      document.querySelectorAll('.edit-modal-backdrop').forEach(function(backdrop) {
        backdrop.style.display = 'none';
      });
      // Show the modal and backdrop for this event
      var modalId = 'edit-modal-' + btn.dataset.id;
      var backdropId = 'edit-modal-backdrop-' + btn.dataset.id;
      var modalEl = document.getElementById(modalId);
      var backdropEl = document.getElementById(backdropId);
      if (modalEl && backdropEl) {
        modalEl.style.display = 'block';
        backdropEl.style.display = 'block';
      }
    });
  });
  document.querySelectorAll('.cancel-edit-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var modalId = 'edit-modal-' + btn.dataset.id;
      var backdropId = 'edit-modal-backdrop-' + btn.dataset.id;
      var modalEl = document.getElementById(modalId);
      var backdropEl = document.getElementById(backdropId);
      if (modalEl && backdropEl) {
        modalEl.style.display = 'none';
        backdropEl.style.display = 'none';
      }
    });
  });
  document.querySelectorAll('.save-edit-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var modalId = 'edit-modal-' + btn.dataset.id;
      var modalEl = document.getElementById(modalId);
      if (!modalEl) return;
      // Find the form inside the modal
      var form = modalEl.querySelector('form');
      if (!form) return;
      // Collect form data
      var formData = {};
      Array.from(form.elements).forEach(function(el) {
        if (el.name) {
          if (el.type === 'checkbox') {
            formData[el.name] = el.checked;
          } else {
            formData[el.name] = el.value;
          }
        }
      });
      formData['id'] = btn.dataset.id;
      // Send AJAX request to backend
      fetch('/api/update_subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          alert('Subscription updated!');
          modalEl.style.display = 'none';
          var backdropEl = document.getElementById('edit-modal-backdrop-' + btn.dataset.id);
          if (backdropEl) backdropEl.style.display = 'none';
          location.reload();
        } else {
          alert('Error: ' + data.message);
        }
      })
      .catch(err => {
        alert('Error saving subscription: ' + err);
      });
    });
  });
  document.querySelectorAll('.delete-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      if (!confirm('Are you sure you want to delete this subscription?')) return;
      fetch('/api/delete_subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: btn.dataset.id })
      })
        .then(async response => {
          let data;
          try {
            data = await response.json();
          } catch (e) {
            // If response is not JSON, show generic error
            alert('Error deleting subscription: Server returned invalid response.');
            return;
          }
          if (data.status === 'success') {
             alert('Subscription deleted!');
             // Only reload after user closes the alert
             window.setTimeout(function() { location.reload(); }, 100);
          } else {
            alert('Error: ' + (data.message || 'Could not delete subscription.'));
          }
        })
        .catch(err => {
          alert('Error deleting subscription: ' + err);
        });
    });
  });
});
