import React, { useState, useEffect } from 'react';
import { parseISO, format } from  'date-fns'
import Chart from 'chart.js'
import 'bootstrap/dist/css/bootstrap.min.css';

function HeaderCard(props) {
  return (
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">PMI {props.particleSize}</h5>
          <p className="card-text">{ props.value }</p>
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
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'PMI 2.5',
          data: Object.values(pmi25),
          borderWidth: 1,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
        },
        {
          label: 'PMI 10',
          data: Object.values(pmi10),
          borderWidth: 1,
          fill: false,
          borderColor: 'rgb(192, 75, 75)'
        },
      ]
    },
    options: {
      scales: {
        x: {
          type: "timeseries",
        },
        y: {
          beginAtZero: true
        },
        xAxes: {
          ticks: {
            max: 5
          }
        },
        ticks: {
          maxTicksLimit: 10,
        }
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
  
    fetch('/current').then(res => res.json()).then(data => {
      setCurrent25(data['2.5']);
      setCurrent10(data['10']);
    }).catch(error => console.log(error));

    fetch('/series').then(res => res.json()).then(data => {
      const pmi25 = Object.fromEntries(data.map(d => [d[0], d[1]]));
      const pmi10 = Object.fromEntries(data.map(d => [d[0], d[2]]));
      renderChart(pmi25, pmi10);

    }).catch(error => console.log(error));  }, []);

  return (
    <div className="App">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossOrigin="anonymous"></link>

      <div className="container">
        <div className="row text-center">
          <h1>Home Air Quality</h1>
        </div>
        <div className="row justify-content-md-center">
          <div className="col-2">
            <HeaderCard particleSize="2.5" value={current25}></HeaderCard>
          </div>
          <div className="col-2">
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
