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
    // Get tab state from data attribute
    var tab = window.tabValue || 'weather';
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
