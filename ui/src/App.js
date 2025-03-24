import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

const Modal = ({ show, onClose, children }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>X</button>
        {children}
      </div>
    </div>
  );
};

function Card({ player }) {
  const showPlayerDetails = () => {
    // TODOROSS - https://www.npmjs.com/package/react-modal
    console.log(player);
    toggleDetailModal(player);
  };

  const editPlayer = (event) => {
    event.stopPropagation();

    // TODOROSS - https://www.npmjs.com/package/@sumor/llm-connector
    console.log("Editing player " + player.player_name);
    toggleEditModal(player);
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
        <div className="Actions-row">
          <button className="Player-edit-button" onClick={editPlayer}>✏️</button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);

  const [players, setPlayers] = useState([]);
  const [playerFocus, setPlayerFocus] = useState(null);

  const toggleDetailModal = (player) => {
    setPlayerFocus(player);
    setIsDetailModalVisible(!isDetailModalVisible);

    // TODOROSS: confirm these work
    if (!isDetailModalVisible) {
      setPlayerFocus(null);
    }
  };

  const toggleEditModal = (player) => {
    setPlayerFocus(player);
    setIsEditModalVisible(!isEditModalVisible);

    if (!isEditModalVisible) {
      setPlayerFocus(null);
    }
  };

  const onUpdatePlayer = () => {
    fetch("/players", {
      method: "PUT",
      body: JSON.stringify(playerFocus),
    }).then((res) => res.json()).then((data) => {
        // TODOROSS - update UI?
      });
  };

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
      <Modal id="detail-modal" show={isDetailModalVisible} onClose={toggleDetailModal}>
        {playerFocus ? (
          <div>
            <p>{playerFocus.player_name}</p>
            <p>RUN LLM HERE</p>
          </div>
        ) : (<p>No player selected to show details</p>)
        }
      </Modal>
      <Modal id="edit-modal" show={isEditModalVisible} onClose={toggleEditModal}>
        {playerFocus ? (
          <div className="edit-form">
            <label>Player name:</label>
            <input type="text" value={player.player_name}></input>
          </div>
          <button className="save-button" onClick={onUpdatePlayer}>Save changes</button>
        ) : (<p>No player selected to edit</p>)
        }
      </Modal>
    </div>
  );
}

export default App;
