# timetable_ga/initializer.py
import random
from collections import defaultdict
from typing import Dict, List, Tuple
from .models import Gene, GAInput

def build_demand(data: GAInput) -> Dict[int, List[Tuple[int,int,int]]]:
    """
    Returns requirement per section:
      { section_id: [ (subject_id, faculty_id, block_size) repeated by periods needed ], ... }
    LAB of block 2 counts as 2 periods but placed as blocks.
    """
    by_sec = defaultdict(list)
    for (section_id, subject_id, faculty_id) in data.curriculum:
        subj = data.subjects[subject_id]
        if subj.subj_type == 'LAB':
            # number of blocks needed = lecture_count / block_size
            assert subj.lecture_count % subj.contiguous_block_size == 0, "Lab periods must be multiple of block size"
            blocks = subj.lecture_count // subj.contiguous_block_size
            for _ in range(blocks):
                by_sec[section_id].append((subject_id, faculty_id, subj.contiguous_block_size))
        else:
            for _ in range(subj.lecture_count):
                by_sec[section_id].append((subject_id, faculty_id, 1))
    return by_sec

def random_room_for(subj_type: str, data: GAInput, needed_capacity: int) -> int:
    candidates = [r.room_id for r in data.rooms.values()
                  if ((subj_type == 'LAB' and r.rtype == 'LAB') or (subj_type=='THEORY' and r.rtype=='LECTURE'))
                  and r.capacity >= needed_capacity]
    return random.choice(candidates) if candidates else random.choice(list(data.rooms.keys()))

def random_slot_block(block_size: int, data: GAInput) -> int:
    # Pick random start slot where all consecutive slots are usable and within same day
    pday = data.periods_per_day
    while True:
        s = random.choice(tuple(data.timeslots_usable))
        # ensure same day
        base_day = (s-1)//pday
        ok = True
        for k in range(block_size):
            x = s + k
            if (x not in data.timeslots_usable) or ((x-1)//pday != base_day):
                ok = False
                break
        if ok:
            return s

def random_chromosome(data: GAInput) -> Dict[int, List[Gene]]:
    by_sec = build_demand(data)
    chrom = {}
    for sec_id, reqs in by_sec.items():
        genes = []
        size = data.sections[sec_id].student_count
        for (sid, fid, bsize) in reqs:
            subj_type = data.subjects[sid].subj_type
            room = random_room_for(subj_type, data, size)
            slot = random_slot_block(bsize, data)
            genes.append(Gene(section_id=sec_id, subject_id=sid, faculty_id=fid,
                              room_id=room, slot_id=slot, block_size=bsize))
        chrom[sec_id] = genes
    return chrom