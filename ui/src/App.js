import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

function Card({ player }) {
  const showPlayerDetails = () => {
    console.log(player)
  };

  const editPlayer = () => {
    console.log("Editing player " + player.player_name)
  };

  return (
    <div id={`player-${player.id}`} className="Card" onClick={showPlayerDetails}>
      <div className="Card-container">
        <p className="Player-name">{player.player_name}</p>
        <p className="Player-position">{player.position}</p>
        <ul className="Player-stats">
          <li>{player.games} Games</li>
          <li>{player.batting_average.toFixed(3)} AVG</li>
          <li>{player.rbi} RBI</li>
          <li>{player.slugging_percent.toFixed(3)} Slugging</li>
        </ul>
        <button className="Player-edit-button" onClick={editPlayer}>✏️</button>
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
