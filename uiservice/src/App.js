import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import SignUp from './components/SignUp';
import Login from './components/Login';
import IssuesList from './components/IssueList';
import TaskDetail from './components/TaskDetail';
import CreateTask from './components/CreateTask';
import EditTask from './components/EditTask';


const App = () => {
    return (
        <Router>
            <div>
                <Routes>
                    <Route path="/" element={<Navigate to="/login" />} />
                    <Route path="/signup" element={<SignUp />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/tasks" element={<IssuesList />} />
                    <Route path="/tasks/new" element={<CreateTask />} />
                    <Route path="/tasks/:id/edit" element={<EditTask />} />
                    <Route path="/tasks/:id" element={<TaskDetail />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
