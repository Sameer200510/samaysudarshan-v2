// src/components/WeeklyTimetable.js
import React, { useEffect, useMemo, useState, useCallback, useRef } from "react";
import {
  Container, Typography, Paper, Alert, CircularProgress,
  Box, Button, Table, TableHead, TableRow, TableCell, TableBody, Divider,
  FormControl, InputLabel, Select, MenuItem
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import PrintIcon from "@mui/icons-material/Print";
import DownloadIcon from "@mui/icons-material/Download";
import MeetingRoomIcon from "@mui/icons-material/MeetingRoom";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import axiosInstance from "../api/axiosInstance";

const DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"];

// light tag colors by subject
const palettes = [
  { bg: "#eaf3ff", fg: "#0b63c8" },
  { bg: "#fff3e6", fg: "#b05f00" },
  { bg: "#eaf7ef", fg: "#176b3a" },
  { bg: "#f2eaff", fg: "#6a1bb1" },
  { bg: "#ffe9ee", fg: "#b10f32" },
  { bg: "#e9fbff", fg: "#0e6470" },
  { bg: "#f6f7ff", fg: "#2b2b6b" },
];
const colorFor = (key = "") => {
  let h = 0; for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) % 9973;
  return palettes[h % palettes.length];
};

export default function WeeklyTimetable() {
  const [sections, setSections] = useState([]);     // [{section_id, label, dept_id}]
  const [selectedId, setSelectedId] = useState(""); // dropdown value
  const [rows, setRows] = useState([]);             // timetable rows from API
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const printRef = useRef(null);

  const selected = sections.find(s => s.section_id === selectedId);

  // fetch sections
  useEffect(() => {
    let live = true;
    setLoading(true);
    axiosInstance.get("/api/v1/sections")
      .then(({ data }) => {
        const opts = (data || []).map(s => ({
          label: s.section_name,
          section_id: s.section_id,
          dept_id: s.dept_id || "CSE",
        }));
        if (live) {
          setSections(opts);
          if (opts.length) setSelectedId(opts[0].section_id);
        }
      })
      .catch(() => setError("Failed to fetch sections (login required?)"))
      .finally(() => setLoading(false));
    return () => (live = false);
  }, []);

  // fetch timetable for current section
  const fetchTimetable = useCallback(() => {
    if (!selected) return;
    setLoading(true);
    setError("");
    axiosInstance
      .get(`/api/timetable/${selected.dept_id}/${selected.section_id}`)
      .then(res => setRows(res.data || []))
      .catch(() => {
        setRows([]);
        setError("Failed to fetch timetable. Generate from admin panel first.");
      })
      .finally(() => setLoading(false));
  }, [selected]);

  useEffect(() => { fetchTimetable(); }, [fetchTimetable]);

  // unique time slots (sorted)
  const timeSlots = useMemo(() => {
    const m = new Map();
    (rows || []).forEach(r => {
      const key = `${r.start_time}-${r.end_time}`;
      if (!m.has(key)) m.set(key, { start: r.start_time, end: r.end_time });
    });
    return Array.from(m.values()).sort((a, b) => (a.start > b.start ? 1 : -1));
  }, [rows]);

  // day -> slot -> [{subject_code, faculty_name, room_name, room_type}]
  const mapByDayTime = useMemo(() => {
    const map = {};
    (rows || []).forEach(r => {
      const day = (r.day_of_week || "").toUpperCase();
      const key = `${r.start_time}-${r.end_time}`;
      const entry = {
        subject_code: r.subject_code,
        faculty_name: r.faculty_name,
        room_name: r.room_name,
        room_type: (r.room_type || "").toUpperCase(),
      };
      map[day] = map[day] || {};
      (map[day][key] ||= []).push(entry);
    });
    return map;
  }, [rows]);

  // export CSV (subject / faculty / room)
  const handleExport = () => {
    if (!selected) return;
    const header = ["Day", ...timeSlots.map(t => `${t.start}-${t.end}`)];
    const lines = [header.join(",")];
    DAYS.forEach(day => {
      const row = [day];
      timeSlots.forEach(t => {
        const key = `${t.start}-${t.end}`;
        const list = (mapByDayTime[day]?.[key] || []).map(e =>
          `${e.subject_code} / ${e.faculty_name} / ${e.room_name}`
        ).join(" | ");
        row.push(list.replaceAll(",", ";"));
      });
      lines.push(row.join(","));
    });
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `timetable_${selected.label}.csv`; a.click();
    URL.revokeObjectURL(url);
  };

  // print
  const handlePrint = () => {
    const w = window.open("", "_blank");
    if (!w) return;
    const html = `
      <html>
      <head>
        <title>Timetable – ${selected?.label || ""}</title>
        <style>
          body { font-family: Inter, Roboto, Arial; padding: 16px; }
          table { width: 100%; border-collapse: collapse; }
          th, td { border: 1px solid #e5e7eb; padding: 8px; font-size: 12px; }
          th { background: #f8fafc; }
          .day { font-weight: 700; background: #fff; position: sticky; left: 0; }
        </style>
      </head>
      <body>
        ${printRef.current?.innerHTML || ""}
      </body>
      </html>`;
    w.document.write(html);
    w.document.close();
    w.focus();
    w.print();
    w.close();
  };

  // professional cell: Subject (bold), faculty + room
  const Cell = ({ entries }) => {
    if (!entries || !entries.length) {
      return <Typography variant="caption" color="text.disabled">—</Typography>;
    }
    return (
      <Box sx={{ display: "grid", gap: 0.5 }}>
        {entries.map((e, i) => {
          const { bg, fg } = colorFor(e.subject_code);
          const isLab = e.room_type === "LAB";
          return (
            <Box
              key={i}
              sx={{
                bgcolor: bg, color: fg, borderRadius: 1.5, p: 1,
                border: isLab ? "1px dashed rgba(0,0,0,0.25)" : "1px solid transparent"
              }}
            >
              <Box sx={{ fontWeight: 800, fontSize: 13 }}>
                {isLab ? "🧪 " : "📘 "}{e.subject_code}
              </Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, mt: 0.25, color: "#475569" }}>
                <PersonOutlineIcon sx={{ fontSize: 14, opacity: 0.8 }} />
                <Typography variant="caption">{e.faculty_name || "-"}</Typography>
              </Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, color: "#475569" }}>
                <MeetingRoomIcon sx={{ fontSize: 14, opacity: 0.8 }} />
                <Typography variant="caption">{e.room_name || "-"}</Typography>
              </Box>
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header with single dropdown for Section */}
      <Paper
        elevation={0}
        sx={{
          p: 2, mb: 2, borderRadius: 3,
          background: "linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%)",
          color: "white", boxShadow: "0 6px 20px rgba(14,165,233,0.25)"
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: 0.3 }}>
              Weekly Timetable
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Section: {selected?.label || "—"} &nbsp;•&nbsp; Department: {selected?.dept_id || "—"}
            </Typography>
          </Box>

          <FormControl size="small" sx={{ minWidth: 260, bgcolor: "white", borderRadius: 2 }}>
            <InputLabel id="sec-label">Select Section</InputLabel>
            <Select
              labelId="sec-label"
              label="Select Section"
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              {sections.length
                ? sections.map(s => (
                    <MenuItem key={s.section_id} value={s.section_id}>{s.label}</MenuItem>
                  ))
                : <MenuItem disabled>Loading…</MenuItem>}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            startIcon={<RefreshIcon/>}
            onClick={fetchTimetable}
            disabled={!selected || loading}
            sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PrintIcon/>}
            onClick={handlePrint}
            disabled={!selected || loading}
            sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}
          >
            Print
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon/>}
            onClick={handleExport}
            disabled={!selected || loading}
            sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}
          >
            Export CSV
          </Button>
        </Box>
      </Paper>

      {loading && <CircularProgress sx={{ display: "block", m: "24px auto" }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Table */}
      {!loading && !error && (
        <Paper
          elevation={1}
          sx={{
            overflowX: "auto", borderRadius: 3,
            border: "1px solid #e5e7eb", boxShadow: "0 8px 24px rgba(0,0,0,0.06)"
          }}
          ref={printRef}
        >
          <Table stickyHeader size="small" aria-label="weekly timetable">
            <TableHead>
              <TableRow>
                <TableCell
                  sx={{
                    position: "sticky", left: 0, zIndex: 2, bgcolor: "#f8fafc",
                    fontWeight: 800, textTransform: "uppercase", letterSpacing: 0.4, color: "#334155"
                  }}
                >
                  Day
                </TableCell>
                {timeSlots.map(t => (
                  <TableCell
                    key={`${t.start}-${t.end}`}
                    align="center"
                    sx={{
                      bgcolor: "#f8fafc", fontWeight: 800, textTransform: "uppercase",
                      letterSpacing: 0.4, color: "#334155", whiteSpace: "nowrap"
                    }}
                  >
                    {t.start}–{t.end}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>

            <TableBody>
              {DAYS.map((day, idx) => (
                <TableRow
                  key={day}
                  sx={{
                    bgcolor: idx % 2 ? "rgba(0,0,0,0.02)" : "transparent",
                    "&:hover": { bgcolor: "rgba(14,165,233,0.06)" },
                    "& td": { py: 1.5, px: 1.25, verticalAlign: "top" }
                  }}
                >
                  <TableCell
                    sx={{
                      position: "sticky", left: 0, zIndex: 1, bgcolor: "white",
                      fontWeight: 700, whiteSpace: "nowrap", color: "#0f172a"
                    }}
                  >
                    {day.charAt(0) + day.slice(1).toLowerCase()}
                  </TableCell>

                  {timeSlots.map(t => {
                    const key = `${t.start}-${t.end}`;
                    const entries = mapByDayTime[day]?.[key];
                    return (
                      <TableCell key={key} align="center">
                        <Cell entries={entries} />
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {!loading && !error && (
        <Box sx={{ mt: 2, color: "text.secondary", display: "flex", alignItems: "center", gap: 1 }}>
          <Divider flexItem />
          <Typography variant="caption">
            Professional view • Subject, Faculty & Room visible
          </Typography>
          <Divider flexItem />
        </Box>
      )}
    </Container>
  );
}