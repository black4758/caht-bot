
import React from 'react';
import './Header.css';

const Header = ({ user, onLogout }) => {
    return (
        <header className="app-header">
            <div className="logo">
                My Chat App
            </div>
            <div className="user-info">
                {user && <span>Welcome, {user.name}</span>}
                <button onClick={onLogout}>Logout</button>
            </div>
        </header>
    );
};

export default Header;
