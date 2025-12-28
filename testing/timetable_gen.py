import random
import webbrowser
import os
import copy
from collections import defaultdict

# ==========================================
# 1. CONFIGURATION
# ==========================================

CONSTANTS = {
    'DAYS': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    'SLOTS': [
        '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00', 
        '01:00-01:30 (Break)', 
        '01:30-02:30', '02:30-03:30', '03:30-04:30', '04:30-05:30'
    ],
    'RECESS_INDEX': 4,
    'THEORY_ROOMS': ['701', '702', '703', '704', '705'],
    'LAB_ROOMS': ['801', '802', '803', '804', '805', '806'],
    'MATHS_LAB': '902'
}

# Define Home Rooms for Stability
HOME_ROOMS = {
    'SE-A': '701', 'SE-B': '702', 'SE-C': '703',
    'TE-A': '704', 'BE-A': '704', # Collision: BE/TE share rooms
    'TE-B': '705', 'BE-B': '705'  # Collision: BE/TE share rooms
}

# ==========================================
# 2. DATA MAPPING
# ==========================================

ALL_TEACHERS = {
    'T1': 'T1', 'T2': 'T2', 'T3': 'T3', 'T4': 'T4', 'T5': 'T5',
    'T6': 'T6', 'T7': 'T7', 'T8': 'T8', 'T9': 'T9', 'T10': 'T10',
    'T11': 'T11', 'T12': 'T12', 'T13': 'T13', 'T14': 'T14', 'T15': 'T15',
    'T16': 'T16', 'T17': 'T17', 'T18': 'T18', 'T19': 'T19', 'T20': 'T20',
    'T21': 'T21', 'T22': 'Mrs. Smitha'
}

THEORY_DATA = [
    # --- SE ---
    ('T2', 'CNND', ['SE-A', 'SE-B'], 3),
    ('T7', 'CNND', ['SE-C'], 3),
    ('T7', 'BMD', ['SE-A', 'SE-B'], 2),
    ('T9', 'DT', ['SE-B'], 2),
    ('T11', 'DT', ['SE-C'], 2),
    ('T12', 'MDM', ['SE-C'], 3),
    ('T12', 'DT', ['SE-A'], 2),
    ('T14', 'MDM', ['SE-A'], 3),
    ('T15', 'BMD', ['SE-C'], 2),
    ('T17', 'PP', ['SE-B', 'SE-C'], 2),
    ('T17', 'MDM', ['SE-A'], 3), 
    ('T18', 'OS', ['SE-B', 'SE-C'], 3),
    ('T19', 'OE', ['SE-A', 'SE-B', 'SE-C'], 2),
    ('T20', 'MDM', ['SE-B', 'SE-C'], 3),
    ('T22', 'Maths-4', ['SE-A', 'SE-B', 'SE-C'], 2), 
    
    # --- TE ---
    ('T9', 'DMBI', ['TE-A'], 3),
    ('T16', 'DMBI', ['TE-B'], 3),
    ('T10', 'AIDS', ['TE-A'], 3),
    ('T11', 'AIDS', ['TE-B'], 3),
    ('T14', 'WebX', ['TE-A'], 3),
    ('T21', 'WebX', ['TE-B'], 3),
    ('T15', 'WT', ['TE-A', 'TE-B'], 3),
    
    # --- BE ---
    ('T3', 'BDLT', ['BE-A', 'BE-B'], 3),
    ('T12', 'BDA', ['BE-A', 'BE-B'], 3),
    ('T4', 'PM', ['BE-A'], 3),
    ('T6', 'PM', ['BE-B'], 3),
]

ELECTIVE_DATA = [
    ('EHF', 'T1', 'GIT', 'T14', ['TE-A', 'TE-B'], 3),
    ('UID', 'T13', 'CCS', 'T8', ['BE-A', 'BE-B'], 3)
]

