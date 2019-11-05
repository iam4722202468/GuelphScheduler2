require('jquery');
require('webpack-jquery-ui');
require('webpack-jquery-ui/css');

require('bootstrap');
require('bootstrap/scss/bootstrap.scss');
require('font-awesome/css/font-awesome.css');

require('fullcalendar');
require('fullcalendar/dist/fullcalendar.css');

import $ from 'jquery';
window.jQuery = $;
window.$ = $;

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
        
        classList = [];

        if (request.error) {
          $("#modal-course-name_").html('Error')
          $("#modal-course-error").html(request['error'])
          $("#noSections").modal()
        }

        for (let x in request['schedules'])
        {
          getCourseInfo(request['schedules'][x], function(data) {
            addToList(data);
          });
        }
        
        scheduleStart = 0;
        $(".numberOfInputs").html(0);
        $(".showingNumber").html(0);
        refreshTable([]);
      }
      
      $("#canvases").html("");
      createThumbnails(schedules);
    }
  });
}

function makeBlock(toMake)
{
  addBlock();
  const modifyBlock = $("#blockedTimes").children().last();
  
  $(modifyBlock).find('.endtime').val(toMake.Time_End);
  $(modifyBlock).find('.starttime').val(toMake.Time_Start);
  const days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri'];

  days.forEach(day => {
    if (toMake.Day.indexOf(day) !== -1) {
      $(modifyBlock).find(`.${day}`).click();
    }
  });
}

