import React, { useState, useEffect } from 'react';
import { createTask, getUsers } from '../utils/api';
import { Container, Typography, TextField, Button, Select, MenuItem, FormControl, InputLabel } from '@material-ui/core';
import { useNavigate } from 'react-router-dom';

const CreateTask = () => {
    const [creatorName, setCreatorName] = useState('');
    const [assignerName, setAssignerName] = useState('');
    const [subject, setSubject] = useState('');
    const [criticality, setCriticality] = useState('');
    const [status, setStatus] = useState('');
    const [threadId, setThreadId] = useState('');
    const [htmlFile, setHtmlFile] = useState(null);
    const [users, setUsers] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await getUsers();
                setUsers(response.data.map(user => user.username));
            } catch (err) {
                console.error(err);
            }
        };
        fetchUsers();
        setCreatorName(JSON.parse(localStorage.getItem('user'))['username']);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('creator_name', creatorName);
        formData.append('assigner_name', assignerName);
        formData.append('subject', subject);
        formData.append('criticality', criticality);
        formData.append('status', status);
        formData.append('thread_id', threadId);
        formData.append('html_file', htmlFile);

        try {
            await createTask(formData);
            // Redirect to issues list page
            navigate('/tasks');
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <Container style={{ marginTop: '20px', paddingBottom: '25px', border: '1px solid #ccc', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', background: 'white' }}>
            <Typography variant="h4" style={{ marginTop: '1rem', fontWeight: 'bold' }}>
                Create Task
            </Typography>
            <form onSubmit={handleSubmit} style={{ marginTop: '1rem' }}>
                <FormControl variant="outlined" style={{ marginBottom: '1rem' }}>
                    <TextField disabled
                        name="creator_name"
                        value={creatorName}
                        // onChange={handleChange}
                        InputProps={{
                            readOnly: true,
                        }}
                        label="Creator Name"
                        style={{marginBottom: '0.3rem'}}
                    />
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <InputLabel>Assigner Name</InputLabel>
                    <Select
                        value={assignerName}
                        onChange={(e) => setAssignerName(e.target.value)}
                        label="Assigner Name"
                        required
                        style={{marginBottom: '0.3rem'}}
                    >
                        {users.map(user => (
                            <MenuItem key={user} value={user}>
                                {user}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <TextField
                        label="Subject"
                        value={subject}
                        onChange={(e) => setSubject(e.target.value)}
                        inputProps={{ maxLength: 100 }}
                        required
                        style={{marginBottom: '0.3rem'}}
                    />
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <InputLabel>Criticality</InputLabel>
                    <Select
                        value={criticality}
                        onChange={(e) => setCriticality(e.target.value)}
                        label="Criticality"
                        required
                        style={{marginBottom: '0.3rem'}}
                    >
                        {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map(level => (
                            <MenuItem key={level} value={level}>
                                {level}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <InputLabel>Status</InputLabel>
                    <Select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        label="Status"
                        required
                        style={{marginBottom: '0.3rem'}}
                    >
                        {['OPEN', 'FIXED', 'CLOSED'].map(statusOption => (
                            <MenuItem key={statusOption} value={statusOption}>
                                {statusOption}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <TextField
                        label="Thread ID"
                        value={threadId}
                        onChange={(e) => setThreadId(e.target.value)}
                        required
                        style={{marginBottom: '0.3rem'}}
                    />
                </FormControl>
                <FormControl variant="outlined" fullWidth style={{ marginBottom: '1rem' }}>
                    <input
                        type="file"
                        onChange={(e) => setHtmlFile(e.target.files[0])}
                        required
                        style={{marginBottom: '0.3rem'}}
                    />
                </FormControl>
                <Button type="submit" variant="contained" color="primary">
                    Create Task
                </Button>
            </form>
        </Container>
    );
};

export default CreateTask;