LAB_TASKS = [
    # --- SE LABS ---
    ('SE-A', ['A1','A2','A3'], 'NDL', 'T2'),
    ('SE-B', ['B1','B2'],      'NDL', 'T4'),
    ('SE-A', ['A1','A2','A3'], 'UL', 'T5'),
    ('SE-B', ['B1','B2'],      'UL', 'T5'),
    ('SE-A', ['A1'],           'DT', 'T6'),
    ('SE-A', ['A1','A2','A3'], 'BMD', 'T7'),
    ('SE-C', ['C1'],           'BMD', 'T7'),
    
    ('SE-B', ['B1','B2'],      'DT', 'T9'),
    ('SE-B', ['B1','B2','B3'], 'PP', 'T10'),

    ('SE-C', ['C2','C3'],      'DT', 'T11'),
    ('SE-C', ['C1'],           'MDM', 'T12'), 
    ('SE-A', ['A1'],           'MDM', 'T12'), 
    ('SE-A', ['A2','A3'],      'DT', 'T12'),
    ('SE-B', ['B1','B2','B3'], 'BMD', 'T13'),
    ('SE-A', ['A2'],           'MDM', 'T14'),
    ('SE-C', ['C1','C2','C3'], 'NDL', 'T16'),
    ('SE-A', ['A1','A2','A3'], 'PP', 'T17'),
    ('SE-C', ['C3'],           'PP', 'T17'),
    ('SE-C', ['C1','C2','C3'], 'UL', 'T18'),
    ('SE-B', ['B3'],           'UL', 'T18'),
    ('SE-A', ['A3'],           'MDM', 'T18'),
    ('SE-B', ['B3'],           'NDL', 'T19'),
    ('SE-B', ['B3'],           'DT', 'T19'),
    ('SE-C', ['C1'],           'DT', 'T19'),
    ('SE-C', ['C2','C3'],      'BMD', 'T19'),
    ('SE-B', ['B1','B2','B3'], 'MDM', 'T20'),
    ('SE-C', ['C2','C3'],      'MDM', 'T20'),
    
    # --- TE LABS ---
    ('TE-A', ['A1','A2','A3'], 'BIL', 'T9'),
    ('TE-B', ['B1','B2','B3'], 'BIL', 'T16'),
    ('TE-A', ['A1','A2','A3'], 'WL', 'T14'),
    ('TE-B', ['B1','B2','B3'], 'WL', 'T13'),
    ('TE-A', ['A1','A2','A3'], 'SL', 'T1'),
    ('TE-B', ['B1','B2','B3'], 'SL', 'T15'),
    ('TE-A', ['A1','A2','A3'], 'DSPYL', 'T10'),
    ('TE-B', ['B1','B2','B3'], 'DSPYL', 'T11'),
    ('TE-A', ['A1','A2','A3'], 'MPWA', 'T6'),
    ('TE-B', ['B1','B2','B3'], 'MPWA', 'T21'),
    
    # --- BE LABS ---
    ('BE-A', ['A1','A2','A3'], 'BDLT Lab', 'T3'),
    ('BE-B', ['B1','B2','B3'], 'BDLT Lab', 'T4'),
    ('BE-A', ['A1','A2','A3'], 'CCL', 'T8'),
    ('BE-B', ['B1','B2','B3'], 'CCL', 'T8'),
]

# ==========================================
# 3. CLASSES
# ==========================================

class Teacher:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.current_load = 0
        self.max_load = 40
    def assign_load(self, duration=1): self.current_load += duration
    def __repr__(self): return self.name

class Gene:
    def __init__(self, div, type, subject, teacher=None, duration=1, lab_subjects=None, teachers_list=None, batch=None):
        self.div = div
        self.type = type 
        self.subject = subject 
        self.lab_subjects = lab_subjects 
        self.duration = duration
        self.teacher = teacher 
        self.teachers_list = teachers_list 
        self.batch = batch 
        self.day = -1
        self.slot = -1
        self.assigned_room = []
    def __repr__(self): return f"{self.div}|{self.subject}"

