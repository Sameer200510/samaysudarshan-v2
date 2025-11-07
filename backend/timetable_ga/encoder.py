# timetable_ga/encoder.py
from typing import Dict, List
from .models import Gene, GAInput

def chromosome_to_rows(chrom: Dict[int, List[Gene]]):
    rows = []
    for sec, arr in chrom.items():
        for g in arr:
            rows.append({
                "section_id": g.section_id,
                "subject_id": g.subject_id,
                "faculty_id": g.faculty_id,
                "room_id": g.room_id,
                "slot_id": g.slot_id,
                "duration": g.block_size
            })
    return rows