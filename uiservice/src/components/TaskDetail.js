import React, { useState, useEffect } from 'react';
import { getTask } from '../utils/api';
import { useParams } from 'react-router-dom';

const TaskDetail = () => {
    const { id } = useParams();
    const [task, setTask] = useState(null);

    useEffect(() => {
        const fetchTask = async () => {
            try {
                const response = await getTask(id);
                setTask(response.data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchTask();
    }, [id]);

    if (!task) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container">
            <h2>Task Details</h2>
            <div className="mb-3">
                <label className="form-label">Creator</label>
                <input type="text" className="form-control" value={task.creator_name} readOnly />
            </div>
            <div className="mb-3">
                <label className="form-label">Assigner</label>
                <input type="text" className="form-control" value={task.assigner_name} readOnly />
            </div>
            <div className="mb-3">
                <label className="form-label">Subject</label>
                <input type="text" className="form-control" value={task.subject} readOnly />
            </div>
            <div className="mb-3">
                <label className="form-label">Criticality</label>
                <input type="text" className="form-control" value={task.criticality} readOnly />
            </div>
            <div className="mb-3">
                <label className="form-label">Status</label>
                <input type="text" className="form-control" value={task.status} readOnly />
            </div>
        </div>
    );
};

export default TaskDetail;
