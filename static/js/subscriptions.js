document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.edit-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      // Hide all edit forms first
      document.querySelectorAll('.edit-form-container').forEach(function(form) {
        form.style.display = 'none';
      });
      // Show the edit form for this event
      var formId = 'edit-form-' + btn.dataset.id;
      var formEl = document.getElementById(formId);
      if (formEl) {
        formEl.style.display = 'block';
      }
    });
  });
  document.querySelectorAll('.cancel-edit-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var formId = 'edit-form-' + btn.dataset.id;
      var formEl = document.getElementById(formId);
      if (formEl) {
        formEl.style.display = 'none';
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
