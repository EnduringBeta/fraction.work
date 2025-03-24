import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

const DetailModal = ({ show, player, onClose }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>❌</button>
        {player ? (
          <div>
            <p>{player.player_name}</p>
            <p>RUN LLM HERE</p>
          </div>
        ) : (<p>No player selected to show details</p>)
        }
      </div>
    </div>
  );
};

// TODOROSS: exit after update?
const EditModal = ({ show, player, onUpdatePlayer, onClose }) => {
  const [editedPlayer, setEditedPlayer] = useState(player);

  if (!show) return null;

  const handleChange = (event) => {
    console.log(event);
    console.log(editedPlayer);
    setEditedPlayer({ ...editedPlayer, [event.target.name]: event.target.value });
    console.log(editedPlayer);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>❌</button>
        {editedPlayer ? (
          <div>
            <div className="edit-form">
              <label>Player name:</label>
              <input type="text" value={editedPlayer.player_name} onChange={handleChange}></input>
            </div>
            <button className="save-button" onClick={onUpdatePlayer}>Save changes</button>
          </div>
        ) : (<p>No player selected to edit</p>)
        }
      </div>
    </div>
  );
};

function Card({ player, onDetail, onEdit }) {
  const showPlayerDetails = () => {
    console.log(player);

    onDetail(player);
  };

  const editPlayer = (event) => {
    event.stopPropagation();
    console.log("Editing player " + player.player_name);

    // TODOROSS - https://www.npmjs.com/package/@sumor/llm-connector
    onEdit(player);
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

  const toggleDetailModal = () => {
    setIsDetailModalVisible(!isDetailModalVisible);
  };

  const toggleEditModal = () => {
    setIsEditModalVisible(!isEditModalVisible);
  };

  const openDetailModal = (player) => {
    setPlayerFocus(player);
    toggleDetailModal();
  }

  const openEditModal = (player) => {
    setPlayerFocus(player);
    toggleEditModal();
  }

  const updatePlayer = () => {
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
            <Card key={index} player={item} onDetail={() => openDetailModal(item)}
              onEdit={() => openEditModal(item)} />
          )}
        </div>
      </header>
      <DetailModal id="detail-modal" show={isDetailModalVisible} player={playerFocus}
        onClose={toggleDetailModal} />
      <EditModal id="edit-modal" show={isEditModalVisible} player={playerFocus}
        onUpdatePlayer={updatePlayer} onClose={toggleEditModal} />
    </div>
  );
}

export default App;
