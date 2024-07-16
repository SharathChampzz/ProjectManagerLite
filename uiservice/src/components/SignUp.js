import React, { useState } from 'react';
import { signUp } from '../utils/api';
import { Container, Typography, TextField, Button, Link, Box } from '@material-ui/core';

const SignUp = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await signUp({ username, password });
            window.location.href = '/login';
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <Container style={{width: '30vw', border: '1px solid #ccc', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', marginTop: '25vh', paddingBottom: '2rem', background: 'white'}}>
            <Typography variant="h4" style={{ marginTop: '1rem', fontWeight: 'bold' }}>
                Sign Up
            </Typography>
            <form onSubmit={handleSubmit} style={{ marginTop: '1rem' }}>
                <TextField
                    label="Email"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    type="email"
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
                    Sign Up
                </Button>
            </form>
            <Box mt={2}>
                <Link href="/login" variant="body2">
                    Already have an account? Login
                </Link>
            </Box>
        </Container>
    );
};

export default SignUp;
