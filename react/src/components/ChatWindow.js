
import React, { useState, useEffect, useRef } from 'react';
import './ChatWindow.css';

const ChatWindow = ({ room }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(() => {
        if (room) {
            fetch(`/api/v1/rooms/${room.room_id}/messages`)
                .then(response => response.json())
                .then(data => setMessages(Array.isArray(data) ? data : []))
                .catch(error => {
                    console.error('Error fetching messages:', error);
                    setMessages([]); // Set to empty array on error
                });
        } else {
            setMessages([]);
        }
    }, [room]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (newMessage.trim() === '' || !room || isLoading) return;

        const userMessage = { 
            id: `user-${Date.now()}`,
            sender: 'user',
            content: newMessage.trim(),
            room_id: room.room_id
        };

        setMessages(prevMessages => [...prevMessages, userMessage]);
        setNewMessage('');
        setIsLoading(true);

        const formData = new FormData();
        formData.append('room_id', room.room_id);
        formData.append('question', userMessage.content);

        try {
            const response = await fetch('/api/v1/query-pdf/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            const systemMessage = {
                id: `system-${Date.now()}`,
                sender: 'system',
                content: data.answer,
                room_id: room.room_id
            };
            
            setMessages(prevMessages => [...prevMessages, systemMessage]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: `error-${Date.now()}`,
                sender: 'system',
                content: 'Sorry, something went wrong while getting a response.',
                room_id: room.room_id
            };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!room) {
        return <div className="chat-window"><div className="select-room-prompt">Select a room to start chatting</div></div>;
    }

    return (
        <div className="chat-window">
            <div className="messages-list">
                {messages.map((msg) => (
                    <div key={msg.id || msg.sequence_number} className={`message ${msg.sender === 'user' ? 'sent' : 'received'}`}>
                        <div className="message-sender">{msg.sender}</div>
                        <div className="message-content">{msg.content}</div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message received">
                        <div className="message-sender">system</div>
                        <div className="message-content typing-indicator">...</div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <form className="message-input-form" onSubmit={handleSendMessage}>
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? '...' : 'Send'}
                </button>
            </form>
        </div>
    );
};

export default ChatWindow;
