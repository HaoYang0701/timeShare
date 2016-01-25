var req;

// Sends a new request to update the to-do list
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    req.open("GET", "/guru/get-dates", true);
    req.send(); 
}

// This function is called for each request readystatechange,
// and it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }

    var data = JSON.parse(req.responseText);


    if (document.getElementById("student") != null) {
       var s_ilist = document.getElementById("s-idates-list");
        var s_slist = document.getElementById("s-sdates-list");
        var s_idata = data.sdata[0].its
        var s_sdata = data.sdata[0].sts
        if (s_ilist != null) {
           while (s_ilist.hasChildNodes()) {
              s_ilist.removeChild(s_ilist.firstChild);
            }
            for (var c = 0; c < s_idata.length; c++) {
              newItem = document.createElement("li");
              newItem.innerHTML = s_idata[c].date + " " + s_idata[c].fromTime + " to "+ s_idata[c].toTime;
              s_ilist.appendChild(newItem)
            }

        }
        if (s_slist != null) {
            while (s_slist.hasChildNodes()) {
                s_slist.removeChild(s_slist.firstChild);
            }
            for (var d = 0; d < s_sdata.length; d++) {
              newItem = document.createElement("li");
              newItem.innerHTML = "<a href=\"/guru/delete-date/" + s_sdata[d].id + "\">X</a> " + s_sdata[d].date + " " + s_sdata[d].fromTime + " to "+ s_sdata[d].toTime;
              s_slist.appendChild(newItem)
            }      
        }
    } 
    else if (document.getElementById("instructor") != null) {

      var i_ilist = document.getElementById("i-idates-list");
      var i_slist = document.getElementById("i-sdates-list");
      var i_idata = data.idata[0].its
      var i_sdata = data.idata[0].sts

      if (i_ilist != null) {
        while (i_ilist.hasChildNodes()) {
          i_ilist.removeChild(i_ilist.firstChild);
        }
        for (var a = 0; a < i_idata.length; a++) {
        var newItem = document.createElement("li");
        newItem.innerHTML = "<a href=\"/guru/delete-date/" + i_idata[a].id + "\">X</a> " + i_idata[a].date + " " + i_idata[a].fromTime + " to "+ i_idata[a].toTime;
        i_ilist.appendChild(newItem)
        }
      }

      if (i_slist != null) {
        while (i_slist.hasChildNodes()) {
          i_slist.removeChild(i_slist.firstChild);
        }
        for (var b = 0; b < i_sdata.length; b++) {
          newItem = document.createElement("li");
          newItem.innerHTML =  i_sdata[b].date + " " + i_sdata[b].fromTime + " to "+ i_sdata[b].toTime;
          i_slist.appendChild(newItem)
        }
      }
    }
}

// causes the sendRequest function to run every 10 seconds
window.setInterval(sendRequest, 20000);


function to24HourTime(time) {
   var hours = Number(time.match(/^(\d+)/)[1]);
  var minutes = Number(time.match(/:(\d+)/)[1]);
  var AMPM = time.match(/\s(.*)$/)[1];
  if(AMPM == "PM" && hours<12) hours = hours+12;
  if(AMPM == "AM" && hours==12) hours = hours-12;
  var sHours = hours.toString();
  var sMinutes = minutes.toString();
  if(hours<10) sHours = "0" + sHours;
  if(minutes<10) sMinutes = "0" + sMinutes;
  //alert(sHours + ":" + sMinutes);
  return sHours + ":" + sMinutes;
}



