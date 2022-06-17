var xhr = new XMLHttpRequest();
var actors = [];
var links = '';
xhr.onload = function () {
  if (xhr.status === 200) {
    responseObject = JSON.parse(xhr.responseText);
     var newContent = '';
    var arrayCount = 0;
    for (var i = 0; i < responseObject.length; i++) {
    if(responseObject[i].cast != ""){
      for (var j = 0; j < responseObject[i].cast.length; j++) {
          if(actors.includes(responseObject[i].cast[j]) == false){

            actors[arrayCount] = responseObject[i].cast[j];
            arrayCount++;
          }
      }
    }
  }
actors.sort();
 for(var i = 0; i < actors.length; ++i){
    newContent += '<a href ="javascript:myFunction(' + i + ');">'+ actors[i] + '</a><br>';
 }
  document.getElementById('content').innerHTML = newContent;
  }
};

function myFunction(num){
  responseObject = JSON.parse(xhr.responseText);
  var newContent = '';
  newContent += '<div class="movie"><p>';
  for (var i = 0; i < responseObject.length; i++) {
    if(responseObject[i].cast != ""){
      for (var j = 0; j < responseObject[i].cast.length; j++){
        if(responseObject[i].cast[j].includes(actors[num]) == true){
          newContent += responseObject[i].title +'<br>';
        }
      }
    }
  }
  newContent += '</p></div>';
  document.getElementById('content').innerHTML = newContent;
};
xhr.open('GET', '/static/movies.json', true);
xhr.send(null);