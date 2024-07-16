import React, { useState } from 'react';
import { login } from '../utils/api';
import { Container, Typography, TextField, Button, Link, Box } from '@material-ui/core';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await login(new URLSearchParams({ username, password }));
            const { access_token, user } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(user));
            window.location.href = '/tasks';
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <Container style={{width: '30vw', border: '1px solid #ccc', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', marginTop: '25vh', paddingBottom: '2rem', background: 'white'}}>
            <Typography variant="h4" style={{ marginTop: '1rem', fontWeight: 'bold' }}>
                Login
            </Typography>
            <form onSubmit={handleSubmit} style={{ marginTop: '1rem' }}>
                <TextField
                    label="Email"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    type='email'
                    required
                    style={{ marginBottom: '1rem' }}
                />
                <TextField
                    label="Password"
                    variant="outlined"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{ marginBottom: '1rem' }}
                />
                <Button type="submit" variant="contained" color="primary" fullWidth style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                    Login
                </Button>
            </form>
            <Box mt={2}>
                <Link href="/signup" variant="body2">
                    Don't have an account? Sign Up
                </Link>
            </Box>
        </Container>
    );
};

export default Login;
