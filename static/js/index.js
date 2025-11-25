document.addEventListener('DOMContentLoaded', function() {
  var accountBtn = document.getElementById('accountBtn');
  var accountModal = document.getElementById('accountModal');
  var closeAccountModal = document.getElementById('closeAccountModal');

  if (accountBtn && accountModal && closeAccountModal) {
    accountBtn.addEventListener('click', function() {
      accountModal.style.display = 'flex';
    });
    closeAccountModal.addEventListener('click', function() {
      accountModal.style.display = 'none';
    });
    accountModal.addEventListener('click', function(e) {
      if (e.target === accountModal) {
        accountModal.style.display = 'none';
      }
    });
  }
});
