import React from 'react';
import { Card, CardContent, Typography, Button, CircularProgress, Alert, Box } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import axiosInstance from '../../api/axiosInstance'; // Interceptor ke liye

const GenerateTimetableButton = () => {
    const [status, setStatus] = React.useState({ msg: '', loading: false, severity: 'info' });

    const handleGenerate = async () => {
        setStatus({ msg: 'Timetable Generation Started... (CPU Intensive)', loading: true, severity: 'info' });

        try {
            // Route /api/v1/generate_timetable par post karega (jo app.py mein hai)
            const response = await axiosInstance.post('/api/v1/generate_timetable', {});
            
            
            setStatus({ 
                msg: response.data.msg + ' Check View Tab now!', 
                loading: false, 
                severity: 'success' 
            });
        } catch (error) {
            const errorMsg = error.response?.data?.msg || 'Generation failed. Check DB data!';
            setStatus({ 
                msg: 'Error: ' + errorMsg, 
                loading: false, 
                severity: 'error' 
            });
        }
    };

    return (
        // Use Card for a clean, elevated section
        <Card elevation={6} sx={{ mt: 4, borderLeft: '5px solid #007BFF' }}> 
            <CardContent>
                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    🚀 Step 3: Smart Timetable Generation
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    This process runs the Genetic Algorithm (GA) to find the optimal schedule. It should only be run after all Section, Curriculum, Subject, Faculty, and Room data is entered.
                </Typography>

                {status.msg && (
                    <Alert severity={status.severity} sx={{ mb: 2 }}>
                        {status.msg}
                    </Alert>
                )}
                
                <Button
                    onClick={handleGenerate}
                    disabled={status.loading}
                    variant="contained"
                    color="primary"
                    startIcon={!status.loading && <PlayArrowIcon />}
                    sx={{ height: '48px' }}
                >
                    {status.loading ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            Running GA... <CircularProgress size={20} sx={{ color: 'white', ml: 1 }} />
                        </Box>
                    ) : (
                        'Generate Timetable Now'
                    )}
                </Button>
            </CardContent>
        </Card>
    );
};

export default GenerateTimetableButton;