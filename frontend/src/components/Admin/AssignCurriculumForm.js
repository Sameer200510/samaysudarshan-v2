import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert, CircularProgress, MenuItem } from '@mui/material';
import LinkIcon from '@mui/icons-material/Link';
import axiosInstance from '../../api/axiosInstance'; 

// --- Yeh form 3 alag-alag APIs se data fetch karega ---

const AssignCurriculumForm = () => {
    // Data storage
    const [sections, setSections] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [faculty, setFaculty] = useState([]);
    
    // Form state
    const [formData, setFormData] = useState({
        section_id: '',
        subject_id: '',
        faculty_id: '',
    });
    const [status, setStatus] = useState({ msg: null, severity: null, loading: false });

    // --- Data Fetching ---
    useEffect(() => {
        // Sections fetch karna
        axiosInstance.get('/api/v1/sections')
            .then(res => setSections(res.data))
            .catch(err => console.error("Failed to fetch sections:", err));
            
        // Subjects fetch karna
        axiosInstance.get('/api/v1/subjects')
            .then(res => setSubjects(res.data))
            .catch(err => console.error("Failed to fetch subjects:", err));

        // Faculty fetch karna
        axiosInstance.get('/api/v1/faculty')
            .then(res => setFaculty(res.data))
            .catch(err => console.error("Failed to fetch faculty:", err));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus({ msg: null, severity: null, loading: true });

        if (!formData.section_id || !formData.subject_id || !formData.faculty_id) {
             setStatus({ msg: 'All fields are required.', severity: 'error', loading: false });
             return;
        }

        try {
            // Route /api/v1/assign_curriculum par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/assign_curriculum', formData); 
            setStatus({ msg: response.data.message || 'Curriculum assigned!', severity: 'success', loading: false });
            // Form clear nahi kar rahe taaki admin ek hi section mein multiple subjects assign kar sake
            setFormData({ ...formData, subject_id: '', faculty_id: '' }); 

        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to assign. (Already assigned?)';
            setStatus({ msg: errorMsg, severity: 'error', loading: false });
        }
    };

    return (
        <Card elevation={4} sx={{ height: '100%' }}>
            <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                    <LinkIcon sx={{ verticalAlign: 'middle', mr: 1 }} color="primary" /> 
                    Assign Curriculum
                </Typography>
                
                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>{status.msg}</Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                    
                    <TextField
                        select
                        name="section_id"
                        label="1. Select Section"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.section_id}
                        onChange={handleChange}
                    >
                        {sections.map((opt) => (
                            <MenuItem key={opt.section_id} value={opt.section_id}>
                                {opt.section_name}
                            </MenuItem>
                        ))}
                    </TextField>
                    
                    <TextField
                        select
                        name="subject_id"
                        label="2. Select Subject"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.subject_id}
                        onChange={handleChange}
                    >
                        {subjects.map((opt) => (
                            <MenuItem key={opt.subject_id} value={opt.subject_id}>
                                {opt.subject_name} ({opt.subject_code})
                            </MenuItem>
                        ))}
                    </TextField>

                    <TextField
                        select
                        name="faculty_id"
                        label="3. Assign Faculty (Can be from any Dept)"
                        fullWidth
                        required
                        variant="outlined"
                        margin="normal"
                        value={formData.faculty_id}
                        onChange={handleChange}
                    >
                        {faculty.map((opt) => (
                            <MenuItem key={opt.faculty_id} value={opt.faculty_id}>
                                {opt.name} ({opt.faculty_id_code})
                            </MenuItem>
                        ))}
                    </TextField>

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        disabled={status.loading}
                        startIcon={status.loading ? <CircularProgress size={20} color="inherit" /> : <LinkIcon />}
                        sx={{ mt: 3, height: '48px' }}
                    >
                        {status.loading ? 'Assigning...' : 'Assign Subject to Section'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default AssignCurriculumForm;