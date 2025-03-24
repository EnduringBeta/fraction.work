import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

function Card({ player }) {
  return (
    <div id="player-{player.id}" className="Card">
      <div className="Container">
        <h2>{player.player_name} ({player.position})</h2>
        <ul>
          <li>{player.games} Games</li>
          <li>{player.batting_average} AVG</li>
          <li>{player.rbi} RBI</li>
          <li>{player.slugging_percent} Slugging</li>
        </ul>
      </div>
    </div>
  );
}

function App() {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    fetch("/players").then((res) => res.json()).then((data) => {
        setPlayers(data);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Fraction.Work - ⚾ Players</h1>
        <div className="Players">
          {players.map((item, index) =>
            <Card key={index} player={item} />
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
