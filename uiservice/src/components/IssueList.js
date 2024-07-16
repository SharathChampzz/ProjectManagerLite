import React, { useState, useEffect } from 'react';
import { getTasks, getUsers, deleteTask, getTaskHtml } from '../utils/api';
import { Link } from 'react-router-dom';
import {
    Container, Typography, TextField, IconButton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Select, MenuItem, FormControl, InputLabel, Button,
    Dialog, DialogTitle, DialogContent, DialogActions
} from '@material-ui/core';
import { Pagination } from '@material-ui/lab';
import SearchIcon from '@material-ui/icons/Search';
import VisibilityIcon from '@material-ui/icons/Visibility';
import EditIcon from '@material-ui/icons/Edit';
import RefreshIcon from '@material-ui/icons/Refresh';
import DeleteIcon from '@material-ui/icons/Delete';
import AddIcon from '@material-ui/icons/Add';

const IssuesList = () => {
    const defaultFilters = {
        skip: 0,
        limit: 10,
        creator_name: 'All',
        assigner_name: 'All',
        subject_contains: '',
        criticality: 'All',
        status: 'All',
        thread_id: '',
    };

    const [tasks, setTasks] = useState([]);
    const [users, setUsers] = useState([]);
    const [filters, setFilters] = useState(defaultFilters);
    const is_superuser = JSON.parse(localStorage.getItem('user'))?.is_superuser || false;
    const [htmlContent, setHtmlContent] = useState('');
    const [open, setOpen] = useState(false);

    const fetchTasks = async () => {
        try {
            const response = await getTasks({
                ...filters,
                creator_name: filters.creator_name === 'All' ? '' : filters.creator_name,
                assigner_name: filters.assigner_name === 'All' ? '' : filters.assigner_name,
                criticality: filters.criticality === 'All' ? '' : filters.criticality,
                status: filters.status === 'All' ? '' : filters.status,
            });
            setTasks(response.data);
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

    useEffect(() => {
        fetchTasks();
        fetchUsers();
    }, [filters]);

    const handleChange = (e) => {
        setFilters({
            ...filters,
            [e.target.name]: e.target.value,
        });
    };

    const handleDeleteTask = async (id) => {
        try {
            const confirmed = window.confirm("Are you sure you want to delete this task?");
            if (confirmed) {
                await deleteTask(id);
                await fetchTasks();
            }
        } catch (err) {
            console.error(err);
        }
    }

    const resetFilters = () => {
        setFilters(defaultFilters);
    };

    const handlePageChange = (event, value) => {
        setFilters({
            ...filters,
            skip: (value - 1) * filters.limit,
        });
    };

    const getRowStyle = (task) => {
        if (task.status === 'CLOSED') {
            return { backgroundColor: 'rgba(232,245,233,255)' };
        }
        if (task.criticality === 'CRITICAL' && task.status === 'OPEN') {
            return { backgroundColor: 'rgba(254,235,236,255)' };
        }
        return { backgroundColor: 'rgba(255,245,235,255)'};
    };

    const handleViewClick = async (html_file_loc) => {
        try {
            const response = await getTaskHtml(html_file_loc);
            setHtmlContent(response.data);
            setOpen(true);
        } catch (err) {
            console.error(err);
        }
    };

    const handleClose = () => {
        setOpen(false);
        setHtmlContent('');
    };

    return (
        <Container style={{ marginTop: '20px', paddingBottom: '25px', border: '1px solid #ccc', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', background: 'white' }}>
            <Typography variant="h4" style={{ marginTop: '1rem', fontWeight: 'bold' }}>
                Issues List
            </Typography>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', marginTop: '1rem'}}>
                <FormControl style={{ width: '175px' }}>
                    <InputLabel>Creator Name</InputLabel>
                    <Select
                        name="creator_name"
                        value={filters.creator_name}
                        onChange={handleChange}
                        // label="Creator Name"
                    >
                        <MenuItem value="All">All</MenuItem>
                        {users.map((user) => (
                            <MenuItem key={user} value={user}>
                                {user.split('@')[0]}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl style={{ width: '175px' }}>
                    <InputLabel>Assigner Name</InputLabel>
                    <Select
                        name="assigner_name"
                        value={filters.assigner_name}
                        onChange={handleChange}
                        // label="Assigner Name"
                    >
                        <MenuItem value="All">All</MenuItem>
                        {users.map((user) => (
                            <MenuItem key={user} value={user}>
                                {user.split('@')[0]}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl style={{ width: '150px' }}>
                    <InputLabel>Criticality</InputLabel>
                    <Select
                        name="criticality"
                        value={filters.criticality}
                        onChange={handleChange}
                        // label="Criticality"
                    >
                        {['All', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level) => (
                            <MenuItem key={level} value={level}>
                                {level}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl style={{ width: '150px' }}>
                    <InputLabel>Status</InputLabel>
                    <Select
                        name="status"
                        value={filters.status}
                        onChange={handleChange}
                        // label="Status"
                    >
                        {['All', 'OPEN', 'FIXED', 'CLOSED'].map((status) => (
                            <MenuItem key={status} value={status}>
                                {status || 'All'}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl style={{ flex: 2 }}>
                    <TextField
                        name="subject_contains"
                        value={filters.subject_contains}
                        onChange={handleChange}
                        label="Subject"
                        InputProps={{
                            endAdornment: (
                                <IconButton>
                                    <SearchIcon />
                                </IconButton>
                            ),
                        }}
                    />
                </FormControl>
                <IconButton onClick={resetFilters} color="secondary">
                    <RefreshIcon />
                </IconButton>
                {is_superuser && (
                <IconButton component={Link} to={`/tasks/new`}>
                    <AddIcon />
                </IconButton>
                )}
            </div>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Creator</TableCell>
                            <TableCell>Assigner</TableCell>
                            <TableCell>Subject</TableCell>
                            <TableCell>Criticality</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tasks.map(task => (
                            <TableRow key={task.id} style={getRowStyle(task)}>
                                <TableCell>{task.creator_name.split('@')[0]}</TableCell>
                                <TableCell>{task.assigner_name.split('@')[0]}</TableCell>
                                <TableCell width={'300px'} >{task.subject}</TableCell>
                                <TableCell color='red'>{task.criticality}</TableCell>
                                <TableCell>{task.status}</TableCell>
                                <TableCell>
                                <IconButton onClick={() => handleViewClick(task.html_file)}>
                                        <VisibilityIcon />
                                    </IconButton>
                                    <IconButton component={Link} to={`/tasks/${task.id}/edit`}>
                                        <EditIcon />
                                    </IconButton>
                                    {is_superuser && (
                                        <IconButton onClick={() => handleDeleteTask(task.id)}>
                                            <DeleteIcon />
                                        </IconButton>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <Pagination
                count={Math.ceil(tasks.total / filters.limit)}
                page={Math.floor(filters.skip / filters.limit) + 1}
                onChange={handlePageChange}
                color="primary"
                style={{ marginTop: '1rem' }}
            />
            <Dialog open={open} onClose={handleClose} fullWidth maxWidth="md">
                <DialogTitle>Task HTML Content</DialogTitle>
                <DialogContent dividers>
                    <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default IssuesList;
