import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert, CircularProgress, MenuItem, Switch, FormControlLabel } from '@mui/material';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import axiosInstance from '../../api/axiosInstance'; 

const roomTypes = ['Lecture Hall', 'Computer Lab', 'Seminar Room', 'Specialized Lab'];

const AddRoomForm = () => {
    const [formData, setFormData] = useState({
        room_name: '',
        room_capacity: '',
        room_type: '',
        is_available: true, // Default to available
    });
    const [status, setStatus] = useState({ msg: null, severity: null, loading: false });

    const handleChange = (e) => {
        const { name, value, checked, type } = e.target;
        setFormData({ 
            ...formData, 
            [name]: type === 'checkbox' ? checked : value 
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: null, severity: null, loading: true });

        if (!formData.room_name || !formData.room_capacity || !formData.room_type) {
             setStatus({ msg: 'Room Name, Capacity, and Type are required.', severity: 'error', loading: false });
             return;
        }
        
        if (isNaN(Number(formData.room_capacity))) {
            setStatus({ msg: 'Capacity must be a valid number.', severity: 'error', loading: false });
            return;
        }

        try {
            // Route /api/v1/add_room par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/add_room', formData); 
            
            setStatus({ msg: response.data.message || 'Room added successfully!', severity: 'success', loading: false });
            setFormData({ room_name: '', room_capacity: '', room_type: '', is_available: true }); 

        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add room. Check Flask console for details.';
            setStatus({ msg: errorMsg, severity: 'error', loading: false });
        }
    };

    return (
        <Card elevation={4} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent>
                <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: '600' }}>
                    <MeetingRoomIcon sx={{ verticalAlign: 'middle', mr: 1 }} color="primary" /> 
                    Add New Room/Lab
                </Typography>
                
                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>
                        {status.msg}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                    <TextField
                        name="room_name"
                        label="Room Name (e.g., A-201, CS-Lab-1)"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.room_name}
                        onChange={handleChange}
                    />
                    <TextField
                        name="room_capacity"
                        label="Seating Capacity"
                        fullWidth
                        required
                        type="number"
                        variant="outlined"
                        margin="normal"
                        value={formData.room_capacity}
                        onChange={handleChange}
                        inputProps={{ min: 1 }}
                    />
                    
                    <TextField
                        select
                        name="room_type"
                        label="Room Type"
                        fullWidth
                        variant="outlined"
                        margin="normal"
                        value={formData.room_type}
                        onChange={handleChange}
                        required
                    >
                        {roomTypes.map((type) => (
                            <MenuItem key={type} value={type}>
                                {type}
                            </MenuItem>
                        ))}
                    </TextField>
                    
                    <FormControlLabel
                        control={
                            <Switch
                                checked={formData.is_available}
                                onChange={handleChange}
                                name="is_available"
                                color="primary"
                            />
                        }
                        label="Is Room Currently Available?"
                        sx={{ mt: 1, mb: 1 }}
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={status.loading}
                        startIcon={status.loading ? <CircularProgress size={20} color="inherit" /> : <MeetingRoomIcon />}
                        sx={{ mt: 3, height: '48px' }}
                    >
                        {status.loading ? 'Adding Room...' : 'Submit Room Data'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AddRoomForm;