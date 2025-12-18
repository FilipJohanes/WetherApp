document.addEventListener('DOMContentLoaded', function() {
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
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          alert('Subscription deleted!');
          location.reload();
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
