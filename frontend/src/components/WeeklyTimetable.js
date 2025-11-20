import React, { useEffect, useState, useMemo, useCallback, useRef } from "react";
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

const DAYS = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"];

// tag colors
const palettes = [
  { bg: "#f3ecff", fg: "#6b21a8" },
  { bg: "#eaf3ff", fg: "#0b63c8" },
  { bg: "#fff3e6", fg: "#b05f00" },
  { bg: "#eaf7ef", fg: "#176b3a" },
  { bg: "#ffe9ee", fg: "#b10f32" },
  { bg: "#e9fbff", fg: "#0e6470" },
  { bg: "#f6f7ff", fg: "#2b2b6b" },
];
const colorFor = (key = "") => {
  let h = 0; for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) % 9973;
  return palettes[h % palettes.length];
};

// utils
const toHHMM = (t) => {
  const s = String(t ?? "");
  return s.length >= 5 ? s.slice(0,5) : s;
};
const pick = (obj, keys, def = undefined) => {
  for (const k of keys) {
    if (obj && Object.prototype.hasOwnProperty.call(obj, k) && obj[k] != null) return obj[k];
    if (obj && obj[k] === 0) return 0;
  }
  return def;
};

// detect LAB (robust – room_type, room_name, subject_code/name)
const looksLikeLab = (entry) => {
  const rt = String(entry.room_type || "").toLowerCase();
  const rn = String(entry.room_name || "").toLowerCase();
  const sc = String(entry.subject_code || "").toLowerCase();
  const sn = String(entry.subject_name || "").toLowerCase();
  return (
    /lab|laborat/.test(rt) ||
    /lab/.test(rn) ||
    /\blab\b|\bpract/.test(sn) ||
    /l\d*$/.test(sc) || 
    /lab/.test(sc)
  );
};

// supports number, numeric-string and names
const useDayKey = () => useCallback((d) => {
  if (d == null) return "";
  if (typeof d === "number") {
    if (d >= 1 && d <= 7) return DAYS[d - 1] || "";
    if (d >= 0 && d < 7)  return DAYS[d] || "";
    return "";
  }
  const s = String(d).trim();
  if (/^-?\d+$/.test(s)) {
    const n = parseInt(s, 10);
    if (n >= 1 && n <= 7) return DAYS[n - 1] || "";
    if (n >= 0 && n < 7)  return DAYS[n] || "";
    return "";
  }
  const up = s.toUpperCase();
  const short = { MON: "MONDAY", TUE: "TUESDAY", WED: "WEDNESDAY", THU: "THURSDAY", FRI: "FRIDAY", SAT: "SATURDAY" };
  return short[up.slice(0,3)] || up;
}, []);

