var req;

// Sends a new request to update the to-do list
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    req.open("GET", "/guru/get-relevantInterest", true);
    req.send(); 
}

// This function is called for each request readystatechange,
// and it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }

    var data = JSON.parse(req.responseText);

   

    d = document.getElementById("personalizedResults")

    while (d.hasChildNodes()) {
         d.removeChild(d.firstChild);


    }

            for (var key in data) {
            var username =data[key].username
            var userId = data[key].userId
            var rating = data[key].rating
            var description = data[key].description
            var picture = data[key].picture
            var firstName = data[key].firstName
            var lastName = data[key].lastName
            var skillType = data[key].skillType
            var location = data[key].location
            var subject = data[key].subject
            var date = data[key].date

            newd = document.createElement("div");
            newd.className = "row";
            newd.innerHTML = '<a href="/guru/postdetails"><div class="col-md-3"><div class="user-info-wrap"> <a id="listinguser" href="/guru/profile/'+userId+'"><div class="user-image"><img src="/guru'+picture+'" alt="user" class="img-circle user-size2"></div><div class="user-info"><div class="username">'+username+ '</div><div class="username">'+firstName + ' ' + lastName +'</div>'+rating+'<i class="glyphicon glyphicon-star"></i></div></a></div></div><div class="col-md-6"><a href="/guru/postdetails/'+key+'"><p class="subject">'+subject+'</p><p>'+skillType+'</p><p>'+description+'</p></a></div><div class="col-md-3"><br>'+date+'<br>Location:'+ location + '</div>'

            d.appendChild(newd)

        //console.log(data[key].)
     }

    console.log(d)


    
}
// causes the sendRequest function to run every 10 seconds
window.setInterval(sendRequest, 5000);

