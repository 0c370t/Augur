$(document).ready(function(){
  // Set up image display
  iw = $('#imageWrapper');
  iwHeight = iw.css('height');
  iw.css('min-width',iwHeight);


  // Populate endpoint options
  // TODO: Allow a default endpoint selection.
  $.get('getEndpoints', function(routes){
    for(route in routes){
      route = routes[route];
      newOption = document.createElement('option');
      newOption.value = route['route'];
      newOption.textContent = route['description'];
      $('#endpointSelector').append(newOption);
    }
  });
});
