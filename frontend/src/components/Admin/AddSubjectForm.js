// src/components/Admin/AddSubjectForm.js
import React, { useState } from "react";
import {
  Card, CardContent, CardHeader, TextField, MenuItem,
  FormControl, InputLabel, Select, Button, Stack, Alert, Box
} from "@mui/material";
import axiosInstance from "../../api/axiosInstance";

const DEPARTMENTS = [
  { id: "1", name: "Computer Science" },
  { id: "2", name: "Electronics & Comm." },
];

export default function AddSubjectForm() {
  const [form, setForm] = useState({
    subject_name: "",
    subject_code: "",
    department_id: "",
    lecture_count: "",
    type: "THEORY",               // NEW: default THEORY
    contiguous_block_size: 1,     // NEW: default 1; for LAB we'll switch to 2
  });
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const onTypeChange = (e) => {
    const value = e.target.value;
    setForm((f) => ({
      ...f,
      type: value,
      contiguous_block_size: value === "LAB" ? Math.max(2, Number(f.contiguous_block_size) || 2) : 1,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg({ type: "", text: "" });

    // basic validation
    if (!form.subject_name || !form.subject_code || !form.department_id || !form.lecture_count) {
      setMsg({ type: "error", text: "Please fill all required fields." });
      return;
    }

    // payload aligns with backend
    const payload = {
      subject_name: form.subject_name.trim(),
      subject_code: form.subject_code.trim(),
      department_id: form.department_id,
      lecture_count: Number(form.lecture_count),
      type: form.type, // THEORY or LAB
      contiguous_block_size: form.type === "LAB" ? Number(form.contiguous_block_size || 2) : 1,
    };

    try {
      setLoading(true);
      const { data } = await axiosInstance.post("/api/v1/add_subject", payload);
      setMsg({ type: "success", text: data?.message || "Subject added successfully." });
      // reset (keep department)
      setForm((f) => ({
        subject_name: "",
        subject_code: "",
        department_id: f.department_id,
        lecture_count: "",
        type: "THEORY",
        contiguous_block_size: 1,
      }));
    } catch (err) {
      const text =
        err?.response?.data?.msg ||
        err?.response?.data?.message ||
        "Failed to add subject.";
      setMsg({ type: "error", text });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card elevation={2}>
      <CardHeader title="Add New Subject" />
      <CardContent>
        <Stack component="form" spacing={2} onSubmit={handleSubmit}>
          {msg.text ? <Alert severity={msg.type}>{msg.text}</Alert> : null}

          <TextField
            label="Subject Name *"
            name="subject_name"
            value={form.subject_name}
            onChange={onChange}
            fullWidth
          />

          <TextField
            label="Subject Code (e.g., CS101) *"
            name="subject_code"
            value={form.subject_code}
            onChange={onChange}
            fullWidth
          />

          <FormControl fullWidth>
            <InputLabel>Department *</InputLabel>
            <Select
              label="Department *"
              name="department_id"
              value={form.department_id}
              onChange={onChange}
            >
              {DEPARTMENTS.map((d) => (
                <MenuItem key={d.id} value={d.id}>{d.name} ({d.id})</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Lecture Hours / Week *"
            name="lecture_count"
            value={form.lecture_count}
            onChange={(e) =>
              setForm((f) => ({ ...f, lecture_count: e.target.value.replace(/[^\d]/g, "") }))
            }
            fullWidth
            inputProps={{ inputMode: "numeric", pattern: "[0-9]*" }}
          />

          {/* NEW: Subject Type */}
          <FormControl fullWidth>
            <InputLabel>Subject Type *</InputLabel>
            <Select
              label="Subject Type *"
              name="type"
              value={form.type}
              onChange={onTypeChange}
            >
              <MenuItem value="THEORY">THEORY</MenuItem>
              <MenuItem value="LAB">LAB / PRACTICAL</MenuItem>
            </Select>
          </FormControl>

          {/* NEW: Block size only when LAB */}
          {form.type === "LAB" && (
            <TextField
              label="Contiguous Block Size (periods)"
              name="contiguous_block_size"
              value={form.contiguous_block_size}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  contiguous_block_size: e.target.value.replace(/[^\d]/g, ""),
                }))
              }
              helperText="Typical labs need 2 or 3 consecutive periods."
              fullWidth
              inputProps={{ inputMode: "numeric", pattern: "[0-9]*", min: 2 }}
            />
          )}

          <Box>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? "Submitting..." : "Submit Subject"}
            </Button>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}