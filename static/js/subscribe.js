document.addEventListener('DOMContentLoaded', function() {
    // Get tab and layer elements
    var weatherTab = document.getElementById('weatherTab');
    var countdownTab = document.getElementById('countdownTab');
    var subscriptionsTab = document.getElementById('subscriptionsTab');
    var weatherLayer = document.getElementById('weatherLayer');
    var countdownLayer = document.getElementById('countdownLayer');
    var subscriptionsLayer = document.getElementById('subscriptionsLayer');
    console.log('DOMContentLoaded event fired');
    console.log('weatherTab:', weatherTab);
    console.log('countdownTab:', countdownTab);
    console.log('weatherLayer:', weatherLayer);
    console.log('countdownLayer:', countdownLayer);
    
    // Check for success parameter in URL
    var urlParams = new URLSearchParams(window.location.search);
    var successType = urlParams.get('success');
    var tab = urlParams.get('tab') || window.tabValue || 'weather';
    
    // If we have a success parameter, clear the corresponding form
    if (successType === 'weather') {
        clearWeatherForm();
        tab = 'subscriptions'; // Force show subscriptions tab
    } else if (successType === 'countdown') {
        clearCountdownForm();
        tab = 'subscriptions'; // Force show subscriptions tab
    }
    
    showLayer(tab);
    toggleAfterEvent();
    
    weatherTab.addEventListener('click', function(e) {
        e.preventDefault();
        showLayer('weather');
    });
    countdownTab.addEventListener('click', function(e) {
        e.preventDefault();
        showLayer('countdown');
    });
    if (subscriptionsTab) {
        subscriptionsTab.addEventListener('click', function(e) {
            e.preventDefault();
            showLayer('subscriptions');
        });
    }
});

function clearWeatherForm() {
    var form = document.querySelector('#weatherLayer form');
    if (form) {
        form.reset();
        console.log('Weather form cleared');
    }
}

function clearCountdownForm() {
    var form = document.querySelector('#countdownLayer form');
    if (form) {
        form.reset();
        console.log('Countdown form cleared');
    }
}
function showLayer(layer) {
    document.getElementById('weatherLayer').style.display = (layer === 'weather') ? 'block' : 'none';
    document.getElementById('countdownLayer').style.display = (layer === 'countdown') ? 'block' : 'none';
    document.getElementById('subscriptionsLayer').style.display = (layer === 'subscriptions') ? 'block' : 'none';
    document.getElementById('weatherTab').className = (layer === 'weather') ? 'btn btn-primary' : 'btn btn-secondary';
    document.getElementById('countdownTab').className = (layer === 'countdown') ? 'btn btn-primary' : 'btn btn-secondary';
    document.getElementById('subscriptionsTab').className = (layer === 'subscriptions') ? 'btn btn-primary' : 'btn btn-secondary';
}
function toggleAfterEvent() {
    var yearly = document.getElementById('countdown_yearly').checked;
    document.getElementById('afterEventGroup').style.display = yearly ? 'none' : 'block';
}
