import React, { useState, useEffect } from 'react';
import { Box, Typography, Alert, IconButton, CircularProgress, Button } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';

import DashboardLayout from '../components/DashboardLayout'; // Admin layout
import axiosInstance from '../api/axiosInstance';

const FacultyListPage = () => {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState({ msg: null, severity: null });
    const [rowModesModel, setRowModesModel] = React.useState({});

    // Data Fetching
    const fetchFaculty = () => {
        setLoading(true);
        axiosInstance.get('/api/v1/faculty') // Updated route
            .then(response => {
                setRows(response.data); // 'id' field Flask se aa raha hai
                setLoading(false);
            })
            .catch(error => {
                console.error("Failed to fetch faculty:", error);
                setStatus({ msg: 'Failed to load faculty.', severity: 'error' });
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchFaculty();
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
    };

    const handleSaveClick = (id) => () => {
        setRowModesModel({ ...rowModesModel, [id]: { mode: 'view' } });
    };

    // --- Row Update (Process) ---
    const processRowUpdate = async (updatedRow, originalRow) => {
        setLoading(true);
        try {
            const payload = {
                faculty_name: updatedRow.name, // Note: field name mismatch
                faculty_id_code: updatedRow.faculty_id_code,
                max_load: updatedRow.max_load,
                // Aap aur fields bhi update kar sakte hain
            };

            await axiosInstance.put(`/api/v1/faculty/${updatedRow.id}`, payload);
            
            // Local state update
            const updatedRows = rows.map(row => (row.id === updatedRow.id ? updatedRow : row));
            setRows(updatedRows);
            
            setStatus({ msg: 'Faculty updated successfully!', severity: 'success' });
            setLoading(false);
            return updatedRow;
            
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to update faculty.';
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
        if (window.confirm("Are you sure? This faculty member will be deleted permanently.")) {
            setLoading(true);
            try {
                await axiosInstance.delete(`/api/v1/faculty/${id}`);
                setRows(rows.filter(row => row.id !== id));
                setStatus({ msg: 'Faculty deleted!', severity: 'success' });
                setLoading(false);
            } catch (error) {
                const errorMsg = error.response?.data?.message || 'Failed to delete faculty.';
                setStatus({ msg: errorMsg, severity: 'error' });
                setLoading(false);
            }
        }
    };

    // --- Column Definitions ---
    const columns = [
        { field: 'faculty_id', headerName: 'ID', width: 70 },
        { field: 'name', headerName: 'Faculty Name', width: 220, editable: true },
        { field: 'faculty_id_code', headerName: 'ID Code', width: 130, editable: true },
        { field: 'dept_name', headerName: 'Department', width: 180, editable: false },
        { field: 'designation', headerName: 'Designation', width: 150, editable: true },
        { field: 'max_load', headerName: 'Max Load', type: 'number', width: 100, editable: true },
        { field: 'email', headerName: 'Email', width: 200, editable: true },
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

    const handleAddClick = () => {
        alert("TODO: Naya faculty add karne ke liye modal form kholo.");
        // (Yahaan aap AdminDashboard waala 'AddFacultyForm' component ek Modal mein dikha sakte hain)
    };

    return (
        <DashboardLayout>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                Manage Faculty (CRUD)
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
                                    Add New Faculty
                                </Button>
                                <GridToolbar />
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

export default FacultyListPage;