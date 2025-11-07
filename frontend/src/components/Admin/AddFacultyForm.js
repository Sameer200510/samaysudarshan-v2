import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert, CircularProgress, MenuItem } from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import axiosInstance from '../../api/axiosInstance'; 

// --- DUMMY DATA: Aapko yeh 'dummyDepartments' ko API se fetch karna chahiye ---
const dummyDepartments = [
    { id: 1, name: 'Computer Science' },
    { id: 2, name: 'Electronics & Comm.' },
    { id: 3, name: 'Mechanical Engineering' },
    { id: 4, name: 'Physics (Visiting)' },
];

const facultyDesignations = [
    'Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer', 'Head of Department', 'Visiting Faculty'
];

const AddFacultyForm = () => {
    const [formData, setFormData] = useState({
        faculty_name: '',
        faculty_id_code: '', // Unique identifier
        designation: '',
        email: '',
        department_id: '', // Required for FK constraint
        max_load: '',      // Max hours/week constraint for GA
    });
    const [status, setStatus] = useState({ msg: null, severity: null, loading: false });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: null, severity: null, loading: true });

        if (!formData.faculty_name || !formData.faculty_id_code || !formData.department_id || !formData.max_load) {
             setStatus({ msg: 'All required fields (Name, ID, Dept, Max Load) must be filled.', severity: 'error', loading: false });
             return;
        }

        try {
            // Route /api/v1/add_faculty par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/add_faculty', formData); 
            
            setStatus({ msg: response.data.message || 'Faculty added successfully!', severity: 'success', loading: false });
            setFormData({ faculty_name: '', faculty_id_code: '', designation: '', email: '', department_id: '', max_load: '' }); 

        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add faculty member. Check Flask console for DB errors.';
            setStatus({ msg: errorMsg, severity: 'error', loading: false });
        }
    };

    return (
        <Card elevation={4} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent>
                <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: '600' }}>
                    <PersonAddIcon sx={{ verticalAlign: 'middle', mr: 1 }} color="primary" /> 
                    Add New Faculty
                </Typography>
                
                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>
                        {status.msg}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                    <TextField
                        name="faculty_name"
                        label="Faculty Member Name"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.faculty_name}
                        onChange={handleChange}
                    />
                    <TextField
                        name="faculty_id_code"
                        label="Faculty ID Code (Unique)"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.faculty_id_code}
                        onChange={handleChange}
                    />
                    
                    <TextField
                        select
                        name="department_id"
                        label="Home Department"
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
                        select
                        name="designation"
                        label="Designation/Role"
                        fullWidth
                        variant="outlined"
                        margin="normal"
                        value={formData.designation}
                        onChange={handleChange}
                        required
                    >
                        {facultyDesignations.map((role) => (
                            <MenuItem key={role} value={role}>
                                {role}
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        name="email"
                        label="Email Address (Optional)"
                        fullWidth
                        type="email"
                        variant="outlined"
                        margin="normal"
                        value={formData.email}
                        onChange={handleChange}
                    />
                    
                    <TextField
                        name="max_load"
                        label="Max Lecture Load/Week"
                        fullWidth
                        required
                        type="number"
                        variant="outlined"
                        margin="normal"
                        value={formData.max_load}
                        onChange={handleChange}
                        inputProps={{ min: 1, max: 25 }}
                    />


                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={status.loading}
                        startIcon={status.loading ? <CircularProgress size={20} color="inherit" /> : <PersonAddIcon />}
                        sx={{ mt: 3, height: '48px' }}
                    >
                        {status.loading ? 'Adding Faculty...' : 'Submit Faculty Data'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AddFacultyForm;