export default function WeeklyTimetable() {
  const [sections, setSections] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const printRef = useRef(null);

  // MOCK LUNCH TIMES: Hardcode to ensure the display works consistently
  const lunchTimes = useMemo(() => ({ start: '12:05:00', end: '13:00:00' }), []);
  const lunchSlotString = useMemo(() => {
      // 12:05:00 -> 12:05
      return `${toHHMM(lunchTimes.start)}-${toHHMM(lunchTimes.end)}`;
  }, [lunchTimes]);

  const dayKey = useDayKey();

  // fetch sections
  useEffect(() => {
    let live = true;
    setLoading(true); setError("");
    axiosInstance.get("/api/v1/sections")
      .then(({ data }) => {
        const opts = (data || []).map(s => ({
          label: pick(s, ["section_name", "batch_id"], null), // Updated to handle common batch fields
          section_id: String(pick(s, ["section_id", "batch_id"], null)),
          dept_id: String(pick(s, ["dept_id", "department_id"], "1")),
        }));
        if (!live) return;
        setSections(opts);
        if (opts.length && !selectedId) setSelectedId(opts[0].section_id);
      })
      .catch(() => { if (live) setError("Failed to fetch sections (login required?)"); })
      .finally(() => { if (live) setLoading(false); });
    return () => { live = false; };
  }, [selectedId]); // Added selectedId to dependency to avoid resetting selection

  const selected = useMemo(
    () => sections.find(s => String(s.section_id) === String(selectedId)),
    [sections, selectedId]
  );

  // fetch timetable
  const fetchTimetable = useCallback(() => {
    if (!selected) return;
    setLoading(true); setError("");
    const dept = String(selected.dept_id ?? "1");
    const sec  = String(selected.section_id);
    axiosInstance.get(`/api/timetable/${dept}/${sec}`)
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : (res.data?.rows || res.data?.data || res.data?.result || []);
        console.log("[Timetable] fetched", { count: data.length, sample: data[0] });
        setRows(data || []);
      })
      .catch(() => { setRows([]); setError("Failed to fetch timetable. Generate from admin panel first."); })
      .finally(() => setLoading(false));
  }, [selected]);

  useEffect(() => { fetchTimetable(); }, [fetchTimetable]);

  // headers (unique slots)
  const timeSlots = useMemo(() => {
    const m = new Map();
    (rows || []).forEach(r => {
      const start = toHHMM(pick(r, ["start_time","startTime","start"], ""));
      const end   = toHHMM(pick(r, ["end_time","endTime","end"], ""));
      if (!start || !end) return;
      const key = `${start}-${end}`;
      if (!m.has(key)) m.set(key, { start, end });
    });
    
    // Add LUNCH SLOT to the list if the current timetable slots do not contain it
    const allSlots = Array.from(m.values()).sort((a,b) => (a.start > b.start ? 1 : -1));
    const lunchSlotObj = { start: toHHMM(lunchTimes.start), end: toHHMM(lunchTimes.end) };
    const lunchKey = `${lunchSlotObj.start}-${lunchSlotObj.end}`;

    if (!m.has(lunchKey)) {
        // If the GA didn't generate an entry for lunch, we must manually insert the slot for the header.
        allSlots.push(lunchSlotObj);
        allSlots.sort((a,b) => (a.start > b.start ? 1 : -1)); // Sort again after insertion
    }

    return allSlots;
  }, [rows, lunchTimes]);

  // grid + LAB mirror
  const mapByDayTime = useMemo(() => {
    const map = {};

    // base map
    (rows || []).forEach(r => {
      const d = dayKey(pick(r, ["day_of_week","dayOfWeek","day","dayName"], null));
      if (!d) return;
      const start = toHHMM(pick(r, ["start_time","startTime","start"], ""));
      const end   = toHHMM(pick(r, ["end_time","endTime","end"], ""));
      if (!start || !end) return;

      const key = `${start}-${end}`;
      const entry = {
        subject_code: pick(r, ["subject_code","subjectCode","subject","code"], "-"),
        subject_name: pick(r, ["subject_name","subjectName","subjectTitle","name"], ""),
        faculty_name: pick(r, ["faculty_name","facultyName","teacher","instructor"], "-"),
        room_name:      pick(r, ["room_name","roomName","room"], "-"),
        room_type:      String(pick(r, ["room_type","roomType","type"], "")).toUpperCase(),
      };

      map[d] = map[d] || {};
      (map[d][key] ||= []).push(entry);
    });

    // mirror LAB into next empty slot (2-slot labs) - Logic remains the same
    DAYS.forEach(day => {
      if (!map[day]) return;
      for (let i = 0; i < timeSlots.length - 1; i++) {
        const key    = `${timeSlots[i].start}-${timeSlots[i].end}`;
        const nextKey = `${timeSlots[i + 1].start}-${timeSlots[i + 1].end}`;

        const entries = map[day][key];
        if (!entries || entries.length === 0) continue;

        const labEntries = entries.filter(looksLikeLab);
        // copy only if next cell is truly empty/undefined
        if (labEntries.length && (!map[day][nextKey] || map[day][nextKey].length === 0)) {
          map[day][nextKey] = labEntries.map(e => ({ ...e })); // shallow clone
        }
      }
    });

    return map;
  }, [rows, dayKey, timeSlots]);

  // export CSV
  const handleExport = () => {
    // ... (CSV export logic remains the same) ...
    if (!selected) return;
    const header = ["Day", ...timeSlots.map(t => `${t.start}-${t.end}`)];
    const lines = [header.join(",")];
    DAYS.forEach(day => {
      const row = [day];
      timeSlots.forEach(t => {
        const key = `${t.start}-${t.end}`;
        const list = (mapByDayTime[day]?.[key] || []).map(e =>
          `${e.subject_code || "-"} / ${e.faculty_name || "-"} / ${e.room_name || "-"}`
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

  // ---------- UPDATED PRINT FUNCTION (robust) ----------
  const handlePrint = () => {
    if (!printRef.current) {
      console.warn("Print ref not found");
      return;
    }

    // Try to open new window
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      // Popup was blocked -> fallback to printing whole page
      alert("Popup blocked — falling back to printing the current page. Allow popups for best experience.");
      window.print();
      return;
    }

    // Clone the node to avoid mutating React DOM
    const clone = printRef.current.cloneNode(true);

    // Create minimal document shell
    const doc = printWindow.document;
    doc.open();
    doc.write(`<!doctype html><html><head><meta charset="utf-8"><title>Timetable Print – ${selected?.label || ""}</title></head><body></body></html>`);
    doc.close();

    // Copy external stylesheet links
    try {
      const head = doc.head;
      Array.from(document.querySelectorAll("link[rel='stylesheet']")).forEach(link => {
        try {
          const newLink = doc.createElement("link");
          newLink.rel = "stylesheet";
          newLink.href = link.href;
          head.appendChild(newLink);
        } catch (e) { /* ignore single link failures */ }
      });

      // Copy inline style tags (MUI/emotion injects styles here)
      Array.from(document.querySelectorAll("style")).forEach(s => {
        try {
          const newStyle = doc.createElement("style");
          newStyle.innerHTML = s.innerHTML;
          head.appendChild(newStyle);
        } catch (e) { /* ignore */ }
      });
    } catch (e) {
      console.warn("Failed to copy styles to print window", e);
    }

    // Optional adjustments for printing (ensure backgrounds print, hide controls)
    const adjustStyle = doc.createElement("style");
    adjustStyle.innerHTML = `
      @media print {
        body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .no-print, button, .MuiButton-root { display: none !important; }
      }
      table { width: 100%; border-collapse: collapse; }
      th, td { border: 1px solid #e5e7eb; padding: 6px; font-size: 12px; }
      th { background: #f8fafc; }
    `;
    doc.head.appendChild(adjustStyle);

    // Insert cloned content
    doc.body.style.margin = "10px";
    doc.body.appendChild(clone);

    // Wait a short while for CSS to load, then trigger print
    setTimeout(() => {
      try {
        printWindow.focus();
        printWindow.print();
        // close the print window after small delay (some browsers may block immediate close)
        setTimeout(() => {
          try { printWindow.close(); } catch (e) { /* ignore */ }
        }, 300);
      } catch (err) {
        console.error("Print failed", err);
        window.print(); // fallback
      }
    }, 600); // increase if your stylesheets/fonts are slow to load
  };

  // cell
  const Cell = ({ entries, slotKey }) => {
    // 1. DYNAMIC LUNCH BREAK OVERRIDE (The Fix)
    if (slotKey === lunchSlotString) {
        return (
            <Box sx={{ 
                bgcolor: '#fffae0', color: '#b05f00', p: 1, borderRadius: 1.5, fontWeight: 800,
                border: '1px solid #f9a825', minHeight: 48, display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
                <Typography variant="body2" sx={{ fontWeight: 800 }}>
                    🍴 LUNCH BREAK
                </Typography>
            </Box>
        );
    }
    
    // 2. Class Content
    if (!entries || !entries.length) {
      return <Typography variant="caption" color="text.disabled">—</Typography>;
    }
    return (
      <Box sx={{ display: "grid", gap: 0.5 }}>
        {entries.map((e, i) => {
          const { bg, fg } = colorFor(e.subject_code || "");
          const isLab = looksLikeLab(e);
          return (
            <Box
              key={i}
              sx={{
                bgcolor: bg, color: fg, borderRadius: 1.5, p: 1,
                border: isLab ? "1px dashed rgba(0,0,0,0.25)" : "1px solid transparent"
              }}
            >
              <Box sx={{ fontWeight: 800, fontSize: 13 }}>
                {isLab ? "🧪 " : "📘 "}{e.subject_code || "-"}
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
      {/* header */}
      <Paper
        elevation={0}
        sx={{
          p: 2, mb: 2, borderRadius: 3,
          background: "linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%)",
          color: "white", boxShadow: "0 6px 20px rgba(14,165,233,0.25)"
        }}
      >
        {/* added no-print class so header controls will be hidden in printed output */}
        <Box className="no-print" sx={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
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
              onChange={(e) => setSelectedId(String(e.target.value))}
            >
              {sections.length
                ? sections.map(s => <MenuItem key={s.section_id} value={s.section_id}>{s.label}</MenuItem>)
                : <MenuItem disabled>Loading…</MenuItem>}
            </Select>
          </FormControl>

          <Button variant="contained" startIcon={<RefreshIcon/>} onClick={fetchTimetable}
                      disabled={!selected || loading}
                      sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<PrintIcon/>} onClick={handlePrint}
                      disabled={!selected || loading}
                      sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}>
            Print
          </Button>
          <Button variant="contained" startIcon={<DownloadIcon/>} onClick={handleExport}
                      disabled={!selected || loading}
                      sx={{ bgcolor: "rgba(255,255,255,0.15)", "&:hover": { bgcolor: "rgba(255,255,255,0.25)" } }}>
            Export CSV
          </Button>
        </Box>
      </Paper>

      {loading && <CircularProgress sx={{ display: "block", m: "24px auto" }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* table */}
      {!loading && !error && rows && rows.length > 0 && (
        <Paper
          elevation={1}
          sx={{ overflowX: "auto", borderRadius: 3, border: "1px solid #e5e7eb", boxShadow: "0 8px 24px rgba(0,0,0,0.06)" }}
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
                    
                    const isLunchSlot = key === lunchSlotString; // Check lunch slot string

                    return (
                      <TableCell key={key} align="center">
                        {isLunchSlot ? (
                            <Box sx={{ 
                                bgcolor: '#fff3cd', color: '#b05f00', p: 1, borderRadius: 1.5, fontWeight: 800,
                                border: '1px solid #f9a825', minHeight: 48, display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <Typography variant="body2" sx={{ fontWeight: 800 }}>
                                    🍴 LUNCH BREAK
                                </Typography>
                            </Box>
                        ) : (
                            <Cell entries={entries} slotKey={key} />
                        )}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {/* empty state */}
      {!loading && !error && (!rows || rows.length === 0) && (
        <Alert severity="info" sx={{ mt: 2, borderRadius: 2 }}>
          No timetable entries found for this selection. Tip: verify backend returns records for
          <strong> dept_id={String(selected?.dept_id || "")} </strong> and <strong> section_id={String(selected?.section_id || "")} </strong>.
        </Alert>
      )}

      {!loading && !error && (
        <Box sx={{ mt: 2, color: "text.secondary", display: "flex", alignItems: "center", gap: 1 }}>
          <Divider flexItem />
          <Typography variant="caption">Professional view • Subject, Faculty & Room visible</Typography>
          <Divider flexItem />
        </Box>
      )}
    </Container>
  );
}
