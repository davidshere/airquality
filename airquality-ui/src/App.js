import React, { useState, useEffect } from 'react';
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

function App() {
  const [current25, setCurrent25] = useState(0);
  const [current10, setCurrent10] = useState(0);

  useEffect(() => {
    document.title = 'Home air qualty dashboard'
  
    fetch('/current').then(d => {console.log(d); return d}).then(res => res.json()).then(data => {
      setCurrent25(data['2.5']);
      setCurrent10(data['10'])
    }).catch(error => console.log(error));
  }, []);

  return (
    <div className="App">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous"></link>

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
      </div>
    </div>
  );
}

export default App;
