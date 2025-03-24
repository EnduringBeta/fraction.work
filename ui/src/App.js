import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

const DetailModal = ({ show, player, description, loading, onClose }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>❌</button>
        {loading ? (<p>Loading player details...</p>)
          : player ? (
            <div>
              <p>{player.player_name}</p>
              <p>{description}</p>
            </div>
          ) : (<p>No player selected to show details</p>)
        }
      </div>
    </div>
  );
};

// TODO: add more fields
const EditModal = ({ show, player, onUpdatePlayer, onClose }) => {
  const [editedPlayer, setEditedPlayer] = useState(player);

  useEffect(() => {
    setEditedPlayer(player);
  }, [player]);

  if (!show) return null;

  const handleChange = (event) => {
    setEditedPlayer({ ...editedPlayer, [event.target.name]: event.target.value });
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>❌</button>
        {editedPlayer ? (
          <div>
            <div className="edit-form">
              <div>
                <label>Player name: </label>
                <input name="player_name" type="text" value={editedPlayer.player_name}
                  onChange={handleChange}></input>
              </div>
              <div>
                <label>Position: </label>
                <input name="position" type="text" value={editedPlayer.position}
                  onChange={handleChange}></input>
              </div>
            </div>
            <button className="save-button" onClick={() => onUpdatePlayer(editedPlayer)}>
              Save changes
            </button>
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
    onEdit(player);
  };

  // TODO: Hits Per Game was a live addition; perhaps do that math elsewhere or store in DB
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
          <li>{(player.hits / player.games).toFixed(3)} Hits Per Game</li>
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
  const [playerDescription, setPlayerDescription] = useState("Awaiting baseball player details...");
  const [loading, setLoading] = useState(false);

  const toggleDetailModal = () => {
    setIsDetailModalVisible(!isDetailModalVisible);
  };

  const toggleEditModal = () => {
    setIsEditModalVisible(!isEditModalVisible);
  };

  const openDetailModal = async (player) => {
    setPlayerFocus(player);
    toggleDetailModal();
    await getPlayerDescription(player);
  }

  const openEditModal = (player) => {
    setPlayerFocus(player);
    toggleEditModal();
  }

  const getPlayerDescription = async (player) => {
    setLoading(true);
    try {
      fetch("/players/description/" + player.id).then((res) => res.json()).then((data) => {
        console.log(data);
        setPlayerDescription(data.description);
      });
    } catch (error) {
      console.error("Error getting player description: ", error);
    } finally {
      setLoading(false);
    }
  };

  const updatePlayer = (editedPlayer) => {
    fetch("/players", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(editedPlayer),
    }).then((res) => res.json()).then((data) => {
        console.log(data);

        // Update the player in the list
        setPlayers((prevPlayers) =>
          prevPlayers.map((player) => player.id === editedPlayer.id ? editedPlayer : player));

        toggleEditModal();
        setPlayerFocus(null);
      })
      .catch((error) => {
        console.error("Error updating player: ", error);
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
        description={playerDescription} loading={loading} onClose={toggleDetailModal} />
      <EditModal id="edit-modal" show={isEditModalVisible} player={playerFocus}
        onUpdatePlayer={updatePlayer} onClose={toggleEditModal} />
    </div>
  );
}

export default App;
