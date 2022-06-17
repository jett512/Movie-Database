var xhr = new XMLHttpRequest();
var totalComedy = 0;
var totalAction = 0;
var totalThriller = 0;
var totalDrama = 0;
var totalHorror = 0;
var totalActors = 0;
xhr.onload = function () {
  if (xhr.status === 200) {
    responseObject = JSON.parse(xhr.responseText);

    var actors = '';
    for (var i = 0; i < responseObject.length; i++) {
          
    if(responseObject[i].cast != ""){
      for (var j = 0; j < responseObject[i].cast.length; j++) {
        if(actors.includes(responseObject[i].cast[j]) == false){
          totalActors++;
          actors += responseObject[i].cast[j] + ' ';
          }
      }
    }
    var newContent = '';
    newContent += '<div class="movie"><p>';
      if(responseObject[i].genres != ""){
        if(responseObject[i].genres.includes("Comedy") == true){
          totalComedy++;
        }
        if(responseObject[i].genres.includes("Action") == true){
          totalAction++;
        }
        if(responseObject[i].genres.includes("Horror") == true){
          totalHorror++;
        }
        if(responseObject[i].genres.includes("Drama") == true){
          totalDrama++;
        }
        if(responseObject[i].genres.includes("Thriller") == true){
          totalThriller++;
          }
        }
      }
  newContent += 'Total number of movies by genre:<br>Comedy: ' + totalComedy + '<br>';
  newContent += 'Action: ' + totalAction + '<br>';
  newContent += 'Horror: ' + totalHorror + '<br>';
  newContent += 'Thriller: ' + totalThriller + '<br>';
  newContent += 'Drama: ' + totalDrama + '<br><br>';
  newContent += 'Total number of Actors in the database: ' + totalActors + '</p><br>';
  newContent += '</div>';
  document.getElementById('content').innerHTML = newContent;
  }
};
xhr.open('GET', '/static/movies.json', true);
xhr.send(null);