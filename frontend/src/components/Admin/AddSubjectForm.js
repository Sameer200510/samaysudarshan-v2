import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert, CircularProgress, MenuItem } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import axiosInstance from '../../api/axiosInstance'; // Axios instance for API call

// Dummy Data for Departments (Replace with actual data fetch from API if needed)
const dummyDepartments = [
    { id: 1, name: 'Computer Science' },
    { id: 2, name: 'Electronics & Comm.' },
    { id: 3, name: 'Mechanical Engineering' },
];

const AddSubjectForm = () => {
    const [formData, setFormData] = useState({
        subject_name: '',
        subject_code: '',
        department_id: '',
        lecture_count: '', // Expected as a number
    });
    const [status, setStatus] = useState({ msg: null, severity: null, loading: false });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: null, severity: null, loading: true });

        // --- ENHANCED VALIDATION CHECK ---
        if (!formData.subject_name || !formData.subject_code || !formData.department_id || !formData.lecture_count) {
             setStatus({ msg: 'Subject Name, Code, Department, and Lecture Hours are required.', severity: 'error', loading: false });
             return;
        }

        try {
            // Route /api/v1/add_subject par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/add_subject', formData); 
            
            setStatus({ msg: response.data.message || 'Subject added successfully!', severity: 'success', loading: false });
            setFormData({ subject_name: '', subject_code: '', department_id: '', lecture_count: '' }); // Clear form

        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add subject. Check Flask console for DB errors.';
            setStatus({ msg: errorMsg, severity: 'error', loading: false });
        }
    };

    return (
        // Use Card for the elevated, contained form look
        <Card elevation={4} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent>
                <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: '600' }}>
                    <AddIcon sx={{ verticalAlign: 'middle', mr: 1 }} color="primary" /> 
                    Add New Subject
                </Typography>
                
                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>
                        {status.msg}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                    <TextField
                        name="subject_name"
                        label="Subject Name"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.subject_name}
                        onChange={handleChange}
                    />
                    <TextField
                        name="subject_code"
                        label="Subject Code (e.g., CS101)"
                        fullWidth
                        required 
                        variant="outlined"
                        margin="normal"
                        value={formData.subject_code}
                        onChange={handleChange}
                    />
                    
                    <TextField
                        select
                        name="department_id"
                        label="Department"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.department_id}
                        onChange={handleChange}
                    >
                        {dummyDepartments.map((option) => (
                            <MenuItem key={option.id} value={option.id}>
                                {option.name}
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        name="lecture_count"
                        label="Lecture Hours/Week"
                        fullWidth
                        type="number"
                        required 
                        variant="outlined"
                        margin="normal"
                        value={formData.lecture_count}
                        onChange={handleChange}
                        inputProps={{ min: 1 }}
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={status.loading}
                        startIcon={status.loading ? <CircularProgress size={20} color="inherit" /> : <AddIcon />}
                        sx={{ mt: 3, height: '48px' }}
                    >
                        {status.loading ? 'Adding Subject...' : 'Submit Subject'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AddSubjectForm;