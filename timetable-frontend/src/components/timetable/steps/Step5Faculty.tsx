import { useState } from 'react';
import { Faculty, FacultyData, CurriculumData, WelcomeData, WorkloadData } from '@/types/timetable';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Users, Plus, Trash2, UserCog, Wand2, X } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface Step5FacultyProps {
  data: FacultyData;
  workload: WorkloadData;
  curriculum: CurriculumData;
  welcome: WelcomeData;
  onUpdate: (data: FacultyData) => void;
  onUpdateWorkload: (data: WorkloadData) => void;
}

export const Step5Faculty = ({ 
  data, 
  workload, 
  curriculum, 
  welcome, 
  onUpdate, 
  onUpdateWorkload 
}: Step5FacultyProps) => {

  const [activeTeacherId, setActiveTeacherId] = useState<string | null>(null);
  const [assignType, setAssignType] = useState<'theory' | 'lab'>('theory');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedDivisions, setSelectedDivisions] = useState<string[]>([]);
  const [selectedBatches, setSelectedBatches] = useState<string[]>([]);

  const loadDefaults = () => {
    
    // 1. DEFINE TEACHERS
    const facultyList: Faculty[] = [
      { id: 'T1', name: 'T1', shortCode: 'T1', role: 'HOD', experience: 20, shift: '9-5' },
      { id: 'T2', name: 'T2', shortCode: 'T2', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T3', name: 'T3', shortCode: 'T3', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T4', name: 'T4', shortCode: 'T4', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T5', name: 'T5', shortCode: 'T5', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T6', name: 'T6', shortCode: 'T6', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T7', name: 'T7', shortCode: 'T7', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T8', name: 'T8', shortCode: 'T8', role: 'Div Incharge', experience: 15, shift: '9-5' },
      { id: 'T9', name: 'T9', shortCode: 'T9', role: 'Faculty', experience: 8, shift: '10-6' },
      { id: 'T10', name: 'T10', shortCode: 'T10', role: 'Faculty', experience: 8, shift: '10-6' },
      { id: 'T11', name: 'T11', shortCode: 'T11', role: 'Faculty', experience: 8, shift: '10-6' },
      { id: 'T12', name: 'T12', shortCode: 'T12', role: 'Faculty', experience: 5, shift: '10-6' },
      { id: 'T13', name: 'T13', shortCode: 'T13', role: 'Faculty', experience: 5, shift: '10-6' },
      { id: 'T14', name: 'T14', shortCode: 'T14', role: 'Faculty', experience: 5, shift: '10-6' },
      { id: 'T15', name: 'T15', shortCode: 'T15', role: 'Faculty', experience: 5, shift: '10-6' },
      { id: 'T16', name: 'T16', shortCode: 'T16', role: 'Faculty', experience: 3, shift: '10-6' },
      { id: 'T17', name: 'T17', shortCode: 'T17', role: 'Faculty', experience: 3, shift: '10-6' },
      { id: 'T18', name: 'T18', shortCode: 'T18', role: 'Faculty', experience: 3, shift: '10-6' },
      { id: 'T19', name: 'T19', shortCode: 'T19', role: 'Faculty', experience: 2, shift: '10-6' },
      { id: 'T20', name: 'T20', shortCode: 'T20', role: 'Faculty', experience: 2, shift: '10-6' },
      { id: 'T21', name: 'T21', shortCode: 'T21', role: 'Faculty', experience: 1, shift: '10-6' },
      { id: 'T22', name: 'Mrs. Smitha', shortCode: 'Smi', role: 'Faculty', experience: 10, shift: '9-5' },
    ];

    // 2. DEFINE ALLOCATIONS
    const allocations: any[] = [];

    const assignTheory = (tid: string, subject: string, divs: string[]) => {
      let alloc = allocations.find(a => a.subjectName === subject);
      if (!alloc) {
        alloc = { subjectId: subject, subjectName: subject, divisions: {} };
        allocations.push(alloc);
      }
      divs.forEach(div => alloc.divisions[div] = tid);
    };

    // FIXED: Batch Formatting SE-A-A1
    const assignLab = (tid: string, subject: string, divBase: string, batches: number[]) => {
      let alloc = allocations.find(a => a.subjectName === subject);
      if (!alloc) {
        alloc = { subjectId: subject, subjectName: subject, divisions: {} };
        allocations.push(alloc);
      }
      batches.forEach(b => {
        const divChar = divBase.split('-')[1]; // Extract 'A' from 'SE-A'
        const batchId = `${divBase}-${divChar}${b}`; // Creates "SE-A-A1"
        alloc.divisions[batchId] = tid;
      });
    };

    // --- T1 ---
    assignTheory('T1', 'EHF', ['TE-A', 'TE-B']);
    assignLab('T1', 'SL', 'TE-A', [1, 2, 3]);

    // --- T2 ---
    assignTheory('T2', 'CNND', ['SE-A', 'SE-B']);
    assignLab('T2', 'NDL', 'SE-A', [1, 2, 3]);

    // --- T3 ---
    assignTheory('T3', 'BDLT', ['BE-A', 'BE-B']);
    assignLab('T3', 'BDLT Lab', 'BE-A', [1, 2, 3]);

    // --- T4 ---
    assignTheory('T4', 'PM', ['BE-A']);
    assignLab('T4', 'NDL', 'SE-B', [1, 2]); 
    assignLab('T4', 'BDLT Lab', 'BE-B', [1, 2, 3]);

    // --- T5 ---
    assignLab('T5', 'UL', 'SE-A', [1, 2, 3]);
    assignLab('T5', 'UL', 'SE-B', [1, 2]);

    // --- T6 ---
    assignTheory('T6', 'PM', ['BE-B']);
    assignLab('T6', 'DT', 'SE-A', [1]); 
    assignLab('T6', 'MPWA', 'TE-A', [1, 2, 3]);

    // --- T7 ---
    assignTheory('T7', 'CNND', ['SE-C']);
    assignTheory('T7', 'BMD', ['SE-A', 'SE-B']);
    assignLab('T7', 'BMD', 'SE-A', [1, 2, 3]);
    assignLab('T7', 'BMD', 'SE-C', [1]); 

    // --- T8 ---
    assignTheory('T8', 'CCS', ['BE-A', 'BE-B']);
    assignLab('T8', 'CCL', 'BE-A', [1, 2, 3]);
    assignLab('T8', 'CCL', 'BE-B', [1, 2, 3]);

    // --- T9 ---
    assignTheory('T9', 'DT', ['SE-B']);
    assignTheory('T9', 'DMBI', ['TE-A']);
    assignLab('T9', 'DT', 'SE-B', [1, 2]); 
    assignLab('T9', 'BIL', 'TE-A', [1, 2, 3]);

    // --- T10 ---
    assignTheory('T10', 'AIDS', ['TE-A']);
    assignLab('T10', 'PP', 'SE-B', [1, 2, 3]);
    assignLab('T10', 'DSPYL', 'TE-A', [1, 2, 3]);

    // --- T11 ---
    assignTheory('T11', 'DT', ['SE-C']);
    assignTheory('T11', 'AIDS', ['TE-B']);
    assignLab('T11', 'DT', 'SE-C', [2, 3]);
    assignLab('T11', 'DSPYL', 'TE-B', [1, 2, 3]);

    // --- T12 ---
    assignTheory('T12', 'MDM', ['SE-C']);
    assignTheory('T12', 'DT', ['SE-A']);
    assignTheory('T12', 'BDA', ['BE-A', 'BE-B']);
    assignLab('T12', 'MDM', 'SE-C', [1]); 
    assignLab('T12', 'MDM', 'SE-A', [1]); 
    assignLab('T12', 'DT', 'SE-A', [2, 3]);

    // --- T13 ---
    assignTheory('T13', 'UID', ['BE-A', 'BE-B']);
    assignLab('T13', 'BMD', 'SE-B', [1, 2, 3]);

    // --- T14 ---
    assignTheory('T14', 'MDM', ['SE-A']);
    assignTheory('T14', 'WebX', ['TE-A']);
    assignTheory('T14', 'GIT', ['TE-A', 'TE-B']);
    assignLab('T14', 'MDM', 'SE-A', [2]);
    assignLab('T14', 'WL', 'TE-A', [1, 2, 3]);

    // --- T15 ---
    assignTheory('T15', 'BMD', ['SE-C']);
    assignTheory('T15', 'WT', ['TE-A', 'TE-B']);
    assignLab('T15', 'SL', 'TE-B', [1, 2, 3]);

    // --- T16 ---
    assignTheory('T16', 'DMBI', ['TE-B']);
    assignLab('T16', 'NDL', 'SE-C', [1, 2, 3]);
    assignLab('T16', 'BIL', 'TE-B', [1, 2, 3]);

    // --- T17 ---
    assignTheory('T17', 'PP', ['SE-B', 'SE-C']);
    assignTheory('T17', 'MDM', ['SE-A']); 
    assignLab('T17', 'PP', 'SE-A', [1, 2, 3]);
    assignLab('T17', 'PP', 'SE-C', [3]);

    // --- T18 ---
    assignTheory('T18', 'OS', ['SE-B', 'SE-C']);
    assignLab('T18', 'UL', 'SE-C', [1, 2, 3]);
    assignLab('T18', 'UL', 'SE-B', [3]);
    assignLab('T18', 'MDM', 'SE-A', [3]);

    // --- T19 ---
    assignTheory('T19', 'OE', ['SE-A', 'SE-B', 'SE-C']);
    assignLab('T19', 'NDL', 'SE-B', [3]);
    assignLab('T19', 'DT', 'SE-B', [3]);
    assignLab('T19', 'DT', 'SE-C', [1]);
    assignLab('T19', 'BMD', 'SE-C', [2, 3]);

    // --- T20 ---
    assignTheory('T20', 'MDM', ['SE-B', 'SE-C']);
    assignLab('T20', 'MDM', 'SE-B', [1, 2, 3]);
    assignLab('T20', 'MDM', 'SE-C', [2, 3]);

    // --- T21 ---
    assignTheory('T21', 'WebX', ['TE-B']);
    assignLab('T21', 'MPWA', 'TE-B', [1, 2, 3]);

    // --- T22 (Mrs. Smitha) ---
    assignTheory('T22', 'Maths-4', ['SE-A', 'SE-B', 'SE-C']);
    assignLab('T22', 'Maths Tut', 'SE-A', [1, 2, 3]);
    assignLab('T22', 'Maths Tut', 'SE-B', [1, 2, 3]);
    assignLab('T22', 'Maths Tut', 'SE-C', [1, 2, 3]);

    // C. APPLY UPDATES
    onUpdate({ faculty: facultyList });
    onUpdateWorkload({ ...workload, allocations: allocations });

    toast({
      title: "Template Loaded",
      description: "Faculty & Workload assigned based on V66 Data.",
    });
  };

  // --- HELPERS ---
  const getSubjectList = (type: 'theory' | 'lab') => {
    if (!selectedYear) return [];
    if (type === 'theory') {
      return curriculum.theorySubjects.filter(s => s.year === selectedYear);
    }
    return curriculum.labSubjects.filter(s => s.year === selectedYear);
  };

  const getDivisions = () => {
    if (!selectedYear) return [];
    const cls = welcome.classes.find(c => c.name === selectedYear);
    if (!cls) return [];
    return Array.from({ length: cls.divisions }, (_, i) => `${selectedYear}-${String.fromCharCode(65 + i)}`);
  };

  // FIXED: Return SE-A-A1 format
  const getBatches = (division: string) => {
    if (assignType !== 'lab' || !selectedSubject) return [];
    const sub = curriculum.labSubjects.find(s => s.name === selectedSubject); 
    const count = sub?.batchCount || 3;
    const divChar = division.split('-')[1]; // "A" from "SE-A"
    
    // Returns: ["SE-A-A1", "SE-A-A2", "SE-A-A3"]
    return Array.from({ length: count }, (_, i) => `${division}-${divChar}${i + 1}`); 
  };

  // --- ACTIONS ---
  const handleAssign = () => {
    if (!activeTeacherId || !selectedSubject) return;

    const newAllocations = [...workload.allocations];
    let subjectAlloc = newAllocations.find(a => a.subjectName === selectedSubject);
    if (!subjectAlloc) {
      subjectAlloc = {
        subjectId: selectedSubject,
        subjectName: selectedSubject,
        divisions: {}
      };
      newAllocations.push(subjectAlloc);
    }

    if (assignType === 'theory') {
      selectedDivisions.forEach(div => {
        subjectAlloc!.divisions[div] = activeTeacherId;
      });
    } else {
      selectedBatches.forEach(batch => {
        subjectAlloc!.divisions[batch] = activeTeacherId;
      });
    }

    onUpdateWorkload({ ...workload, allocations: newAllocations });
    setSelectedDivisions([]);
    setSelectedBatches([]);
    toast({ title: "Assigned Successfully" });
  };

  const removeAssignment = (subjectName: string, divisionOrBatch: string) => {
    const newAllocations = [...workload.allocations];
    const alloc = newAllocations.find(a => a.subjectName === subjectName);
    if (alloc) {
      delete alloc.divisions[divisionOrBatch];
      if (Object.keys(alloc.divisions).length === 0) {
        const idx = newAllocations.indexOf(alloc);
        newAllocations.splice(idx, 1);
      }
      onUpdateWorkload({ ...workload, allocations: newAllocations });
    }
  };

  const getTeacherAssignments = (teacherId: string) => {
    const assignments: Array<{ subject: string, div: string, type: 'theory' | 'lab' }> = [];
    workload.allocations.forEach(alloc => {
      Object.entries(alloc.divisions).forEach(([div, tid]) => {
        if (tid === teacherId) {
          const isLab = /\d$/.test(div); 
          assignments.push({
            subject: alloc.subjectName,
            div: div,
            type: isLab ? 'lab' : 'theory'
          });
        }
      });
    });
    return assignments;
  };

  const addFaculty = () => {
    const newFaculty: Faculty = {
      id: crypto.randomUUID(),
      name: '',
      shortCode: '',
      role: 'Faculty',
      experience: 1,
      shift: '9-5',
    };
    onUpdate({ faculty: [...data.faculty, newFaculty] });
    setActiveTeacherId(newFaculty.id);
  };

  const updateFaculty = (id: string, field: keyof Faculty, value: any) => {
    const updated = data.faculty.map((f) => f.id === id ? { ...f, [field]: value } : f);
    onUpdate({ faculty: updated });
  };

  const removeFaculty = (id: string) => {
    onUpdate({ faculty: data.faculty.filter((f) => f.id !== id) });
    if (activeTeacherId === id) setActiveTeacherId(null);
  };

  return (
    <div className="form-section animate-slide-up">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full gradient-navy flex items-center justify-center">
            <Users className="w-6 h-6 text-gold" />
          </div>
          <div>
            <h2 className="section-title mb-0">Faculty & Workload</h2>
            <p className="text-muted-foreground text-sm">Define teachers and assign their subjects</p>
          </div>
        </div>
        <div className="flex gap-2">
          {/* IMPORTANT: type="button" prevents form submission refresh */}
          <Button type="button" onClick={loadDefaults} variant="outline" className="gap-2 border-purple-200 hover:bg-purple-50 text-purple-700">
            <Wand2 className="w-4 h-4" /> Load V66 Template
          </Button>
          <Button type="button" onClick={addFaculty} variant="outline" className="gap-2 border-dashed">
            <UserCog className="w-4 h-4" /> Add Teacher
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        {data.faculty.map((f) => {
          const isExpanded = activeTeacherId === f.id;
          const assignments = getTeacherAssignments(f.id);

          return (
            <Card 
              key={f.id} 
              className={`p-0 overflow-hidden transition-all duration-300 border-l-4 ${isExpanded ? 'border-l-gold ring-1 ring-primary/10 shadow-md' : 'border-l-transparent hover:border-l-primary/30'}`}
            >
              {/* Header / Summary Row */}
              <div 
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-muted/5"
                onClick={() => setActiveTeacherId(isExpanded ? null : f.id)}
              >
                <div className="grid gap-4 md:grid-cols-12 items-center flex-1">
                  <div className="md:col-span-1 flex justify-center">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                      {f.shortCode || '??'}
                    </div>
                  </div>

                  <div className="md:col-span-3" onClick={e => e.stopPropagation()}>
                    <Label className="text-[10px] text-muted-foreground uppercase tracking-wider">Name</Label>
                    <Input 
                      value={f.name} 
                      onChange={(e) => updateFaculty(f.id, 'name', e.target.value)} 
                      className="h-8 text-sm" 
                      placeholder="Faculty Name" 
                    />
                  </div>
                  
                  <div className="md:col-span-2" onClick={e => e.stopPropagation()}>
                    <Label className="text-[10px] text-muted-foreground uppercase tracking-wider">Short Code</Label>
                    <Input 
                      value={f.shortCode} 
                      onChange={(e) => updateFaculty(f.id, 'shortCode', e.target.value)} 
                      className="h-8 text-sm" 
                      placeholder="e.g. JD" 
                    />
                  </div>

                  <div className="md:col-span-2" onClick={e => e.stopPropagation()}>
                    <Label className="text-[10px] text-muted-foreground uppercase tracking-wider">Shift</Label>
                    <Select value={f.shift} onValueChange={(val) => updateFaculty(f.id, 'shift', val)}>
                      <SelectTrigger className="h-8"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="9-5">Morning</SelectItem>
                        <SelectItem value="10-6">Afternoon</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="md:col-span-3 flex flex-wrap gap-1 justify-end px-2">
                    {assignments.length === 0 && <span className="text-xs text-muted-foreground italic">No assignments</span>}
                    {assignments.slice(0, 3).map((a, i) => (
                      <Badge key={i} variant="secondary" className="text-[10px] px-1 h-5">
                        {a.subject} ({a.div.split('-')[2] || a.div})
                      </Badge>
                    ))}
                    {assignments.length > 3 && <Badge variant="outline" className="text-[10px] h-5">+{assignments.length - 3}</Badge>}
                  </div>

                  <div className="md:col-span-1 flex justify-end" onClick={e => e.stopPropagation()}>
                    <Button type="button" variant="ghost" size="icon" className="h-8 w-8 text-destructive opacity-50 hover:opacity-100" onClick={() => removeFaculty(f.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* EXPANDED ASSIGNMENT UI */}
              {isExpanded && (
                <div className="border-t bg-muted/5 p-4 animate-slide-down">
                  
                  <div className="mb-6 flex flex-wrap gap-2">
                    {assignments.map((a, i) => (
                      <Badge 
                        key={i} 
                        variant={a.type === 'theory' ? 'default' : 'secondary'} 
                        className={`text-xs pl-2 pr-1 py-1 flex items-center gap-2 ${a.type === 'lab' ? 'bg-orange-100 text-orange-800 hover:bg-orange-200' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'}`}
                      >
                        <span className="font-semibold">{a.subject}</span>
                        <span className="opacity-70 font-mono">[{a.div}]</span>
                        <button type="button" onClick={() => removeAssignment(a.subject, a.div)} className="hover:bg-black/10 rounded-full p-0.5">
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                    {assignments.length === 0 && (
                      <p className="text-sm text-muted-foreground w-full text-center py-2">Select options below to assign subjects to {f.name || 'this teacher'}</p>
                    )}
                  </div>

                  <div className="bg-card border rounded-lg p-4 shadow-sm">
                    <Tabs value={assignType} onValueChange={(v) => setAssignType(v as any)} className="w-full">
                      <div className="flex items-center justify-between mb-4">
                        <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Assign New Workload</Label>
                        <TabsList className="h-8">
                          <TabsTrigger value="theory" className="text-xs h-6 px-3">Theory</TabsTrigger>
                          <TabsTrigger value="lab" className="text-xs h-6 px-3">Lab / Tut</TabsTrigger>
                        </TabsList>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                        
                        <div className="space-y-1">
                          <Label className="text-xs">1. Year</Label>
                          <Select value={selectedYear} onValueChange={(v) => { setSelectedYear(v); setSelectedSubject(''); }}>
                            <SelectTrigger className="h-9"><SelectValue placeholder="Select Year" /></SelectTrigger>
                            <SelectContent>
                              {welcome.classes.filter(c => c.selected).map(c => (
                                <SelectItem key={c.name} value={c.name}>{c.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-1">
                          <Label className="text-xs">2. Subject</Label>
                          <Select value={selectedSubject} onValueChange={setSelectedSubject} disabled={!selectedYear}>
                            <SelectTrigger className="h-9"><SelectValue placeholder="Select Subject" /></SelectTrigger>
                            <SelectContent>
                              {getSubjectList(assignType).map(s => (
                                <SelectItem key={s.id} value={s.name}>
                                  {s.name} <span className="text-muted-foreground text-xs ml-2">({s.code})</span>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-1 md:col-span-1">
                          <Label className="text-xs">3. {assignType === 'theory' ? 'Divisions' : 'Batches'}</Label>
                          
                          <div className="min-h-[36px] p-1 border rounded-md bg-background flex flex-wrap gap-1">
                            {assignType === 'theory' 
                              ? getDivisions().map(div => (
                                  <button
                                    type="button"
                                    key={div}
                                    onClick={() => setSelectedDivisions(prev => prev.includes(div) ? prev.filter(d => d !== div) : [...prev, div])}
                                    className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${selectedDivisions.includes(div) ? 'bg-primary text-primary-foreground border-primary' : 'bg-muted hover:bg-muted/80'}`}
                                  >
                                    {div}
                                  </button>
                                ))
                              : getDivisions().map(div => (
                                  <div key={div} className="flex flex-col gap-1 p-1 border rounded bg-muted/20 w-full">
                                    <span className="text-[9px] font-bold text-muted-foreground ml-1">{div}</span>
                                    <div className="flex flex-wrap gap-1">
                                      {getBatches(div).map(batch => (
                                        <button
                                          type="button"
                                          key={batch}
                                          onClick={() => setSelectedBatches(prev => prev.includes(batch) ? prev.filter(b => b !== batch) : [...prev, batch])}
                                          className={`text-[9px] px-2 py-0.5 rounded border ${selectedBatches.includes(batch) ? 'bg-orange-500 text-white border-orange-600' : 'bg-white hover:bg-gray-100'}`}
                                        >
                                          {/* Display only A1, A2 from SE-A-A1 */}
                                          {batch.split('-')[2]}
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                ))
                            }
                          </div>
                        </div>

                        <div className="flex justify-end">
                          <Button 
                            type="button"
                            size="sm" 
                            onClick={handleAssign} 
                            disabled={!selectedSubject || (assignType === 'theory' ? selectedDivisions.length === 0 : selectedBatches.length === 0)}
                            className="w-full gap-2"
                          >
                            <Plus className="w-4 h-4" /> Assign
                          </Button>
                        </div>

                      </div>
                    </Tabs>
                  </div>

                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
};