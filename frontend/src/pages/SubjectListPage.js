import React, { useState, useEffect } from 'react';
import { Box, Typography, Alert, IconButton, CircularProgress, Button } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import { useDispatch } from 'react-redux';

import DashboardLayout from '../components/DashboardLayout'; // Admin layout
import axiosInstance from '../api/axiosInstance';
// import { logout } from '../features/auth/authSlice'; // Logout action (agar zaroorat ho)

// Yeh component "Subject Management" page hai (CRUD)
const SubjectListPage = () => {
    const dispatch = useDispatch();
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState({ msg: null, severity: null });
    const [rowModesModel, setRowModesModel] = React.useState({});

    // Data Fetching
    const fetchSubjects = () => {
        setLoading(true);
        axiosInstance.get('/api/v1/subjects') // Yeh route humne app.py mein banaya tha
            .then(response => {
                setRows(response.data); // 'id' field pehle se hi Flask se aa raha hai
                setLoading(false);
            })
            .catch(error => {
                console.error("Failed to fetch subjects:", error);
                setStatus({ msg: 'Failed to load subjects.', severity: 'error' });
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchSubjects();
    }, []);

    // --- Row Edit Handlers ---
    
    const handleEditClick = (id) => () => {
        setRowModesModel({ ...rowModesModel, [id]: { mode: 'edit' } });
    };

    const handleCancelClick = (id) => () => {
        setRowModesModel({
          ...rowModesModel,
          [id]: { mode: 'view', ignoreModifications: true },
        });
        // Row ko original state par revert karna (optional, agar fetch nahi kar rahe)
        // const originalRow = rows.find(row => row.id === id);
        // setRows(rows.map(row => (row.id === id ? originalRow : row)));
    };

    const handleSaveClick = (id) => () => {
        setRowModesModel({ ...rowModesModel, [id]: { mode: 'view' } });
    };

    // --- Row Update (Process) ---
    const processRowUpdate = async (updatedRow, originalRow) => {
        setLoading(true);
        try {
            const payload = {
                subject_name: updatedRow.subject_name,
                subject_code: updatedRow.subject_code,
                lecture_count: updatedRow.lecture_count,
            };

            await axiosInstance.put(`/api/v1/subject/${updatedRow.id}`, payload);
            
            // Local state update
            const updatedRows = rows.map(row => (row.id === updatedRow.id ? updatedRow : row));
            setRows(updatedRows);
            
            setStatus({ msg: 'Subject updated successfully!', severity: 'success' });
            setLoading(false);
            return updatedRow;
            
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to update subject.';
            setStatus({ msg: errorMsg, severity: 'error' });
            setLoading(false);
            return originalRow; // Error state, revert changes
        }
    };
    
    const onProcessRowUpdateError = (error) => {
        console.error("DataGrid Update Error:", error);
        setStatus({ msg: 'Failed to process update.', severity: 'error' });
    }

    // --- Delete Handler ---
    const handleDeleteClick = (id) => async () => {
        // Custom confirmation modal behtar hai
        if (window.confirm("Are you sure? This subject will be deleted permanently.")) {
            setLoading(true);
            try {
                await axiosInstance.delete(`/api/v1/subject/${id}`);
                setRows(rows.filter(row => row.id !== id));
                setStatus({ msg: 'Subject deleted!', severity: 'success' });
                setLoading(false);
            } catch (error) {
                const errorMsg = error.response?.data?.message || 'Failed to delete subject.';
                setStatus({ msg: errorMsg, severity: 'error' });
                setLoading(false);
            }
        }
    };

    // --- Column Definitions for DataGrid ---
    const columns = [
        // 'id' field DataGrid ko chahiye, but user ko 'subject_id' dikha sakte hain
        { field: 'subject_id', headerName: 'ID', width: 90 },
        { field: 'subject_name', headerName: 'Subject Name', width: 250, editable: true },
        { field: 'subject_code', headerName: 'Subject Code', width: 150, editable: true },
        { field: 'dept_name', headerName: 'Department', width: 200, editable: false }, // Join se aaya hai
        { field: 'lecture_count', headerName: 'Hours/Week', type: 'number', width: 130, editable: true },
        {
            field: 'actions',
            headerName: 'Actions',
            type: 'actions',
            width: 100,
            cellClassName: 'actions',
            getActions: ({ id }) => {
                const isInEditMode = rowModesModel[id]?.mode === 'edit';

                if (isInEditMode) {
                    return [
                        <IconButton title="Save" color="primary" onClick={handleSaveClick(id)}><SaveIcon /></IconButton>,
                        <IconButton title="Cancel" onClick={handleCancelClick(id)}><CancelIcon /></IconButton>,
                    ];
                }

                return [
                    <IconButton title="Edit" color="primary" onClick={handleEditClick(id)}><EditIcon /></IconButton>,
                    <IconButton title="Delete" color="error" onClick={handleDeleteClick(id)}><DeleteIcon /></IconButton>,
                ];
            },
        },
    ];

    const handleLogout = () => {
        // dispatch(logout());
        console.log("Logout clicked");
    };
    
    // Naya subject add karne ke liye (TODO: Modal form kholna chahiye)
    const handleAddClick = () => {
        alert("TODO: Naya subject add karne ke liye modal form kholo.");
        // (Yahaan aap AdminDashboard waala 'AddSubjectForm' component ek Modal mein dikha sakte hain)
    };

    return (
        <DashboardLayout onLogout={handleLogout}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                Manage Subjects (CRUD)
            </Typography>

            {status.msg && (
                <Alert 
                  severity={status.severity} 
                  sx={{ mb: 2 }} 
                  onClose={() => setStatus({ msg: null, severity: null })}
                >
                    {status.msg}
                </Alert>
            )}

            <Box sx={{ height: 650, width: '100%', backgroundColor: 'white' }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    loading={loading}
                    editMode="row"
                    rowModesModel={rowModesModel}
                    onRowModesModelChange={(newModel) => setRowModesModel(newModel)}
                    processRowUpdate={processRowUpdate}
                    onProcessRowUpdateError={onProcessRowUpdateError}
                    slots={{
                        toolbar: () => (
                            <Box sx={{ p: 1, borderBottom: '1px solid #eee' }}>
                                <Button startIcon={<AddIcon />} onClick={handleAddClick}>
                                    Add New Subject
                                </Button>
                                <GridToolbar /> {/* Filters, Export, etc. */}
                            </Box>
                        ),
                        loadingOverlay: CircularProgress,
                    }}
                    slotProps={{
                        toolbar: { setRows, setRowModesModel },
                    }}
                />
            </Box>
        </DashboardLayout>
    );
};

export default SubjectListPage;