class Schedule:
    def __init__(self, genes):
        self.genes = genes
        self.grid = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        self.div_slots = defaultdict(lambda: defaultdict(list))
        self.teacher_slots = defaultdict(lambda: defaultdict(list))
        self.theory_rooms_used = defaultdict(lambda: defaultdict(int))
        self.div_batch_busy = defaultdict(lambda: defaultdict(lambda: defaultdict(set))) 
        self.div_subject_history = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
        self.div_type_history = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

    def is_free(self, day, start, duration, div, teachers=None, rooms=None, batches=None):
        for s in range(start, start + duration):
            if s == CONSTANTS['RECESS_INDEX']: return False
            if s >= 9: return False
            
            if batches:
                current_busy = self.div_batch_busy[day][s][div]
                if "ALL" in current_busy: return False
                for b in batches:
                    if b in current_busy: return False
            else:
                if self.div_batch_busy[day][s][div]: return False

            if teachers:
                for t in teachers:
                    if t and t.id != "-1" and t.id in self.grid[day][s]['teacher']: return False
            if rooms:
                for r in rooms:
                    if r != "Library" and r in self.grid[day][s]['room']: return False
        return True

    def book(self, gene, day, start, rooms, teachers):
        gene.day = day
        gene.slot = start
        gene.assigned_room = rooms
        for i in range(gene.duration):
            idx = start + i
            self.div_subject_history[day][idx][gene.div] = gene.subject
            self.div_type_history[day][idx][gene.div] = gene.type
            self.div_slots[gene.div][day].append(idx)

            if gene.batch: 
                self.div_batch_busy[day][idx][gene.div].add(gene.batch)
            elif gene.type == "LAB": 
                for b in gene.lab_subjects: 
                    self.div_batch_busy[day][idx][gene.div].add(b)
            else: 
                self.div_batch_busy[day][idx][gene.div].add("ALL")

            if teachers:
                for t in teachers:
                    if t and t.id != "-1":
                        self.grid[day][idx]['teacher'].add(t.id)
                        self.teacher_slots[t.id][day].append(idx)
            for r in rooms:
                if r != "Library": self.grid[day][idx]['room'].add(r)
            
            if gene.type == "THEORY": self.theory_rooms_used[day][idx] += 1
            elif gene.type == "ELECTIVE": self.theory_rooms_used[day][idx] += 2

# ==========================================
# 4. WORKLOAD GENERATION
# ==========================================

teachers_obj = {}
for tid, name in ALL_TEACHERS.items(): teachers_obj[tid] = Teacher(tid, name)

def distribute_workload():
    all_genes = []
    
    # 1. Theory
    for tid, subj, divs, count in THEORY_DATA:
        for div in divs:
            t = teachers_obj.get(tid)
            if t: t.assign_load(count)
            for _ in range(count):
                all_genes.append(Gene(div, "THEORY", subj, teacher=t))
                
    # 2. Electives
    for s1, tid1, s2, tid2, divs, count in ELECTIVE_DATA:
        for div in divs:
            t1 = teachers_obj.get(tid1)
            t2 = teachers_obj.get(tid2)
            if t1: t1.assign_load(count)
            if t2: t2.assign_load(count)
            for _ in range(count):
                g = Gene(div, "ELECTIVE", f"{s1} / {s2}", teachers_list=[t1, t2], duration=1)
                all_genes.append(g)
                
    # 3. Atomic Labs
    for div, batches, subj, tid in LAB_TASKS:
        t = teachers_obj.get(tid)
        if t: t.assign_load(len(batches) * 2) 
        for b in batches:
            g = Gene(div, "LAB", subj, duration=2, teacher=t, batch=b, lab_subjects=[b])
            all_genes.append(g)
            
    # 4. Maths Tut (SE)
    t_math = teachers_obj['T22']
    for div in ['SE-A', 'SE-B', 'SE-C']:
        for b in ['A1','A2','A3','B1','B2','B3','C1','C2','C3']: 
            if b.startswith(div.split('-')[1]):
                g = Gene(div, "MATHS_TUT", f"Maths Tut", duration=1, teacher=t_math, batch=b)
                all_genes.append(g)

    return all_genes

# ==========================================
# 5. SOLVER UTILS
# ==========================================

def get_theory_rooms(schedule, day, slot, div, count=1):
    available = []
    
    # 1. Check Home Room First
    home = HOME_ROOMS.get(div)
    if home and schedule.is_free(day, slot, 1, None, rooms=[home]):
        available.append(home)
        # If we need just 1 room and home is free, take it!
        if count == 1: return available
    
    # 2. Check Random Pool for remaining needed rooms
    pool = list(CONSTANTS['THEORY_ROOMS'])
    random.shuffle(pool)
    for r in pool:
        if r != home and schedule.is_free(day, slot, 1, None, rooms=[r]):
            available.append(r)
            if len(available) == count: return available
            
    if len(available) == count: return available
    return None

