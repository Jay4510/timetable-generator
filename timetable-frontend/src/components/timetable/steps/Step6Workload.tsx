import { useState, useMemo, useEffect } from 'react';
import { WorkloadData, Faculty, WelcomeData, CurriculumData } from '@/types/timetable';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Briefcase, CheckCircle2, AlertCircle, Wand2, RefreshCw, AlertTriangle } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface Step6WorkloadProps {
  data: WorkloadData;
  faculty: Faculty[];
  welcomeData: WelcomeData;
  curriculum: CurriculumData;
  onUpdate: (data: WorkloadData) => void;
}

interface AssignableOption {
  value: string;
  label: string;
  subjectName: string;
  division: string;
  type: string;
  load: number;
}

export const Step6Workload = ({
  data,
  faculty,
  welcomeData,
  curriculum,
  onUpdate,
}: Step6WorkloadProps) => {
  const [selectedTeacherId, setSelectedTeacherId] = useState<string>(faculty[0]?.id || '');
  const [activeTab, setActiveTab] = useState<'theory' | 'lab'>('theory');

  // --- 1. PREPARE OPTIONS (Hierarchy Aware) ---
  const { theoryOptions, labOptions } = useMemo(() => {
    const tOptions: AssignableOption[] = [];
    const lOptions: AssignableOption[] = [];
    const activeClasses = welcomeData.classes.filter((c) => c.selected);

    activeClasses.forEach((cls) => {
      const divisions = Array.from({ length: cls.divisions }, (_, i) => 
        `${cls.name}-${String.fromCharCode(65 + i)}`
      );

      divisions.forEach((div) => {
        // Theory & Electives
        curriculum.theorySubjects
          .filter((sub) => sub.year === cls.name)
          .forEach((sub) => {
            tOptions.push({
              value: `${sub.name}::${div}::${sub.type.toUpperCase()}`,
              label: `${sub.name} (${div})`,
              subjectName: sub.name,
              division: div,
              type: sub.type,
              load: sub.weeklyLoad,
            });
          });

        // Labs & Tutorials
        curriculum.labSubjects
          .filter((sub) => sub.year === cls.name)
          .forEach((sub) => {
            const batchCount = sub.batchCount || 3;
            // Add entry for each batch
            for (let b = 1; b <= batchCount; b++) {
              const batchDiv = `${div}${b}`; // e.g. SE-A1
              lOptions.push({
                value: `${sub.name}::${batchDiv}::${sub.type.toUpperCase()}`,
                label: `${sub.name} (${batchDiv})`,
                subjectName: sub.name,
                division: batchDiv,
                type: sub.type, // "Lab" or "Tutorial"
                load: sub.sessionsPerWeek * sub.durationPerSession,
              });
            }
          });
      });
    });

    return { theoryOptions: tOptions, labOptions: lOptions };
  }, [welcomeData, curriculum]);

  // --- 2. LOCAL STATE ---
  const [structuredPrefs, setStructuredPrefs] = useState<Record<string, { theory: string[], lab: string[] }>>({});

  useEffect(() => {
    if (data.allocations.length > 0 && Object.keys(structuredPrefs).length === 0) {
      const initialMap: Record<string, { theory: string[], lab: string[] }> = {};
      
      data.allocations.forEach(alloc => {
        Object.entries(alloc.divisions).forEach(([div, teacherId]) => {
          if (teacherId) {
            // Determine type based on Division string (Batch has number at end)
            // But better to infer from subject list. Here we use heuristics.
            const isBatch = /\d$/.test(div);
            // We need to match the Value string format to restore dropdowns
            const sub = [...curriculum.theorySubjects, ...curriculum.labSubjects].find(s => s.name === alloc.subjectName);
            const typeKey = (sub && (sub.type === 'Lab' || sub.type === 'Tutorial')) ? 'lab' : 'theory';
            
            const val = `${alloc.subjectName}::${div}::${sub?.type.toUpperCase() || 'THEORY'}`;
            
            if (!initialMap[teacherId]) initialMap[teacherId] = { theory: [], lab: [] };
            
            const list = initialMap[teacherId][typeKey];
            if (list.length < (typeKey === 'theory' ? 5 : 5)) list.push(val); // Max 5 slots each
          }
        });
      });
      // Pad
      Object.keys(initialMap).forEach(key => {
         while(initialMap[key].theory.length < 5) initialMap[key].theory.push('');
         while(initialMap[key].lab.length < 5) initialMap[key].lab.push('');
      });
      setStructuredPrefs(initialMap);
    }
  }, []); 

  // --- 3. AUTO ASSIGN ---
  const handleAutoAssign = () => {
    if (faculty.length === 0) {
      toast({ title: "No Faculty", variant: "destructive" });
      return;
    }
    const newPrefs: Record<string, { theory: string[], lab: string[] }> = {};
    faculty.forEach(f => newPrefs[f.id] = { theory: [], lab: [] });

    // Round Robin Logic
    let tPtr = 0, lPtr = 0;
    
    // Assign Theory
    theoryOptions.forEach(opt => {
      // Find teacher with capacity
      for(let i=0; i<faculty.length; i++) {
        const idx = (tPtr + i) % faculty.length;
        const id = faculty[idx].id;
        if(newPrefs[id].theory.length < 5) {
          newPrefs[id].theory.push(opt.value);
          tPtr = idx + 1;
          break;
        }
      }
    });

    // Assign Labs
    labOptions.forEach(opt => {
      for(let i=0; i<faculty.length; i++) {
        const idx = (lPtr + i) % faculty.length;
        const id = faculty[idx].id;
        if(newPrefs[id].lab.length < 5) {
          newPrefs[id].lab.push(opt.value);
          lPtr = idx + 1;
          break;
        }
      }
    });

    // Pad
    faculty.forEach(f => {
      while(newPrefs[f.id].theory.length < 5) newPrefs[f.id].theory.push('');
      while(newPrefs[f.id].lab.length < 5) newPrefs[f.id].lab.push('');
    });

    setStructuredPrefs(newPrefs);
    syncToGlobal(newPrefs);
    toast({ title: "Auto-Assignment Complete" });
  };

  const clearAll = () => {
    const cleared: any = {};
    faculty.forEach(f => cleared[f.id] = { theory: Array(5).fill(''), lab: Array(5).fill('') });
    setStructuredPrefs(cleared);
    syncToGlobal(cleared);
    toast({ title: "Allocations Cleared" });
  };

  // --- 4. VALIDATION & SYNC ---
  const updatePreference = (tId: string, type: 'theory' | 'lab', index: number, value: string) => {
    const prev = structuredPrefs[tId] || { theory: Array(5).fill(''), lab: Array(5).fill('') };
    const newList = [...prev[type]];
    newList[index] = value;
    const newState = { ...structuredPrefs, [tId]: { ...prev, [type]: newList } };
    setStructuredPrefs(newState);
    syncToGlobal(newState);
  };

  const syncToGlobal = (state: Record<string, { theory: string[], lab: string[] }>) => {
    const newAllocations: any[] = [];
    Object.entries(state).forEach(([tId, prefs]) => {
      [...prefs.theory, ...prefs.lab].forEach(val => {
        if (!val) return;
        const parts = val.split('::');
        if (parts.length < 3) return;
        
        const div = parts[parts.length - 2];
        const subName = parts.slice(0, parts.length - 2).join('::');

        let alloc = newAllocations.find(a => a.subjectName === subName);
        if (!alloc) {
          alloc = { subjectName: subName, subjectId: subName, divisions: {} };
          newAllocations.push(alloc);
        }
        alloc.divisions[div] = tId;
      });
    });
    onUpdate({ ...data, allocations: newAllocations });
  };

  // --- RENDER ---
  const renderDropdowns = (type: 'theory' | 'lab') => {
    const slots = [0, 1, 2, 3, 4];
    const currentPrefs = structuredPrefs[selectedTeacherId]?.[type] || Array(5).fill('');
    const optionsList = type === 'theory' ? theoryOptions : labOptions;

    // Group options by Subject Name for better hierarchy in dropdown
    const groupedOptions = useMemo(() => {
        const groups: Record<string, AssignableOption[]> = {};
        optionsList.forEach(opt => {
            if(!groups[opt.subjectName]) groups[opt.subjectName] = [];
            groups[opt.subjectName].push(opt);
        });
        return groups;
    }, [optionsList]);

    return slots.map((index) => {
      // Filter out options already selected *by this teacher* in other slots
      const selectedOthers = currentPrefs.filter((_, i) => i !== index);
      
      return (
        <div key={index} className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-1 block uppercase tracking-wider">Assignment {index + 1}</label>
          <Select
            value={currentPrefs[index] || ''}
            onValueChange={(val) => updatePreference(selectedTeacherId, type, index, val)}
          >
            <SelectTrigger className="bg-white"><SelectValue placeholder="-- Select --" /></SelectTrigger>
            <SelectContent className="max-h-[300px]">
              <SelectItem value="unassigned_placeholder">None</SelectItem>
              {Object.entries(groupedOptions).map(([subject, opts]) => (
                  <div key={subject}>
                      <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground bg-muted/20">{subject}</div>
                      {opts.map(opt => {
                          const isTaken = selectedOthers.includes(opt.value);
                          if(isTaken) return null;
                          return (
                            <SelectItem key={opt.value} value={opt.value} className="pl-4">
                                {opt.division} <span className="ml-2 text-[10px] text-muted-foreground">({opt.load}h)</span>
                            </SelectItem>
                          )
                      })}
                  </div>
              ))}
            </SelectContent>
          </Select>
        </div>
      );
    });
  };

  const selectedTeacher = faculty.find(f => f.id === selectedTeacherId);

  return (
    <div className="form-section animate-slide-up h-[75vh] flex flex-col">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-6 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full gradient-navy flex items-center justify-center">
            <Briefcase className="w-6 h-6 text-gold" />
          </div>
          <div>
            <h2 className="section-title mb-0">Workload Allocation</h2>
            <p className="text-muted-foreground text-sm">Assign subjects and practicals to faculty</p>
          </div>
        </div>
        <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={clearAll} className="gap-2">
                <RefreshCw className="w-4 h-4" /> Reset
            </Button>
            <Button onClick={handleAutoAssign} size="sm" className="gap-2 bg-purple-600 hover:bg-purple-700 text-white">
                <Wand2 className="w-4 h-4" /> Auto Fill
            </Button>
        </div>
      </div>

      <div className="flex flex-1 gap-6 min-h-0">
        {/* Faculty List Sidebar */}
        <div className="w-1/3 border rounded-lg bg-card overflow-hidden flex flex-col shadow-sm">
          <div className="p-3 border-b bg-muted/30 font-semibold text-sm flex-shrink-0">Faculty List</div>
          <div className="flex-1 overflow-y-auto">
            {faculty.map((f) => {
              const prefs = structuredPrefs[f.id] || { theory: [], lab: [] };
              const loadCount = prefs.theory.filter(Boolean).length + prefs.lab.filter(Boolean).length;
              return (
                <button
                  key={f.id}
                  onClick={() => setSelectedTeacherId(f.id)}
                  className={`w-full text-left p-3 border-b transition-colors hover:bg-muted/50 flex items-center justify-between
                    ${selectedTeacherId === f.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : 'border-l-4 border-l-transparent'}
                  `}
                >
                  <div>
                    <div className="font-medium text-sm">{f.name}</div>
                    <div className="text-[10px] text-muted-foreground">{f.role}</div>
                  </div>
                  {loadCount > 0 && <Badge variant="secondary" className="text-[10px] h-5 px-1.5">{loadCount}</Badge>}
                </button>
              );
            })}
          </div>
        </div>

        {/* Allocation Panel */}
        <div className="flex-1 flex flex-col border rounded-lg bg-card p-6 overflow-hidden shadow-sm">
          {selectedTeacher ? (
            <>
              <div className="flex items-center justify-between mb-6 flex-shrink-0">
                <div>
                  <h3 className="text-lg font-bold font-display text-primary">{selectedTeacher.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedTeacher.shift === '9-5' ? 'Morning Shift' : 'Afternoon Shift'} • {selectedTeacher.experience} Yrs</p>
                </div>
                <div className="text-right">
                    <Badge variant="outline" className="font-mono">{selectedTeacher.shortCode}</Badge>
                </div>
              </div>
              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full flex-1 flex flex-col min-h-0">
                <TabsList className="grid w-full grid-cols-2 mb-6 flex-shrink-0">
                  <TabsTrigger value="theory">Theory Subjects</TabsTrigger>
                  <TabsTrigger value="lab">Labs & Tutorials</TabsTrigger>
                </TabsList>
                
                <TabsContent value="theory" className="flex-1 overflow-y-auto pr-2 animate-fade-in">
                  <div className="bg-blue-50/50 p-3 rounded-md border border-blue-100 mb-4 text-xs text-blue-800">
                    Assign main lectures and electives here.
                  </div>
                  {renderDropdowns('theory')}
                </TabsContent>
                
                <TabsContent value="lab" className="flex-1 overflow-y-auto pr-2 animate-fade-in">
                  <div className="bg-orange-50/50 p-3 rounded-md border border-orange-100 mb-4 text-xs text-orange-800">
                    Assign specific batches (e.g. A1, A2) for Labs and Tutorials.
                  </div>
                  {renderDropdowns('lab')}
                </TabsContent>
              </Tabs>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <AlertCircle className="w-10 h-10 mb-2 opacity-20" />
              <p>Select a faculty member to start</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};