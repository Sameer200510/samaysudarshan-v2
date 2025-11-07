import React, { useState } from 'react';
import axiosInstance from '../../api/axiosInstance'; 
// Assuming tumhare paas batches ki list Redux se aati hai

function SetLunchTimeForm() {
    const [batchId, setBatchId] = useState('');
    const [startTime, setStartTime] = useState('12:05'); // Default values for easy entry
    const [endTime, setEndTime] = useState('13:00');
    const [status, setStatus] = useState({ msg: '', type: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: 'Updating lunch time...', type: 'info' });
        
        const payload = { batch_id: batchId, start_time: `${startTime}:00`, end_time: `${endTime}:00` };

        try {
            const response = await axiosInstance.post('/v1/admin/set_lunch_time', payload);
            setStatus({ msg: response.data.msg, type: 'success' });
        } catch (error) {
            const errorMsg = error.response?.data?.msg || 'Error setting lunch time.';
            setStatus({ msg: errorMsg, type: 'error' });
        }
    };

    return (
        <div style={{ padding: '20px', border: '1px solid #FF8C00', marginTop: '20px' }}>
            <h3>🍴 Set Lunch Time (Constraint)</h3>
            <form onSubmit={handleSubmit}>
                <label>Batch ID:</label>
                <input type="text" value={batchId} onChange={(e) => setBatchId(e.target.value)} required />
                
                <label>Start Time:</label>
                <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
                
                <label>End Time:</label>
                <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
                
                <button type="submit">Set Lunch Time</button>
            </form>
            {status.msg && <p style={{ color: status.type === 'error' ? 'red' : 'green' }}>{status.msg}</p>}
        </div>
    );
}

export default SetLunchTimeForm;