def get_lab_room(schedule, day, start, duration):
    pool = list(CONSTANTS['LAB_ROOMS'])
    random.shuffle(pool)
    for r in pool:
        if schedule.is_free(day, start, duration, None, rooms=[r]):
            return r
    return None

def check_soft_constraints(schedule, div, day, slot, gene):
    cost = 0

    # 1. GRAVITY
    cost += slot * 10 

    # 2. BE MORNING COMPRESSION
    if "BE" in div and slot >= 4:
        cost += 50000

    # 3. PREVENT TRAPPING STUDENTS
    if gene.type in ["THEORY", "ELECTIVE"] and slot >= 7:
        afternoon_activity = schedule.div_batch_busy[day][5][div]
        if afternoon_activity and "ALL" not in afternoon_activity:
             return 100000

    # 4. PREVENT ISOLATED LABS
    if gene.type == "LAB" and slot == 5:
        has_late_lecture = False
        for check_s in [7, 8]:
            if schedule.div_type_history[day][check_s][div] in ["THEORY", "ELECTIVE"]:
                has_late_lecture = True
                break
        if has_late_lecture:
            return 10000

    # 5. HOLE ELIMINATION
    current_slots = schedule.div_slots[div][day]
    if current_slots:
        simulated_slots = current_slots + [slot for s in range(gene.duration)]
        simulated_slots = sorted(list(set(simulated_slots)))
        start_t = min(simulated_slots)
        end_t = max(simulated_slots)
        span = end_t - start_t + 1
        lecture_count = len(simulated_slots)
        holes = span - lecture_count
        if start_t < CONSTANTS['RECESS_INDEX'] < end_t:
            holes -= 1 
        if holes > 0: cost += (holes * 2000)
        else: cost -= 500

    # 6. ANTI-BOREDOM
    if gene.type == "THEORY":
        prev1 = slot - 1
        if prev1 == CONSTANTS['RECESS_INDEX']: prev1 -= 1
        prev2 = prev1 - 1
        if prev2 == CONSTANTS['RECESS_INDEX']: prev2 -= 1
        if prev1 >= 0 and prev2 >= 0:
            t1 = schedule.div_type_history[day][prev1][div]
            t2 = schedule.div_type_history[day][prev2][div]
            if t1 in ["THEORY", "ELECTIVE"] and t2 in ["THEORY", "ELECTIVE"]:
                cost += 500 

    # 7. Anti-Repeat
    prev_s = slot - 1
    if prev_s == CONSTANTS['RECESS_INDEX']: prev_s -= 1
    if prev_s >= 0:
         prev_subj = schedule.div_subject_history[day][prev_s][div]
         if prev_subj and prev_subj == gene.subject: return 10000 
    next_s = slot + 1
    if next_s == CONSTANTS['RECESS_INDEX']: next_s += 1
    if next_s < 9:
         next_subj = schedule.div_subject_history[day][next_s][div]
         if next_subj and next_subj == gene.subject: return 10000 

    # 8. Gap Filling
    if gene.type == "MATHS_TUT":
        busy_batches = schedule.div_batch_busy[day][slot][div]
        if busy_batches and "ALL" not in busy_batches:
             return -10000 
        if slot >= 6: return -200

    # 9. Lab Packing
    if gene.type == "LAB":
        busy_batches = schedule.div_batch_busy[day][slot][div]
        if busy_batches: cost -= 2000 
        
    return cost

