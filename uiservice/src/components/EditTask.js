import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getTask, updateTask, getUsers } from '../utils/api';
import {
    Container, Typography, TextField, Button, MenuItem, Select, FormControl, InputLabel
} from '@material-ui/core';

const EditTask = () => {
    const { id } = useParams();
    const [task, setTask] = useState({
        creator_name: '',
        assigner_name: '',
        subject: '',
        criticality: '',
        status: ''
    });
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const fetchTask = async () => {
            try {
                const response = await getTask(id);
                setTask({
                    creator_name: response.data.creator_name,
                    assigner_name: response.data.assigner_name,
                    subject: response.data.subject,
                    criticality: response.data.criticality,
                    status: response.data.status
                });
            } catch (err) {
                console.error(err);
            }
        };

        const fetchUsers = async () => {
            try {
                const response = await getUsers();
                setUsers(response.data.map(user => user.username));
            } catch (err) {
                console.error(err);
            }
        };

        fetchTask();
        fetchUsers();
    }, [id]);

    const handleChange = (e) => {
        setTask({
            ...task,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await updateTask(id, task);
            // Redirect to issues list page
            window.location.href = '/tasks';
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <Container style={{ marginTop: '20px', paddingBottom: '25px', border: '1px solid #ccc', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', background: 'white' }}>
            <Typography variant="h4" style={{ marginTop: '1rem', fontWeight: 'bold' }}>Edit Issue</Typography>
            <form onSubmit={handleSubmit}>
                <FormControl fullWidth margin="normal">
                    <TextField
                        disabled
                        name="creator_name"
                        value={task.creator_name}
                        // onChange={handleChange}
                        InputProps={{
                            readOnly: true,
                        }}
                        style={{marginBottom: '0.3rem'}}
                        label="Creator Name"
                    />
                </FormControl>
                <FormControl fullWidth margin="normal">
                    <InputLabel>Assigner Name</InputLabel>
                    <Select
                        name="assigner_name"
                        value={task.assigner_name}
                        onChange={handleChange}
                        style={{marginBottom: '0.3rem'}}
                    >
                        {users.map((user) => (
                            <MenuItem key={user} value={user}>
                                {user}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                    <TextField
                        name="subject"
                        label="Subject"
                        value={task.subject}
                        onChange={handleChange}
                        inputProps={{ maxLength: 100 }}
                        style={{marginBottom: '0.3rem'}}
                    />
                </FormControl>
                <FormControl fullWidth margin="normal">
                    <InputLabel>Criticality</InputLabel>
                    <Select
                        name="criticality"
                        value={task.criticality}
                        onChange={handleChange}
                    >
                        {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level) => (
                            <MenuItem key={level} value={level}>
                                {level}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                    <InputLabel>Status</InputLabel>
                    <Select
                        name="status"
                        value={task.status}
                        onChange={handleChange}
                        style={{marginBottom: '1rem'}}
                    >
                        {['OPEN', 'FIXED', 'CLOSED'].map((status) => (
                            <MenuItem key={status} value={status}>
                                {status}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Button type="submit" variant="contained" color="primary" >
                    Save Changes
                </Button>
            </form>
        </Container>
    );
};

export default EditTask;
