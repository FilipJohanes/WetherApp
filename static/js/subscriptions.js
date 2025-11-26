document.addEventListener('DOMContentLoaded', function() {
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
      alert('Save functionality coming soon! ID: ' + btn.dataset.id);
    });
  });
  document.querySelectorAll('.delete-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      alert('Delete functionality coming soon! ID: ' + btn.dataset.id);
    });
  });
});
