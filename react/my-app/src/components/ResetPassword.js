import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const ResetPassword = () => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    const [token, setToken] = useState(null);

    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const resetToken = queryParams.get('token');
        if (resetToken) {
            setToken(resetToken);
        } else {
            setError('비밀번호 재설정 토큰이 없습니다.');
        }
    }, [location]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        if (password !== confirmPassword) {
            setError('비밀번호가 일치하지 않습니다.');
            return;
        }

        if (!token) {
            setError('비밀번호 재설정 토큰이 유효하지 않습니다.');
            return;
        }

        try {
            const response = await fetch('http://localhost:8080/auth/password/change', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Reset-Token': token, // Pass the token in the header
                },
                body: JSON.stringify({ newPassword: password }), // Assuming backend expects newPassword
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '비밀번호 재설정 실패');
            }

            setMessage('비밀번호가 성공적으로 재설정되었습니다. 로그인 해주세요.');
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (err) {
            setError(err.message);
        }
    };

    if (!token && !error) {
        return <div>토큰을 확인 중입니다...</div>;
    }

    return (
        <div>
            <h2>비밀번호 재설정</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {!token && !error && <p style={{ color: 'red' }}>유효한 토큰이 필요합니다.</p>}
            {token && (
                <form onSubmit={handleSubmit}>
                    <div>
                        <label htmlFor="password">새 비밀번호:</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="confirmPassword">새 비밀번호 확인:</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit">비밀번호 재설정</button>
                </form>
            )}
            {message && <p style={{ color: 'green' }}>{message}</p>}
        </div>
    );
};

export default ResetPassword;
