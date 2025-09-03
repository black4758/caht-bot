import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [verificationCode, setVerificationCode] = useState(''); // New state for verification code
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [showEmailForm, setShowEmailForm] = useState(true); // State to control form visibility
    const [showCodeForm, setShowCodeForm] = useState(false); // State to control form visibility
    const navigate = useNavigate(); // Initialize navigate

    const handleRequestCode = async (e) => { // Renamed handleSubmit to handleRequestCode
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            const response = await fetch('http://localhost:8080/auth/password/reset-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, name }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '비밀번호 재설정 요청 실패');
            }

            setMessage('인증 코드가 생성되었습니다. 코드를 입력해주세요.'); // Updated message
            setShowEmailForm(false); // Hide email form
            setShowCodeForm(true); // Show code form
        } catch (err) {
            setError(err.message);
        }
    };

    const handleVerifyCode = async (e) => { // New function for code verification
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            const response = await fetch('http://localhost:8080/auth/password/verify-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, code: verificationCode }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '인증 코드 확인 실패');
            }

            const data = await response.json();
            const resetToken = data.resetToken; // Assuming the backend returns { resetToken: "..." }

            setMessage('인증 코드가 확인되었습니다. 비밀번호를 재설정해주세요.');
            navigate(`/reset-password?token=${resetToken}`); // Navigate to reset password page
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="container vh-100 d-flex justify-content-center align-items-center">
            <div className="card p-4" style={{ width: '100%', maxWidth: '400px' }}>
                <div className="card-body">
                    <h2 className="text-center mb-4">비밀번호 찾기</h2>
                    {error && <p className="mt-3 text-danger">{error}</p>}
                    {message && <p className="mt-3 text-success">{message}</p>}

                    {showEmailForm && (
                        <form onSubmit={handleRequestCode}> {/* Use handleRequestCode */}
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
                                <label htmlFor="name">이름:</label>
                                <input
                                    type="text"
                                    id="name"
                                    className="form-control"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100">인증 코드 받기</button> {/* Updated button text */}
                        </form>
                    )}

                    {showCodeForm && (
                        <form onSubmit={handleVerifyCode}> {/* New form for code verification */}
                            <div className="mb-3">
                                <label htmlFor="verificationCode">인증 코드:</label>
                                <input
                                    type="text"
                                    id="verificationCode"
                                    className="form-control"
                                    value={verificationCode}
                                    onChange={(e) => setVerificationCode(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100">코드 확인</button>
                        </form>
                    )}

                    <p className="mt-3 text-center">
                        <a href="/login">로그인 페이지로 돌아가기</a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;