def run_solver(iterations=5000): 
    print("--- Starting Final Solver (Zero Gaps + Anti-Trap + Home Rooms) ---")
    base_genes = distribute_workload()
    best_fitness = -float('inf')
    best_sched = None
    
    def priority_sort(g):
        if "BE" in g.div: return 0  
        if g.type == "MATHS_TUT": return 1 
        if g.type == "LAB": return 2
        if g.type == "ELECTIVE": return 3
        return 4

    base_genes.sort(key=priority_sort)

    for run in range(iterations):
        all_genes = copy.deepcopy(base_genes)
        schedule = Schedule(all_genes)
        unplaced = []
        
        for g in all_genes:
            placed = False
            best_local_cost = float('inf')
            best_move = None
            
            possible_slots = [0, 1, 2, 5, 6, 7] if g.type == "LAB" else [0, 1, 2, 3, 5, 6, 7, 8]
            days = list(range(5)); random.shuffle(days)
            
            for d in days:
                for s in possible_slots:
                    ts = g.teachers_list if g.teachers_list else [g.teacher]
                    target_batches = [g.batch] if g.batch else None
                    if g.type == "LAB": target_batches = [g.batch]
                    
                    if not schedule.is_free(d, s, g.duration, g.div, teachers=ts, batches=target_batches): 
                        continue
                    
                    rooms_to_book = []
                    if g.type == "THEORY":
                        if schedule.theory_rooms_used[d][s] >= 5: continue
                        # UPDATED: Pass 'g.div' to prioritize Home Room
                        rooms = get_theory_rooms(schedule, d, s, g.div, 1)
                        if rooms: rooms_to_book = rooms
                    elif g.type == "ELECTIVE":
                        if schedule.theory_rooms_used[d][s] >= 4: continue
                        # UPDATED: Pass 'g.div'
                        rooms = get_theory_rooms(schedule, d, s, g.div, 2)
                        if rooms: rooms_to_book = rooms
                    elif g.type == "MATHS_TUT":
                        if schedule.is_free(d, s, 1, None, rooms=[CONSTANTS['MATHS_LAB']]):
                            rooms_to_book = [CONSTANTS['MATHS_LAB']]
                    elif g.type == "LAB":
                        r = get_lab_room(schedule, d, s, 2)
                        if r: rooms_to_book = [r]
                    
                    if not rooms_to_book: continue
                    
                    cost = check_soft_constraints(schedule, g.div, d, s, g)
                    if cost >= 10000: continue
                    
                    if cost < best_local_cost:
                        best_local_cost = cost
                        best_move = (d, s, rooms_to_book)
                        if cost <= -1000: break 
                if best_move and best_local_cost <= -1000: break
            
            if best_move:
                d, s, rms = best_move
                ts = g.teachers_list if g.teachers_list else [g.teacher]
                schedule.book(g, d, s, rms, ts)
                placed = True
            else:
                unplaced.append(g)
        
        score = 10000 - (len(unplaced) * 5000)
        
        total_gaps = 0
        for div in schedule.div_slots:
            for d in range(5):
                slots = sorted(schedule.div_slots[div][d])
                if len(slots) > 1:
                    span = slots[-1] - slots[0] + 1
                    gaps = span - len(slots)
                    if slots[0] < 4 and slots[-1] > 4:
                        gaps -= 1
                    if gaps > 0: total_gaps += gaps
        
        score -= (total_gaps * 500) 

        if score > best_fitness:
            best_fitness = score
            best_sched = schedule
            print(f"Run {run}: Score {score} (Unplaced: {len(unplaced)}, Gaps: {total_gaps})")
            if len(unplaced) == 0 and total_gaps == 0: break 
            
    return best_sched

# ==========================================
# 6. HTML GENERATION
# ==========================================

