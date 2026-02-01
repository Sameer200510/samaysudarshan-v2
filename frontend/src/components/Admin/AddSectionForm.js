import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert, CircularProgress, MenuItem } from '@mui/material';
import GroupAddIcon from '@mui/icons-material/GroupAdd';
import axiosInstance from '../../api/axiosInstance'; 

// --- DUMMY DATA: Aapko yeh 'dummyDepartments' ko API se fetch karna chahiye ---
const dummyDepartments = [
    { id: 1, name: 'Computer Science' },
    { id: 2, name: 'Electronics & Comm.' },
];
// -------------------------------------------------------------------------

const AddSectionForm = () => {
    const [formData, setFormData] = useState({
        section_name: '',
        dept_id: '',
        student_count: '',
    });
    const [status, setStatus] = useState({ msg: null, severity: null, loading: false });
    
    // Yahaan aap departments fetch kar sakte hain
    // useEffect(() => { ... fetch departments ... }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: null, severity: null, loading: true });

        if (!formData.section_name || !formData.dept_id || !formData.student_count) {
             setStatus({ msg: 'All fields are required.', severity: 'error', loading: false });
             return;
        }

        try {
            // Route /api/v1/add_section par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/add_section', formData); 
            setStatus({ msg: response.data.message || 'Section added successfully!', severity: 'success', loading: false });
            setFormData({ section_name: '', dept_id: '', student_count: '' }); 

        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to add section.';
            setStatus({ msg: errorMsg, severity: 'error', loading: false });
        }
    };

    return (
        <Card elevation={4} sx={{ height: '100%' }}>
            <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                    <GroupAddIcon sx={{ verticalAlign: 'middle', mr: 1 }} color="primary" /> 
                    Add New Section
                </Typography>
                
                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>{status.msg}</Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                    <TextField
                        name="section_name"
                        label="Section Name (e.g., CSE-A Sem 5)"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.section_name}
                        onChange={handleChange}
                    />
                    
                    <TextField
                        select
                        name="dept_id"
                        label="Department"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.dept_id}
                        onChange={handleChange}
                    >
                        {dummyDepartments.map((option) => (
                            <MenuItem key={option.id} value={option.id}>
                                {option.name}
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        name="student_count"
                        label="Student Count"
                        fullWidth
                        required
                        type="number"
                        variant="outlined"
                        margin="normal"
                        value={formData.student_count}
                        onChange={handleChange}
                        inputProps={{ min: 1 }}
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={status.loading}
                        startIcon={status.loading ? <CircularProgress size={20} color="inherit" /> : <GroupAddIcon />}
                        sx={{ mt: 3, height: '48px' }}
                    >
                        {status.loading ? 'Adding Section...' : 'Submit Section'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AddSectionForm;
