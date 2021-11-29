import React, { useState, useEffect } from 'react';
import { parseISO, format } from  'date-fns'
import Chart from 'chart.js'
import 'bootstrap/dist/css/bootstrap.min.css';

const aqiMappings = [
  ['Good', 0],
  ['Moderate', 51],
  ['USG', 101],
  ['Unhealth', 151],
  ['Very Unhealthy', 201],
  ['Hazardous', 301]
]

function getStatus(aqi) {
  for (const mapping of aqiMappings) {
    if (aqi >= mapping[1]){
      return mapping[0]
    }
  }
}

function HeaderCard(props) {
  return (
      <div className="card custom-color bg-gradient-custom-color bg-custom-color">
        <div className="card-body">
          <h5 className="card-title">PMI {props.particleSize}</h5>
          <p className="card-text">{ props.value }</p>
          <p className="card-text">Status: { getStatus(props.value) }</p>
        </div>
    </div>
  );
 }

function renderChart(pmi25, pmi10) {
  const ctx = document.getElementById('myChart').getContext('2d');

  // PPpp = Nov 18, 2021, 10:21:25 PM
  // https://date-fns.org/v2.25.0/docs/format
  const dates = Object.keys(pmi25).map(dt => format(parseISO(dt), 'PPpp'))

  const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'PMI 2.5',
          data: Object.values(pmi25),
          borderWidth: 1,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgb(75, 192, 192)'
        },
        {
          label: 'PMI 10',
          data: Object.values(pmi10),
          borderWidth: 1,
          fill: false,
          borderColor: 'rgb(192, 75, 75)',
          backgroundColor: 'rgb(192, 75, 75)'
        },
      ]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }],
      },
    }
  });
  return myChart
}

function App() {
  const [current25, setCurrent25] = useState(0);
  const [current10, setCurrent10] = useState(0);

  useEffect(() => {
    document.title = 'Home air qualty dashboard'

    fetch('/series').then(res => res.json()).then(data => {
      const pmi25 = Object.fromEntries(data.map(d => [d[0], d[1]]));
      const pmi10 = Object.fromEntries(data.map(d => [d[0], d[2]]));

      const keys = Object.keys(pmi25)
      const lastKey = keys[keys.length - 1];
      setCurrent25(pmi25[lastKey])
      setCurrent10(pmi10[lastKey])

      renderChart(pmi25, pmi10);
    }).catch(error => console.log(error));  }, []);

  return (
    <div className="App">

      <div className="container">
        <div className="row text-center">
          <h1>Home Air Quality</h1>
        </div>
        <div className="row text-center">
          <div className="col-sm-2 offset-md-4">
            <HeaderCard particleSize="2.5" value={current25}></HeaderCard>
          </div>
          <div className="col-sm-2">
            <HeaderCard particleSize="10" value={current10}></HeaderCard>
          </div>
        </div>
        <div className="row">
			    <canvas id="myChart" width="400" height="400"></canvas>
        </div>
      </div>

    </div>
  );
}

export default App;