def generate_html(schedule):
    if not schedule: return
    html = """<html><head><style>
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; padding: 20px; color: #333; }
        .div-container { background: white; margin-bottom: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; border: 1px solid #e0e0e0; }
        h2 { background: #2c3e50; color: white; margin: 0; padding: 20px; font-size: 20px; letter-spacing: 0.5px; border-bottom: 4px solid #3498db; }
        table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        th { background: #34495e; color: #ecf0f1; padding: 12px; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
        td { border: 1px solid #e0e0e0; height: 110px; vertical-align: top; padding: 0; font-size: 11px; transition: background 0.2s; }
        td:hover { background-color: #fafafa; }
        .cell-inner { padding: 8px; height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
        .room { font-weight: bold; color: #e74c3c; font-size: 10px; margin-top: 4px; display: block; }
        .elective-tag { font-size: 9px; color: #8e44ad; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
        .lab-item { border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 4px; padding-bottom: 4px; font-size: 10px; width: 100%; }
        .lab-item:last-child { border-bottom: none; margin-bottom: 0; }
        .break { writing-mode: vertical-rl; text-align: center; background: #dfe6e9; font-weight: bold; color: #7f8c8d; font-size: 12px; letter-spacing: 2px; }
        .cont { font-size:9px; color:#95a5a6; font-style:italic; }
        
        .theory-cell { background-color: #e3f2fd; border-left: 3px solid #2196f3; }
        .lab-cell { background-color: #fff3e0; border-left: 3px solid #ff9800; }
        .elective-cell { background-color: #fce4ec; border-left: 3px solid #e91e63; }
        .maths-cell { background-color: #e8f5e9; border-left: 3px solid #4caf50; }
        .free-cell { background-color: #ffffff; }
        
        .sub-name { font-weight: 700; font-size: 12px; color: #2c3e50; }
        .teach-name { font-size: 11px; color: #546e7a; margin-top: 2px; }

    </style></head><body>"""
    
    divisions = sorted(list(set([g.div for g in schedule.genes])))
    for div in divisions:
        html += f"<div class='div-container'><h2>Division: {div}</h2><table><thead><tr><th>Day</th>"
        for s in CONSTANTS['SLOTS']: html += f"<th>{s.split(' ')[0]}</th>"
        html += "</tr></thead><tbody>"
        for day in range(5):
            html += f"<tr><td style='text-align:center; font-weight:bold; background:#f7f9fa; color:#2c3e50; border-right:2px solid #e0e0e0;'>{CONSTANTS['DAYS'][day]}</td>"
            for slot in range(9):
                if slot == CONSTANTS['RECESS_INDEX']:
                    html += "<td class='break'>RECESS</td>"; continue
                
                active_genes = []
                for g in schedule.genes:
                    if g.day == day and g.div == div:
                        if g.slot <= slot < g.slot + g.duration:
                            active_genes.append(g)
                
                if not active_genes:
                    html += "<td class='free-cell'></td>"; continue
                
                first_type = active_genes[0].type
                cell_class = "free-cell"
                if first_type == "THEORY": cell_class = "theory-cell"
                elif first_type == "ELECTIVE": cell_class = "elective-cell"
                elif first_type == "LAB": cell_class = "lab-cell"
                elif first_type == "MATHS_TUT": cell_class = "maths-cell"
                
                content = "<div class='cell-inner'>"
                active_genes.sort(key=lambda x: 0 if x.type in ["LAB", "MATHS_TUT"] else 1)
                
                for g in active_genes:
                    is_continuation = (slot > g.slot)
                    cont_str = "<span class='cont'>(cont.)</span>" if is_continuation else ""
                    
                    if g.type == "THEORY":
                        content += f"<div class='sub-name'>{g.subject}</div><div class='teach-name'>{g.teacher.name}</div><span class='room'>[{g.assigned_room[0]}]</span>"
                    
                    elif g.type == "ELECTIVE":
                        subs = g.subject.split('/')
                        ts = g.teachers_list
                        rs = g.assigned_room
                        content += f"<span class='elective-tag'>ELECTIVE</span><br><div class='sub-name'>{subs[0]}</div> <div class='teach-name'>({ts[0].name})</div> <span class='room'>[{rs[0]}]</span><hr style='width:50%; opacity:0.3; margin:4px 0;'><div class='sub-name'>{subs[1]}</div> <div class='teach-name'>({ts[1].name})</div> <span class='room'>[{rs[1]}]</span>"
                    
                    elif g.type in ["LAB", "MATHS_TUT"]:
                        style = "color:#d84315;" if g.type == "MATHS_TUT" else ""
                        t_name = g.teacher.name if g.teacher else "TBA"
                        room = g.assigned_room[0] if g.assigned_room else "TBA"
                        batch_lbl = g.batch if g.batch else "ALL"
                        content += f"<div class='lab-item' style='{style}'><b>{batch_lbl}:</b> {g.subject} {cont_str}<br>{t_name} [{room}]</div>"

                content += "</div>"
                html += f"<td class='{cell_class}'>{content}</td>"
            html += "</tr>"
        html += "</tbody></table></div>"
    
    with open("timetable_final.html", "w") as f: f.write(html)
    return os.path.abspath("timetable_final.html")

if __name__ == "__main__":
    best = run_solver(5000)
    if best:
        path = generate_html(best)
        webbrowser.open('file://' + path)
    else:
        print("Failed to generate a valid schedule.")