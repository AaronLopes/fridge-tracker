// Load Charts and the corechart package.
google.charts.load('current', {'packages':['corechart']});
google.charts.load('current', {'packages':['line']});

// Draw line chart to display temperature data when Charts is loaded.
google.charts.setOnLoadCallback(drawTempChart);

// Draw line chart to display pressure data when Charts is loaded.
google.charts.setOnLoadCallback(drawPresChart);

// Draw line chart to display pressure data when Charts is loaded.
google.charts.setOnLoadCallback(drawFlowChart);

// Callback that draws the line chart for temperature data 
function drawTempChart() {

  // Query temp data from sheet
  var query = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1BXX9xQkytohHl4pVvSzlY9WEamZoQv_-gYBZbVp667s/edit?usp=sharing&sheet=Temperature');
  query.setQuery('select B, C, D, F, G, H limit 500')
  query.send(handleTempDataResponse);
}

function handleTempDataResponse(response) {
  if (response.isError()) {
    alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    return;
  }

  var data = response.getDataTable();
  

  var options = {
      title: 'Temperature Data',
      curveType: 'function',
      width: 900,
      height: 400,
      hAxis: {
        title: 'Time (EST)'
      },
      vAxis: {
          scaleType: 'log',
          title: 'Temperature (K)'
      },
      explorer: {keepInBounds: true}
    };
  //console.log(data)
  var chart = new google.visualization.LineChart(document.getElementById('temp_chart_div'));
  chart.draw(data, options);
}


// Callback that draws the line chart for temperature data 
function drawPresChart() {

  // Query temp data from sheet
  var query = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1BXX9xQkytohHl4pVvSzlY9WEamZoQv_-gYBZbVp667s/edit?usp=sharing&sheet=Pressure');
  query.setQuery('select B, C, D, E, F, G, H limit 500')
  query.send(handlePresDataResponse);
}

function handlePresDataResponse(response) {
  if (response.isError()) {
    alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    return;
  }

  var data = response.getDataTable();
  var options = {
      title: 'Pressure Data',
      curveType: 'function',
      width: 900,
      height: 400,
      hAxis: {
        title: 'Time (EST)'
      },
      vAxis: {
          scaleType: 'log',
          title: 'Pressure (mBar)'
      },
      explorer: {keepInBounds: true}
    };
  //console.log(data)
  var chart = new google.visualization.LineChart(document.getElementById('pres_chart_div'));
  chart.draw(data, options);
}

// Callback that draws the line chart for temperature data 
function drawFlowChart() {

  // Query temp data from sheet
  var query = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1BXX9xQkytohHl4pVvSzlY9WEamZoQv_-gYBZbVp667s/edit?usp=sharing&sheet=Flowmeter');
  query.setQuery('select B, C limit 500')
  query.send(handleFlowDataResponse);
}

function handleFlowDataResponse(response) {
  if (response.isError()) {
    alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    return;
  }

  var data = response.getDataTable();
  var options = {
      title: 'Flowmeter Data',
      curveType: 'function',
      width: 900,
      height: 400,
      hAxis: {
        title: 'Time (EST)'
      },
      vAxis: {
          title: 'Flow (mmol/s)'
      },
      explorer: {keepInBounds: true}
    };
  //console.log(data)
  var chart = new google.visualization.LineChart(document.getElementById('flow_chart_div'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}