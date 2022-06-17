var pageCounter = 0;
var movieContainer = document.getElementById("movie_info");
var btn_alpha = document.getElementById("btn_alpha");
var btn = document.getElementById("btn");
var all_btn = document.getElementById("all_btn");
var btn_list= document.getElementById("btn_list");

btn.style.visibility = "hidden"
all_btn.style.visibility = "hidden"

btn_list.addEventListener("click", function(){
var ourRequest = new XMLHttpRequest();
ourRequest.open('GET','static/movies.json');
ourRequest.onload = function() {
    var ourData = JSON.parse(ourRequest.responseText);
    renderHTMLList(ourData);


};


ourRequest.send();
pageCounter = pageCounter + 10;

   btn_alpha.style.visibility = "hidden"
    btn_list.style.visibility = "hidden"
    btn.style.visibility = "visible"
    all_btn.style.visibility = "visible"



function renderHTMLList(data) {
  
    for( i = data.length - 1; i >= data.length - 10; i--){
      
        var htmlString = " ";
        htmlString += "<p> Title: " + data[i].title + "," + " " + data[i].year + ". Cast: " + data[i].cast +  ".</p>";
        movieContainer.insertAdjacentHTML('beforeend', htmlString);
      
      
      }
  
    
}



})
btn.addEventListener("click", function(){
var ourRequest = new XMLHttpRequest();
ourRequest.open('GET','static/movies.json');
ourRequest.onload = function() {
    var ourData = JSON.parse(ourRequest.responseText);
    renderHTML(ourData);


};


ourRequest.send();
btn_list.style.visibility = "hidden"
pageCounter = pageCounter + 10;

    if( pageCounter >= 200){
    btn.style.visibility = "hidden"
        all_btn.style.visibility = "hidden"
}


function renderHTML(data) {

    for (i = data.length - 1; i >= data.length - 10; i--) {
        var htmlString = " ";
        htmlString += "<p>Title: " + data[i-pageCounter].title + ", " + data[i-pageCounter].year + ". Cast: " + data[i-pageCounter].cast + ".</p>";
        movieContainer.insertAdjacentHTML('beforeend', htmlString);



    }
}



})
all_btn.addEventListener("click", function(){
var ourRequest = new XMLHttpRequest();
ourRequest.open('GET','static/movies.json');
ourRequest.onload = function() {
    var ourData = JSON.parse(ourRequest.responseText);
    renderHTMLAll(ourData);


};

ourRequest.send();
    btn_alpha.style.visibility = "hidden"
    btn_list.style.visibility = "hidden"
    all_btn.style.visibility = "hidden"
    btn.style.visibility = "hidden"



function renderHTMLAll(data) {
  
    for (i = data.length -1; i > 0; i--) {
        var htmlString = " ";
        htmlString += "<p>Title: " + data[i - pageCounter].title + ", " + data[i- pageCounter].year + ". Cast: " + data[i- pageCounter].cast + ".</p>";
        movieContainer.insertAdjacentHTML('beforeend', htmlString);



    }
}



})

btn_alpha.addEventListener("click", function(){
var movieTitle = [];
var movieCast = [];
var movieYear = [];
var ourRequest = new XMLHttpRequest();
ourRequest.open('GET','static/movies.json');
ourRequest.onload = function() {
    var ourData = JSON.parse(ourRequest.responseText);
    renderHTMLAll(ourData);


};

ourRequest.send();

  btn_alpha.style.visibility = "hidden"
  btn_list.style.visibility = "hidden"
  all_btn.style.visibility = "hidden"
  btn.style.visibility = "hidden"



function renderHTMLAll(data) {
  
    for (i = 0; i < data.length; i++) {
      movieTitle[i] = data[i].title;

    }
  
  movieTitle.sort();
   for (i = 0; i < data.length; i++) {
     for(j = 0; j < data.length; j++){
       if(movieTitle[i] == data[j].title){
         movieYear[i] = data[j].year;
         movieCast[i] = data[j].cast; 
       }
     }
   }
  for(i = 0; i < data.length; i++){
    var htmlString = " ";
    htmlString += "<p>Title: " + movieTitle[i] + " Cast: " + movieCast[i] + " Year: " + movieYear[i] + ".</p>";
    movieContainer.insertAdjacentHTML('beforeend', htmlString);
  }
}



})
