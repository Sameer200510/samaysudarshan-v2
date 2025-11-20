from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Set

@dataclass(slots=True)
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
    subj_type: str = "THEORY"
    contiguous_block_size: int = 1

    def kind(self) -> str:
        # Always return final LAB/THEORY
        if (self.subj_type or "").upper() == "LAB":
            return "LAB"
        # fallback by block size
        return "LAB" if (self.contiguous_block_size or 1) > 1 else "THEORY"

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
    sections: Dict[int, "Section"]
    subjects: Dict[int, "Subject"]
    curriculum: List[tuple]              # (section_id, subject_id, faculty_id)
    rooms: Dict[int, "Room"]
    faculty: Dict[int, "Faculty"]
    faculty_unavailability: Dict[int, Set[int]]
    timeslots_usable: Set[int]
    periods_per_day: int
    days: int
    slot_order: List[int]

    # NEW: lunch window slots (set of slot_id that fall into lunch window)
    lunch_slots: Set[int] = field(default_factory=set)