function createThumbnails(schedules)
{
  $("#canvases").html("")
  for (var x in schedules)
  {
    var canvasName = "canvas" + x
    $("#canvases").append(`
      <div class="col-6 col-md-12">
        <canvas id="${canvasName}"></canvas>
      </div>`)
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
        for (let x in request['blocks']['Offerings'])
          makeBlock(request['blocks']['Offerings'][x]);
      
      if (!('error' in request))
      {
        schedules = request['schedules'].slice(0, request['schedules'].length - 1);
        
        createThumbnails(schedules)
        
        scheduleSize = request['schedules'][request['schedules'].length - 1];
        refreshTable(schedules[0]);
        $(".numberOfInputs").html(scheduleSize);
        
        for (let x in request['schedules'][0])
        {
          getCourseInfo(request['schedules'][0][x]['Course'], function(data) {
            addToList(data);
          });
        }
        $(".showingNumber").html(1);
      } else {
        for (let x in request['schedules'])
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


function getInfo(courseCode)
{
  getCourseInfo(courseCode, function(data) {
    
    var keys = ['Prerequisites', 'Exclusions', 'Offerings']
    //var permKeys = ['Code', 'Name', 'Description', 'Campus', 'Num_Credits', 'Level']
    
    $("#modal-course-name").html(data['Code'] + ' - ' + data['Name'])
    $("#modal-course-description").html(data['Description'])
    $("#modal-course-campus").html("Offered at " + data['Campus'] + " Campus")
    $("#modal-course-credits").html("Credits: " + data['Num_Credits'])
    $("#modal-course-level").html("Level: " + data['Level'])
    
    $("#modal-course-enrollment").html("Error: enrollment not found")
    $("#modal-course-instructors").html("Error: instructors not found")
    
    for (let x in schedules[showingSchedule])
    {
      if (data['Code'] == schedules[showingSchedule][x]['Course'])
      {
        let instructorURLs = schedules[showingSchedule][x]['Instructors_URL'].split(" ")
        let instructors = schedules[showingSchedule][x]['Instructors'].split(", ")
        
        let combinedArray = []
        
        for (let i in instructorURLs)
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
    
    for (let key in keys)
      if (keys[key] in data)
      {
        $("#modal-course-extra").append(keys[key] + ": " + data[keys[key]])
        $("#modal-course-extra").append("<br><br>")
      }
    
  });
  $("#courseModal").modal('toggle');
}

function jsonBlocks()
{
  const days = ["Mon", "Tues", "Wed", "Thur", "Fri"];
  let objects = [];

  $('.block-time-container').each((i, el) => {
    const endtime = $(el).find('.endtime').val();
    const starttime = $(el).find('.starttime').val();
    
    let dayList = []
    days.forEach(day => {
      if ($(el).find(`.${day}`)[0].checked) {
        dayList.push(day);
      }
    });

    objects.push({
      Day: dayList.join(', '),
      Time_Start: starttime,
      Time_End: endtime
    });

  });

  return objects;
}

function updateBlock()
{
  const jsonObject = jsonBlocks();
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

var elements = [];

function lightenColor(color, percent) {
  var num = parseInt(color,16),
    amt = Math.round(2.55 * percent),
    R = (num >> 16) + amt,
    B = (num >> 8 & 0x00FF) + amt,
    G = (num & 0x0000FF) + amt;
  
  return (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (B<255?B<1?0:B:255)*0x100 + (G<255?G<1?0:G:255)).toString(16).slice(1);
};


function refreshTable(schedule) {
  for(var x in elements) {
    elements[x].remove()
  }
  
  $('#calendar').fullCalendar('removeEvents');
  
  elements = []
  console.log(schedule);

  const dayList = {
    'Mon': '01',
    'Tues': '02',
    'Wed': '03',
    'Thur': '04',
    'Fri': '05'
  };

  schedule.forEach((course) => {
    course.Offerings.forEach((offering) => {
      offering.Day.split(', ').forEach((day) => {
        var colorHash = intToRGB(hashCode(course.Course));

        const event = {
          id: course.Course,
          title: `${offering.Section_Type} - ${course.Course} - ${course.Meeting_Section}`,
          start: `2018-01-${dayList[day]} ${offering.Time_Start.substr(0, 2)}:${offering.Time_Start.substr(2, 4)}:00`,
          end: `2018-01-${dayList[day]} ${offering.Time_End.substr(0, 2)}:${offering.Time_End.substr(2, 4)}:00`,
          borderColor: `#${colorHash}`,
          backgroundColor: `#${lightenColor(colorHash, 60)}`
        }
        $('#calendar').fullCalendar( 'renderEvent', event, true);
      });
    });
  });

  jsonBlocks().forEach((block) => {
    block.Day.split(', ').forEach((day) => {
      const colorHash = "FF0000"
      const event = {
        id: 42069,
        title: `Blocked`,
        start: `2018-01-${dayList[day]} ${block.Time_Start.substr(0, 2)}:${block.Time_Start.substr(2, 4)}:00`,
        end: `2018-01-${dayList[day]} ${block.Time_End.substr(0, 2)}:${block.Time_End.substr(2, 4)}:00`,
        borderColor: `#${colorHash}`,
        backgroundColor: `#${lightenColor(colorHash, 60)}`
      }
      $('#calendar').fullCalendar( 'renderEvent', event, true);
    });
  });
}

var showingSchedule = 0

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
  
  for (let w in schedule)
    for (let w_ in schedule[w]['Offerings'])
    {
      var courseInfo = schedule[w]['Offerings'][w_]
      var dayArray = courseInfo['Day'].split(", ")
      
      var start = parseInt(courseInfo['Time_Start']) - 800
      var end = parseInt(courseInfo['Time_End']) - 800
      start = start/1330*y
      end = end/1330*y
      
      for (let day in dayArray)
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
  $("#" + canvasID).css('width', '100%');
  $("#" + canvasID).css('height', 'auto');
  $("#" + canvasID).css('min-height', '90px');
  
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
      refreshTable(schedules[canvasClick])
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
  
  }).data("ui-autocomplete")._renderItem = (ul, item) => 
    $("<li></li>")
      .data("item.autocomplete", item)
      .append(`
        <div class="divider">
          <div class="left">
            <b>${item.Code}</b> - ${item.Name}
          </div>
          <div class="right">
            <i>${item.Level}[${item.Num_Credits}]</i>
          </div>
        </div>`)
      .appendTo(ul);
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
      
      for (let x in classList)
      {
        if (classList[x].Code == courseCode) {
          $(`div[index='${classList[x].Code}']`).remove();
          classList.splice(x, 1);
        }
      }
      
      if ('error' in request) {
        console.log(request.error);
      }
    }
  });
}

function getInfoPre(e) {
  getInfo($(e.target).closest('.get-info').attr('place'));
}

function deleteClassPre(e) {
  deleteClass($(e.target).closest('.delete-class').attr('place'));
}

function addToList(object)
{
  $("#classList").html("")
  classList.push(object)
  
  for (let x in classList)
  {
    let colorHash = intToRGB(hashCode(classList[x].Code));
    let lighterColor = lightenColor(colorHash, 60);

    const element = `
      <div class="row classlist-el divider"
        style="border: solid 2px #${colorHash};
        background-color: #${lighterColor};"
        index="${classList[x].Code}">
        <div class="col-9">
          <b>${classList[x].Code}</b><br>
          ${classList[x].Name}<br>
          ${classList[x].Num_Credits}
        </div>
        <div place=${classList[x].Code}
        class="col-1 get-info hoverButton btn btn-outline-primary">
          <i class="moveDown fa fa-info"></i>
        </div>
        <div place=${classList[x].Code} 
        class="col-1 delete-class hoverButton btn btn-outline-danger">
          <i class="moveDown fa fa-trash"></i>
        </div>
        <div class="col-1"></div>
      </div>
    `;
    $("#classList").append(element);
  }

  $('.get-info').on('click', getInfoPre);
  $('.delete-class').on('click', deleteClassPre);
}

function addCover() {
  $('#calendar').hide();
  $('#loading').show();
}

function removeCover() {
  $('#calendar').show();
  $('#loading').hide();
}

function addClass(object)
{
  var found = false;
  var courseCode = $("#searchbar").val();
  $("#searchbar").val("");
  
  for (let x in classList)
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
        removeCover();
        
        console.log(request)

        if (request.error) {
          $("#modal-course-name_").html('Error')
          $("#modal-course-error").html(request['error'])
          $("#noSections").modal()
        } else {
          addToList(request.course);
          getSchedules(0,9);
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

function schedulesAllRight()
{
  if (scheduleSize-9 >= 0)
  {
    scheduleStart = scheduleSize-9
    getSchedules(scheduleStart, scheduleStart+9);
  }
}

var blocks = [];

function reloadCriteria()
{
  let criteria = [];
  const titles = [
    '#timeBetween',
    '#averageTime',
    '#classLength',
    '#professorRating'
  ];
  
  for (let x in titles) {
    criteria.push($(titles[x])[0].valueAsNumber);
  }
  
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

function removeBlock(idNumber) {
  blocks[idNumber].remove();
  delete blocks[idNumber];
}

function removeBlockPre(e) {
  removeBlock($(e.target).attr('place'));
}

function addBlock() {
  var place = blocks.length;
  
  let element = `
    <div class="block-time-container">
      <div class="input-group">
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
        </select>
      </div>
    <label class="checkbox-inline dayname">
    <input class="Mon" type="checkbox" value="">Mon</label>
    <label class="checkbox-inline dayname">
    <input class="Tues" type="checkbox" value="">Tues</label>
    <label class="checkbox-inline dayname">
    <input class="Wed" type="checkbox" value="">Wed</label>
    <label class="checkbox-inline dayname">
    <input class="Thur" type="checkbox" value="">Thur</label>
    <label class="checkbox-inline dayname">
    <input class="Fri" type="checkbox" value="">Fri</label>
    <div class="hoverButton btn btn-danger remove-block"
      place="${place}"
      style="margin-left: 90%; margin-top: 0px; margin-bottom: 5%;">
    <i class="moveDown fa fa-trash"></i></div>
    <hr class="style-seven"></div>`
  
  element = $(element);
  blocks.push(element);
  $("#blockedTimes").append(element);
  $('.remove-block').on('click', removeBlockPre);
}

$(document).ready(function() {
  $('#schedules-left').on('click', () => {
    schedulesLeft();
  });

  $('#schedules-right').on('click', () => {
    schedulesRight();
  });

  $('#schedules-all-left').on('click', () => {
    schedulesAllLeft();
  });

  $('#schedules-all-right').on('click', () => {
    schedulesAllRight();
  });

  $('#add-class').on('click', () => {
    addClass();
  });

  $('#reload-criteria').on('click', () => {
    reloadCriteria();
  });

  $('#add-block').on('click', () => {
    addBlock();
  });

  $('#update-block').on('click', () => {
    updateBlock();
  });

  $('#searchbar').on('keypress', (event) => {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13'){
       addClass();
    }
  });

  $('#calendar').fullCalendar({
    header: false,
    defaultView: 'agendaWeek',
    allDayText: '',
    columnHeaderFormat: 'ddd',
    minTime: '08:00:00',
    hiddenDays: [0, 6],
    defaultDate: '2018-01-01',
    navLinks: false,
    editable: false,
    contentHeight: 880,
    eventLimit: false,
    eventClick: function(calEvent, jsEvent, view) {
      getInfo(calEvent.id);
    },
    eventRender: function(event, element) {
      element.css("cursor", "pointer");
    }

  });
});
