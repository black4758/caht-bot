import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');

        try {
            const response = await fetch('http://localhost:8080/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '로그인 실패');
            }

            const data = await response.json();
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            setSuccessMessage('로그인 성공했습니다.');
            setTimeout(() => {
                navigate('/');
            }, 1500);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="container vh-100 d-flex justify-content-center align-items-center">
            <div className="card p-4" style={{ width: '100%', maxWidth: '400px' }}>
                <div className="card-body">
                    <h2 className="text-center mb-4">문서 챗봇 시스템</h2>
                    <h3 className="text-center mb-4">로그인</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="mb-3">
                            <label htmlFor="email">이메일:</label>
                            <input
                                type="email"
                                id="email"
                                className="form-control"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="password">비밀번호:</label>
                            <input
                                type="password"
                                id="password"
                                className="form-control"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn btn-primary w-100">로그인</button>
                    </form>
                    {error && <p className="mt-3 text-danger">{error}</p>}
                    {successMessage && <p className="mt-3 text-success">{successMessage}</p>}
                    <p className="mt-3 text-center">
                        계정이 없으신가요? <a href="/signup">회원가입</a>
                    </p>
                    <p className="text-center">
                        <a href="/forgot-password">비밀번호를 잊으셨나요?</a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;