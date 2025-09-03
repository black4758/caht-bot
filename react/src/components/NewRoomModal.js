
import React, { useState } from 'react';
import './NewRoomModal.css';

const NewRoomModal = ({ user, onRoomCreate, onClose }) => {
    const [title, setTitle] = useState('');
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');
    const [isCreating, setIsCreating] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === 'application/pdf') {
            setFile(selectedFile);
            setError('');
        } else {
            setFile(null);
            setError('Please select a PDF file.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title || !file || !user) {
            setError('Title and PDF file are required.');
            return;
        }

        setIsCreating(true);
        setError('');

        const formData = new FormData();
        formData.append('title', title);
        formData.append('file', file);
        formData.append('user_id', user.id);

        try {
            const response = await fetch('/api/v1/upsert-pdf/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to create room.');
            }

            const newRoomData = await response.json();
            // The API returns { message, base_id, chunk_count }
            // We need to create a room object that matches what the sidebar expects: { room_id, title }
            const newRoom = { room_id: parseInt(newRoomData.base_id), title: title };

            onRoomCreate(newRoom);
            onClose(); // Close the modal on success
        } catch (err) {
            setError(err.message);
        } finally {
            setIsCreating(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Create New Chat Room</h2>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="title">Room Title</label>
                        <input
                            type="text"
                            id="title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="file">PDF File</label>
                        <input
                            type="file"
                            id="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            required
                        />
                    </div>
                    {error && <p className="error-message">{error}</p>}
                    <div className="modal-actions">
                        <button type="button" onClick={onClose} disabled={isCreating}>Cancel</button>
                        <button type="submit" disabled={isCreating}>
                            {isCreating ? 'Creating...' : 'Create'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default NewRoomModal;
