
import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import Header from '../components/Header';
import NewRoomModal from '../components/NewRoomModal'; // Import the modal
import './ChatPage.css';

const ChatPage = () => {
    const [rooms, setRooms] = useState([]);
    const [selectedRoom, setSelectedRoom] = useState(null);
    const [user, setUser] = useState(null); 
    const [isModalOpen, setIsModalOpen] = useState(false); // State for modal

    useEffect(() => {
        const currentUser = { id: 1, name: 'User' }; // Placeholder user
        setUser(currentUser);

        if (currentUser) {
            fetch(`/api/v1/users/${currentUser.id}/rooms`)
                .then(response => response.json())
                .then(data => setRooms(data))
                .catch(error => console.error('Error fetching rooms:', error));
        }
    }, []);

    const handleRoomSelect = (room) => {
        setSelectedRoom(room);
    };

    const handleLogout = () => {
        fetch('/logout', { method: 'POST' })
            .then(() => {
                console.log('Logged out');
                window.location.href = '/login';
            })
            .catch(error => console.error('Error logging out:', error));
    };

    const handleRoomCreate = (newRoom) => {
        setRooms([...rooms, newRoom]);
    };

    const handleRoomDelete = (roomIdToDelete) => {
        setRooms(prevRooms => prevRooms.filter(room => room.room_id !== roomIdToDelete));
        if (selectedRoom && selectedRoom.room_id === roomIdToDelete) {
            setSelectedRoom(null);
        }
    };

    return (
        <div className="chat-page">
            <Header user={user} onLogout={handleLogout} />
            <div className="main-content">
                <Sidebar 
                    rooms={rooms} 
                    onRoomSelect={handleRoomSelect} 
                    onNewChat={() => setIsModalOpen(true)} // Open modal
                    onRoomDelete={handleRoomDelete} // Pass delete handler
                />
                <ChatWindow room={selectedRoom} />
            </div>
            {isModalOpen && (
                <NewRoomModal 
                    user={user}
                    onRoomCreate={handleRoomCreate}
                    onClose={() => setIsModalOpen(false)} // Close modal
                />
            )}
        </div>
    );
};

export default ChatPage;
