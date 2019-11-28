// Load Charts and the corechart package.
google.charts.load('current', {'packages':['corechart']});
google.charts.load('current', {'packages':['line']});


// Draw line chart to display temperature data when Charts is loaded.
google.charts.setOnLoadCallback(drawTempChart);

// Draw line chart to display pressure data when Charts is loaded.
google.charts.setOnLoadCallback(drawPresChart);

// Callback that draws the line chart for temperature data 
function drawTempChart() {

  // Query temp data from sheet
  var query = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1NGcHLuAWhcbnHtlnTRmzgdGae_5xIRjQ53uHW-hefhE/edit?usp=sharing&sheet=Temperature');
  query.setQuery('select B, C, D, E, F, G limit 20')
  query.send(handleTempDataResponse);
}

function handleTempDataResponse(response) {
  if (response.isError()) {
    alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    return;
  }

  var data = response.getDataTable();
  var options = {
      chart: {
        title: 'BlueFors Temperature',
      },
      curveType: 'function',
      width: 700,
      height: 400,
      vAxes: {
          // Adds titles to each axis.
          0: {title: 'Temperature (Kelvin)'}
      }
    };
  //console.log(data)
  var chart = new google.charts.Line(document.getElementById('temp_chart_div'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}


// Callback that draws the line chart for temperature data 
function drawPresChart() {

  // Query temp data from sheet
  var query = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1NGcHLuAWhcbnHtlnTRmzgdGae_5xIRjQ53uHW-hefhE/edit?usp=sharing&sheet=Pressure');
  query.setQuery('select B, C, D, E, F, G limit 20')
  query.send(handlePresDataResponse);
}

function handlePresDataResponse(response) {
  if (response.isError()) {
    alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
    return;
  }

  var data = response.getDataTable();
  var options = {
      chart: {
        title: 'BlueFors Pressure',
      },
      curveType: 'function',
      width: 700,
      height: 400,
      vAxes: {
          // Adds titles to each axis.
          0: {title: 'Pressure (Atmosphere)'}
      }
    };
  //console.log(data)
  var chart = new google.charts.Line(document.getElementById('pres_chart_div'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}
