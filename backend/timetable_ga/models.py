# timetable_ga/models.py
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

@dataclass(frozen=True, slots=True)
class Gene:
    # A single scheduled session (THEORY = 1 period, LAB = contiguous_block_size periods)
    section_id: int
    subject_id: int
    faculty_id: int
    room_id: int
    slot_id: int         # start slot_id (if LAB, this is the first of the block)
    block_size: int      # 1 for theory; 2/3 for lab

    def to_tuple(self) -> Tuple[int, int, int, int, int, int]:
        return (self.section_id, self.subject_id, self.faculty_id, self.room_id, self.slot_id, self.block_size)

    def to_dict(self) -> Dict:
        return asdict(self)

    def occupied_slots(self) -> List[int]:
        # LAB occupies consecutive slots; theory occupies one
        return [self.slot_id + k for k in range(self.block_size)]

# Light DTOs from DB
@dataclass(slots=True)
class Subject:
    subject_id: int
    lecture_count: int
    subj_type: str            # 'THEORY' | 'LAB'
    contiguous_block_size: int

@dataclass(slots=True)
class Section:
    section_id: int
    name: str
    student_count: int

@dataclass(slots=True)
class Room:
    room_id: int
    rtype: str                # 'LECTURE' | 'LAB'
    capacity: int

@dataclass(slots=True)
class Faculty:
    faculty_id: int
    max_load: int

# All input the GA needs (already in memory, app.py se load karke bhejo)
@dataclass(slots=True)
class GAInput:
    sections: Dict[int, Section]
    subjects: Dict[int, Subject]                      # subject_id -> Subject
    curriculum: List[Tuple[int,int,int]]              # (section_id, subject_id, faculty_id)
    rooms: Dict[int, Room]
    faculty: Dict[int, Faculty]
    faculty_unavailability: Dict[int, set]            # faculty_id -> set(slot_id)
    timeslots_usable: set                             # set of slot_id usable (no lunch)
    # Calendar params
    periods_per_day: int
    days: int