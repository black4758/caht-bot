
import React from 'react';
import './Sidebar.css';

const Sidebar = ({ rooms, onRoomSelect, onNewChat, onRoomDelete }) => {

    const handleDeleteClick = (e, roomToDelete) => {
        e.stopPropagation(); // Prevent room selection when clicking delete

        if (window.confirm(`Are you sure you want to delete the room "${roomToDelete.title}"?`)) {
            fetch(`/api/v1/rooms/${roomToDelete.room_id}`, {
                method: 'DELETE',
            })
            .then(response => {
                if (response.ok) {
                    onRoomDelete(roomToDelete.room_id);
                } else {
                    alert('Failed to delete the room.');
                }
            })
            .catch(error => {
                console.error('Error deleting room:', error);
                alert('An error occurred while deleting the room.');
            });
        }
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>My Rooms</h2>
                <button onClick={onNewChat} className="new-chat-btn">+</button>
            </div>
            <ul>
                {rooms.map(room => (
                    <li key={room.room_id} onClick={() => onRoomSelect(room)} className="room-item">
                        <span className="room-title">{room.title}</span>
                        <button onClick={(e) => handleDeleteClick(e, room)} className="delete-room-btn">×</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Sidebar;
