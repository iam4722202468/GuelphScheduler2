import * as $ from 'jquery'

var schedules;
var scheduleSize;
var scheduleStart = 0;

// https://stackoverflow.com/questions/3426404/create-a-hexadecimal-colour-based-on-a-string-with-javascript
function hashCode(str) {
  var hash = 0;
    for (var i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
  return hash;
} 

function intToRGB(i){
  var c = (i & 0x00FFFFFF)
    .toString(16)
    .toUpperCase();

  return "00000".substring(0, 6 - c.length) + c;
}

function getCourseInfo(courseCode, callback_)
{
  var toReturn;
  
  $.ajax({
    type: "POST",
    url: "getInfo",
    data: {"Code" : courseCode},
    
    error : function(request, status, error) {
      callback_(error);
    },
    
    success : function(request, status, error) {
      callback_(request);
    }
  });
}

/*$('#schedules-left').on('click', () => {
  schedulesLeft();
}

/*$('#schedules-right').on('click', () => {
  schedulesRight();
}

$('#schedules-all-left').on('click', () => {
  schedulesAllLeft();
}
$('#schedules-all-right').on('click', () => {
  schedulesAllRight();
}
$('#add-class').on('click', () => {
  addClass();
}
$('#reload-criteria').on('click', () => {
  reloadCriteria();
}
$('#add-block').on('click', () => {
  addBlock();
}
$('#update-block').on('click', () => {
  updateBlock();
}*/

function getSchedules(start, end)
{
  addCover();
  $.ajax({
    type: "POST",
    url: "getSchedules",
    data: {"start":start, "end":end},
    
    error : function(request, status, error) {
      console.log(error);
    },
    
    success : function(request, status, error) {
      removeCover();
      
      if (!('error' in request))
      {
        schedules = request['schedules'].slice(0, request['schedules'].length - 1);
        scheduleSize = request['schedules'][request['schedules'].length - 1];
        
        scheduleStart = start
        refreshTable(schedules[0]);
        $(".numberOfInputs").html(scheduleSize);
        $(".showingNumber").html(scheduleStart+1);
        
      } else {
        schedules = [];
        scheduleSize = 0;
        
        console.log(request.error);
        classList = [];
        
        for (x in request['schedules'])
        {
          getCourseInfo(request['schedules'][x], function(data) {
            addToList(data);
          });
        }
        
        scheduleStart = 0;
        $(".numberOfInputs").html(0);
        $(".showingNumber").html(0);
        refreshTable(-1);
      }
      
      $("#canvases").html("");
      createThumbnails(schedules);
    }
  });
}

function makeBlock(toMake)
{
  addBlock();
  currentBlock = blocks[blocks.length-1];
  
  days = ["Mon", "Tues", "Wed", "Thur", "Fri"]
  
  currentBlock[0]['childNodes'][1].value = toMake['Time_Start']
  currentBlock[0]['childNodes'][4].value = toMake['Time_End']
  
  for (y in days)
  {
    if (toMake['Day'].indexOf(days[y]) > -1) {
      blocks[x][parseInt(y)+2]['childNodes'][0].checked = true;
    }
  }
  
}

function createThumbnails(schedules)
{
  $("#canvases").html("")
  for (var x in schedules)
  {
    var canvasName = "canvas" + x
    $("#canvases").append('<canvas id="' + canvasName + '"></canvas>')
    scheduleThumbnail(schedules[x], canvasName)
  }
}

function init()
{
  addCover();
  
  $.ajax({
    type: "POST",
    url: "init",
    data: "",
    error : function(request, status, error) {
      console.log(error);
    },
    success : function(request, status, error) {
      removeCover();
      
      if ('blocks' in request && 'Offerings' in request['blocks'])
        for (x in request['blocks']['Offerings'])
          makeBlock(request['blocks']['Offerings'][x]);
      
      if (!('error' in request))
      {
        schedules = request['schedules'].slice(0, request['schedules'].length - 1);
        
        createThumbnails(schedules)
        
        scheduleSize = request['schedules'][request['schedules'].length - 1];
        refreshTable(schedules[0]);
        $(".numberOfInputs").html(scheduleSize);
        
        for (x in request['schedules'][0])
        {
          getCourseInfo(request['schedules'][0][x]['Course'], function(data) {
            addToList(data);
          });
        }
        $(".showingNumber").html(1);
      } else {
        for (x in request['schedules'])
        {
          getCourseInfo(request['schedules'][x], function(data) {
            addToList(data);
          });
        }
        
        $(".numberOfInputs").html(0);
        $(".showingNumber").html(0);
      }
    }
  });
}
$('#searchbar').keypress(function(event){
  var keycode = (event.keyCode ? event.keyCode : event.which);
  if(keycode == '13'){
     addClass();
  }
});

function getInfo(courseCode)
{
  getCourseInfo(courseCode, function(data) {
    $("#courseModal").modal()
    
    var keys = ['Prerequisites', 'Exclusions', 'Offerings']
    //var permKeys = ['Code', 'Name', 'Description', 'Campus', 'Num_Credits', 'Level']
    
    $("#modal-course-name").html(data['Code'] + ' - ' + data['Name'])
    $("#modal-course-description").html(data['Description'])
    $("#modal-course-campus").html("Offered at " + data['Campus'] + " Campus")
    $("#modal-course-credits").html("Credits: " + data['Num_Credits'])
    $("#modal-course-level").html("Level: " + data['Level'])
    
    $("#modal-course-enrollment").html("Error: enrollment not found")
    $("#modal-course-instructors").html("Error: instructors not found")
    
    for (x in schedules[showingSchedule])
    {
      if (data['Code'] == schedules[showingSchedule][x]['Course'])
      {
        instructorURLs = schedules[showingSchedule][x]['Instructors_URL'].split(" ")
        instructors = schedules[showingSchedule][x]['Instructors'].split(", ")
        
        combinedArray = []
        
        for (i in instructorURLs)
        {
          if (instructorURLs[i] == "NULL")
            combinedArray.push(instructors[i])
          else if (instructorURLs[i] == "TBA")
            combinedArray.push("TBA")
          else
            combinedArray.push('<a target="_blank" href="' + instructorURLs[i] + '">' + instructors[i] + '</a>')
        }
        
        if (schedules[showingSchedule][x]['Instructors_Rating'] == 0)
          schedules[showingSchedule][x]['Instructors_Rating'] = "Unrated"
        
        //console.log(data['Code'] + " found")
        $("#modal-course-enrollment").html("Enrollment: " + schedules[showingSchedule][x]['Enrollment'] + "/" + schedules[showingSchedule][x]['Size'] + " available")
        $("#modal-course-instructors").html("Instructor(s): " + combinedArray.join(", "))
        $("#modal-course-rating").html("Instructor(s) Rating: " + schedules[showingSchedule][x]['Instructors_Rating'])
      }
    }
    
    $("#modal-course-extra").html("")
    
    for (key in keys)
      if (keys[key] in data)
      {
        $("#modal-course-extra").append(keys[key] + ": " + data[keys[key]])
        $("#modal-course-extra").append("<br><br>")
      }
    
  });
}

function updateBlock()
{
  jsonObject = jsonBlocks();
  addCover();
  
  $.ajax({
    type: "POST",
    url: "updateBlock",
    data: {"Offerings" : jsonObject},
    error : function(request, status, error) {
      console.log(error);
    },
    success : function(request, status, error) {
      getSchedules(0, 9);
    }
  });
}

function jsonBlocks()
{
  days = ["Mon, ", "Tues, ", "Wed, ", "Thur, ", "Fri, "]
  objects = []
  
  for (x in blocks)
  {
    tempObject = {}
    tempObject['Time_Start'] = blocks[x][0]['childNodes'][1].value;
    tempObject['Time_End'] = blocks[x][0]['childNodes'][4].value;
    
    dayString = ""
    
    for (y in days)
    {
      if (blocks[x][parseInt(y)+2]['childNodes'][0].checked)
        dayString += days[y]
    }
    
    tempObject['Day'] = dayString.slice(0,-2);
    objects.push(tempObject);
  }
  
  return objects;
}

function timeToPixels(time, multiplyHeight) {
  return multiplyHeight*(Math.floor(time/100))*2 + multiplyHeight*(time - Math.floor(time/100)*100)/30
}

var elements = [];

function lightenColor(color, percent) {
  var num = parseInt(color,16),
    amt = Math.round(2.55 * percent),
    R = (num >> 16) + amt,
    B = (num >> 8 & 0x00FF) + amt,
    G = (num & 0x0000FF) + amt;
  
  return (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (B<255?B<1?0:B:255)*0x100 + (G<255?G<1?0:G:255)).toString(16).slice(1);
};

function createSlot(day, starttime, endtime, info) {
  days = ["Mon", "Tues", "Wed", "Thur", "Fri"]
  
  starttime = parseInt(starttime)-800
  endtime = parseInt(endtime)-800
  
  startY = $("#startY").outerHeight();
  startX = $("#startX").outerWidth() + 2;
  multiplyHeight = $("#findHeightGrid").outerHeight();
  gridWidth = $("#findHeightGrid").outerWidth();
  
  topPlace = timeToPixels(starttime, multiplyHeight);
  bottomPlace = timeToPixels(endtime, multiplyHeight);
  
  startY += topPlace;
  startX += days.indexOf(day) * gridWidth;
  divHeight = bottomPlace - topPlace;
  
  var element = '<div id="slot" style="left: '+startX+'px; top: '+startY+'px; height: ' + divHeight + 'px;">' + info + '</div>';
  element = $(element).width(gridWidth);
  
  var edgeColor = info.split(" ")[0].split("*").slice(0,2).join("");
  var colorHash = intToRGB(hashCode(edgeColor));
  
  element.css("border", "1px solid #" + colorHash);
  element.css("background-color", "#" + lightenColor(colorHash, 60));
  
  elements.push(element);
  $("#courseslots").append(element);
}

function refreshTable(schedule) {
  for(var x in elements) {
    elements[x].remove()
  }
  
  elements = []
  
  if (schedule != -1)
    showSchedule(schedule)
}

var showingSchedule = 0

function showSchedule(schedule)
{
  if (schedules.indexOf(schedule) >= 0)
  {
    showingSchedule = schedules.indexOf(schedule)
    $(".showingNumber").html(showingSchedule + 1 + scheduleStart)
  }
  
  for (course in schedule)
    for (offering in schedule[course]["Offerings"])
    {
      offeringDays = schedule[course]["Offerings"][offering]["Day"].split(", ");
      
      for (day in offeringDays)
      {
        createSlot(offeringDays[day], schedule[course]["Offerings"][offering]["Time_Start"], schedule[course]["Offerings"][offering]["Time_End"], 
          schedule[course]["Offerings"][offering]["Course"] + "*" + schedule[course]["Meeting_Section"] + " (" + schedule[course]["Offerings"][offering]["Section_Type"] + ")<br>" + schedule[course]["Offerings"][offering]["Location"] + "  - " + schedule[course]["Enrollment"] + "/" + schedule[course]["Size"] + " available<br>" + schedule[course]["Instructors"]);
      }
    }
}

function drawGrid(canvasID)
{
  var x = $("#left-panel").outerWidth() * 0.85;
  var y = x*0.6
  
  var c = document.getElementById(canvasID);
  var ctx = c.getContext("2d");
  
  ctx.rect(0, 0, c.width, c.height);
  
  x = c.width
  y = c.height
  
  for (var i = 0; i <= 5; ++i)
  {
    ctx.moveTo(x/5*i,0);
    ctx.lineTo(x/5*i,y);
    ctx.stroke();
  }
  
  for (var i = 0; i <= 7; ++i)
  {
    ctx.moveTo(0,y/7*i);
    ctx.lineTo(x,y/7*i);
    ctx.stroke();
  }
}

function drawSchedule(schedule, canvasID)
{
  var days = ["Mon", "Tues", "Wed", "Thur", "Fri"]
  var c = document.getElementById(canvasID);
  var ctx = c.getContext("2d");
  
  var x = $("#left-panel").outerWidth() * 0.85;
  var y = x*0.6
  
  x = c.width
  y = c.height
  
  for (w in schedule)
    for (w_ in schedule[w]['Offerings'])
    {
      var courseInfo = schedule[w]['Offerings'][w_]
      var dayArray = courseInfo['Day'].split(", ")
      
      var start = parseInt(courseInfo['Time_Start']) - 800
      var end = parseInt(courseInfo['Time_End']) - 800
      start = start/1330*y
      end = end/1330*y
      
      for (day in dayArray)
      {
        var dayNumber = days.indexOf(dayArray[day])
        ctx.fillStyle="#0058f0";
        ctx.fillRect(dayNumber*x/5,start,x/5,end-start); 
      }
    }
}

function scheduleThumbnail(schedule, canvasID)
{
  var days = ["Mon", "Tues", "Wed", "Thur", "Fri"]
  
  var c = document.getElementById(canvasID);
  var ctx = c.getContext("2d");
  
  var x = $("#left-panel").outerWidth() * 0.85;
  var y = x*0.6
  
  $("#" + canvasID).width(x);
  $("#" + canvasID).height(y);
  $("#" + canvasID).css("border", "1px solid #000000")
  $("#" + canvasID).css("cursor", "pointer")
  
  x = c.width
  y = c.height
  
  drawGrid(canvasID)

  c.onmouseenter = function (e) {
    ctx.rect(0, 0, c.width, c.height);
    ctx.fillStyle = "#719dea";
    ctx.fill();
    
    drawGrid(e.target.id)
    drawSchedule(schedule, canvasID)
  };
  
  c.onmouseleave = function (e) {
    ctx.clearRect(0, 0, c.width, c.height);
    drawGrid(e.target.id)
    drawSchedule(schedule, canvasID)
  };
  
  drawSchedule(schedule, canvasID)
}

$(function() {
  
  $("#canvases").on('click', function(e) {
    var canvasClick = parseInt(e.target.id.substr(6));
    if (e.target.id != "canvases")
      showSchedule(refreshTable(schedules[canvasClick]))
  });

  init();
  
  $('.nav-tabs a').click(function(){
    $(this).tab('show');
  })
  
  $('.typeahead').autocomplete({
    minLength: 1,
    
    appendTo: "#results",
    
    dataType: "json",
    contentType: "application/json",
    source: function(req, res) {
      $.get('/searchClass/' + req.term, function(data) {
        res(data);
      });
    },
    select: function (event, ui) {
      $("#searchbar").val(ui.item.Code);
      return false;
    },
    
    focus: function (event, ui) {
      //$("#searchbar").val(ui.item.Code);
      //bug: arrow keys clears field
      
      return false;
      //return true
    }
  
  }).data("ui-autocomplete")._renderItem = function (ul, item) {
    return $("<li></li>")
      .data("item.autocomplete", item)
      .append("<div class=\"divider\"><div class=\"left\"><b>" + item.Code + "</b> - " + item.Name + "</div><div class=\"right\"><i>" + item.Level + " [" + item.Num_Credits + "] " + "</i></div></div>")
      .appendTo(ul);
  };
});  

var classList = []

function deleteClass(courseCode)
{
  addCover();
  $.ajax({
    type: "POST",
    url: "delete",
    data: {"Code" : courseCode},
    
    error : function(request, status, error) {
      console.log(error);
    },
    
    success : function(request, status, error) {
      getSchedules(0,9);
      
      for (x in classList)
      {
        if (classList[x].Code == courseCode) {
          $("div[index='" + classList[x].Code + "']").html("");
          classList.splice(x, 1);
        }
      }
      
      if ('error' in request) {
        console.log(request.error);
      }
    }
  });
}

function addToList(object)
{
  $("#classList").html("")
  classList.push(object)
  
  for (x in classList)
  {
    var element1 = '<div class="classList divider" index="' + classList[x].Code + '">';
    var element2 = '<div class="left">' + classList[x].Code + '<br>' + classList[x].Name + '<br>' + classList[x].Num_Credits + '</div>';
    var element3 = '<div class="right">';
    
    var element4 = '<div class="hoverButton btn btn-primary"><span class="moveDown glyphicon glyphicon-search"></span></div>';
    element4 = $(element4).attr('onClick', 'getInfo("' + classList[x].Code + '");')[0].outerHTML;
    
    var element5 = '<div class="hoverButton btn btn-danger"><span class="moveDown glyphicon glyphicon-remove"></span></div>';
    element5 = $(element5).attr('onClick', 'deleteClass("' + classList[x].Code + '");')[0].outerHTML;
    
    var element6 = '</div><br><br><br><hr class="style-seven" index="' + classList[x].Code + '"></hr></div>';
    
    let element = element1 + element2 + element3 + element4 + element5 + element6
    
    $("#classList").append(element);
  }
}

var cover = null;

function addCover() {
  if (cover === null) {
    startY = $("#startY").outerHeight();
    startX = $("#startX").outerWidth() + 2;
    
    multiplyHeight = $("#findHeightGrid").outerHeight();
    gridWidth = $("#findHeightGrid").outerWidth();
    
    cover = '<div id="loadingCover" style="left: '+startX+'px; top: '+startY+'px;">Loading Courses...</div>'
    cover = $(cover).width(gridWidth*5-1)
    cover = $(cover).height(multiplyHeight*28-1)
    $("#courseslots").append(cover)
  }
}

function removeCover() {
  if (cover !== null) {
    cover[0].outerHTML = "";
    delete cover[0];
    cover = null;
  }
}

/*function reloadAll()
{
  addCover();
  $.ajax({
    type: "POST",
    url: "reload",
    data: {},
    
    error : function(request, status, error) {
      console.log(error);
    },
    
    success : function(request, status, error) {
      removeCover();
      $("#searchbar").val("");
      classList = [];
      init();
    }
  });
}*/

function addClass(object)
{
  var found = false;
  var courseCode = $("#searchbar").val();
  $("#searchbar").val("");
  
  for (x in classList)
    if (classList[x]['Code'] == courseCode)
      found = true;
  
  if (!found)
  {
    addCover();
    
    $.ajax({
      type: "POST",
      url: "add",
      data: {"Code" : courseCode},
      
      error : function(request, status, error) {
        console.log(error);
      },
      
      success : function(request, status, error) {
        console.log(request)
        removeCover();
        
        if (!('error' in request)) {
          addToList(request.course);
          getSchedules(0,9);
        } else {
          console.log(courseCode)
          $("#modal-course-name_").html(" " + courseCode)
          $("#modal-course-error").html(request['error'])
          $("#noSections").modal()
        }
      }
    });
  }
}

function schedulesLeft()
{
  if (scheduleStart > 8)
  {
    scheduleStart -= 9;
    getSchedules(scheduleStart, scheduleStart+9);
  }
}

function schedulesRight()
{
  if (scheduleStart < scheduleSize - 9)
  {
    scheduleStart += 9;
    getSchedules(scheduleStart, scheduleStart+9);
  }
}

function schedulesAllLeft()
{
  scheduleStart = 0;
  getSchedules(scheduleStart, scheduleStart+9);
}

function schedulesAltRight()
{
  if (scheduleSize-9 >= 0)
  {
    scheduleStart = scheduleSize-9
    getSchedules(scheduleStart, scheduleStart+9);
  }
}

var blocks = []

function reloadCriteria()
{
  criteria = {}
  titles = ['.classStart', '.classEnd', '.timeBetween', '.averageTime', '.shortOrLong', '.teacherRating'];
  
  weight = []
  direction = []
  
  for (x in titles) {
    weight.push($(titles[x])[0].valueAsNumber)
    direction.push($(titles[x]+'2')[0].checked | 0)
  }
  
  criteria['Weight'] = weight;
  criteria['Direction'] = direction;
  
  $.ajax({
    type: "POST",
    url: "updateCriteria",
    data: {"Criteria" : criteria},
    error : function(request, status, error) {
      console.log(error);
    },
    success : function(request, status, error) {
      getSchedules(0, 9);
    }
  });
}

function removeBlock(idNumber)
{
  blocks[idNumber].remove();
  delete blocks[idNumber];
}

function addBlock()
{
  var place = blocks.length;
  
  let element = `<div class="input-group">
    <span class="input-group-addon">Start</span>
    <select class="starttime form-control">
    <option value="">
    </option>
    <option value="0800">08:00 - 8am</option>
    <option value="0900">09:00 - 9am</option>
    <option value="1000">10:00 - 10am</option>
    <option value="1100">1100 - 11am</option>
    <option value="1200">12:00 - 12pm</option>
    <option value="1300">13:00 - 1pm</option>
    <option value="1400">14:00 - 2pm</option>
    <option value="1500">15:00 - 3pm</option>
    <option value="1600">16:00 - 4pm</option>
    <option value="1700">17:00 - 5pm</option>
    <option value="1800">18:00 - 6pm</option>
    <option value="1900">19:00 - 7pm</option>
    <option value="2000">20:00 - 8pm</option>
    <option value="2100">21:00 - 9pm</option>
    <option value="2200">22:00 - 10pm</option>
    </select>
    <span class="input-group-btn" style="width:0px;"></span>
    <span class="input-group-addon">End</span>
    <select class="endtime form-control">
    <option value=""></option>
    <option value="0800">08:00 - 8am</option>
    <option value="0900">09:00 - 9am</option>
    <option value="1000">10:00 - 10am</option>
    <option value="1100">1100 - 11am</option>
    <option value="1200">12:00 - 12pm</option>
    <option value="1300">13:00 - 1pm</option>
    <option value="1400">14:00 - 2pm</option>
    <option value="1500">15:00 - 3pm</option>
    <option value="1600">16:00 - 4pm</option>
    <option value="1700">17:00 - 5pm</option>
    <option value="1800">18:00 - 6pm</option>
    <option value="1900">19:00 - 7pm</option>
    <option value="2000">20:00 - 8pm</option>
    <option value="2100">21:00 - 9pm</option>
    <option value="2200">22:00 - 10pm</option>
    </select></div></div>
    <label class="checkbox-inline dayname">
    <input type="checkbox" value="">Mon</label>
    <label class="checkbox-inline dayname">
    <input type="checkbox" value="">Tues</label>
    <label class="checkbox-inline dayname">
    <input type="checkbox" value="">Wed</label>
    <label class="checkbox-inline dayname">
    <input type="checkbox" value="">Thur</label>
    <label class="checkbox-inline dayname">
    <input type="checkbox" value="">Fri</label>
    <div class="hoverButton btn btn-danger" 
      onclick="removeBlock(' + place + ')" 
      style="margin-left: 90%; margin-top: 0px; margin-bottom: 5%;">
    <span class="moveDown glyphicon glyphicon-remove"></span></div>
    <hr class="style-seven">`
  
  element = $(element);
  blocks.push(element);
  $("#blockedTimes").append(element);
}
