import { useState, useEffect, useMemo, Fragment } from 'react';
import { ResultsData, TimingData, WelcomeData, Faculty, InfrastructureData, BackendEntry } from '@/types/timetable';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Download, User, MapPin, Plus, Monitor, FlaskConical, BookOpen, Layers, Briefcase, AlertCircle } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface Step9ResultsProps {
  data: ResultsData;
  timingData: TimingData;
  welcomeData: WelcomeData;
  faculty?: Faculty[]; 
  infrastructure?: InfrastructureData; 
}

type ViewMode = 'MASTER' | 'TEACHER' | 'CLASSROOM' | 'LAB';

// --- HELPER: Available Rooms ---
const getAvailableRooms = (
  timetable: Record<string, Record<string, BackendEntry[]>>,
  allTheoryRooms: string[],
  allLabRooms: string[],
  day: string,
  slotIndex: number
) => {
  const occupied = new Set<string>();
  
  Object.values(timetable).forEach(days => {
    const entries = days[day] || [];
    entries.forEach(e => {
        if (e.slot <= slotIndex && (e.slot + e.duration) > slotIndex) {
            if (e.room && e.room !== 'TBA') occupied.add(e.room);
            if (e.batches) e.batches.forEach((b: any) => occupied.add(b.room));
        }
    });
  });

  const freeTheory = allTheoryRooms.filter(r => !occupied.has(r));
  const freeLabs = allLabRooms.filter(r => !occupied.has(r));
  return { freeTheory, freeLabs };
};

export const Step9Results = ({ 
  data, 
  timingData, 
  welcomeData,
  faculty = [], 
  infrastructure = { theoryRooms: [], labRooms: [], specialAssignments: {} } 
}: Step9ResultsProps) => {
  const [timetable, setTimetable] = useState<Record<string, Record<string, BackendEntry[]>>>(data.timetable || {});
  const [viewMode, setViewMode] = useState<ViewMode>('MASTER');
  const [selectedEntity, setSelectedEntity] = useState<string>(''); 

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editSlot, setEditSlot] = useState<{ div: string, day: string, slotIndex: number, timeLabel: string } | null>(null);
  const [manualEntry, setManualEntry] = useState({
    type: 'THEORY', subject: '', teacher: '', room: '', duration: 1
  });

  const divisions = useMemo(() => {
    return welcomeData.classes
      .filter(c => c.selected)
      .flatMap(c => Array.from({ length: c.divisions }, (_, i) => `${c.name}-${String.fromCharCode(65 + i)}`));
  }, [welcomeData]);

  useEffect(() => {
    setTimetable(data.timetable || {});
    if (!selectedEntity) {
        if (viewMode === 'MASTER' && divisions.length > 0) setSelectedEntity(divisions[0]);
        else if (viewMode === 'TEACHER' && faculty.length > 0) setSelectedEntity(faculty[0].name);
        else if (viewMode === 'CLASSROOM' && infrastructure.theoryRooms.length > 0) setSelectedEntity(infrastructure.theoryRooms[0]);
        else if (viewMode === 'LAB' && infrastructure.labRooms.length > 0) setSelectedEntity(infrastructure.labRooms[0]);
    }
  }, [data.timetable, viewMode, faculty, infrastructure, divisions]);

  useEffect(() => {
    if (viewMode === 'MASTER' && divisions.length > 0) setSelectedEntity(divisions[0]);
    else if (viewMode === 'TEACHER' && faculty.length > 0) setSelectedEntity(faculty[0].name);
    else if (viewMode === 'CLASSROOM' && infrastructure.theoryRooms.length > 0) setSelectedEntity(infrastructure.theoryRooms[0]);
    else if (viewMode === 'LAB' && infrastructure.labRooms.length > 0) setSelectedEntity(infrastructure.labRooms[0]);
  }, [viewMode]);

  // --- UNPLACED SUBJECTS CALCULATION ---
  const unplacedSubjects = useMemo(() => {
    const missing: { div: string, subjects: any[] }[] = [];
    divisions.forEach(div => {
        const divSchedule = timetable[div] || {};
        let placedCount = 0;
        Object.values(divSchedule).forEach(day => placedCount += day.length);
        
        if (placedCount < 15) {
            missing.push({
                div,
                subjects: [
                    { name: 'Theory Lecture', type: 'THEORY', load: 1 },
                    { name: 'Lab Session', type: 'LAB', load: 2 }
                ]
            });
        }
    });
    return missing;
  }, [timetable, divisions]);

  const timeSlots = useMemo(() => {
    const slots = [];
    if (!timingData?.startTime) return [];
    const [hours, minutes] = timingData.startTime.split(':').map(Number);
    let currentMinutes = hours * 60 + minutes;

    for (let i = 0; i < timingData.totalSlots; i++) {
      const startH = Math.floor(currentMinutes / 60);
      const startM = currentMinutes % 60;
      const endMinutes = currentMinutes + timingData.slotDuration;
      const endH = Math.floor(endMinutes / 60);
      const endM = endMinutes % 60;
      
      const formatTime = (h: number, m: number) => {
        const period = h >= 12 ? 'PM' : 'AM';
        const displayH = h > 12 ? h - 12 : h;
        return `${displayH}:${m.toString().padStart(2, '0')} ${period}`;
      };

      slots.push({
        label: `${formatTime(startH, startM)} - ${formatTime(endH, endM)}`,
        index: i
      });
      
      currentMinutes = endMinutes;
      if (i + 1 === timingData.recessAfterSlot) currentMinutes += (timingData.recessDuration || 45);
    }
    return slots;
  }, [timingData]);

  const getBackendSlotIndex = (visualIndex: number) => {
    if (visualIndex >= timingData.recessAfterSlot) {
        return visualIndex + 1;
    }
    return visualIndex;
  };

  const getDataForCell = (day: string, slotIndex: number) => {
    if (!timetable) return null;
    
    if (viewMode === 'MASTER') {
       const dayData = timetable[selectedEntity]?.[day] || [];
       return dayData.find(e => e.slot <= slotIndex && (e.slot + e.duration) > slotIndex);
    } 
    
    const searchGlobal = (predicate: (e: BackendEntry) => boolean) => {
      for (const div of Object.keys(timetable)) {
        const entries = timetable[div]?.[day] || [];
        const found = entries.find(e => 
          (e.slot <= slotIndex && (e.slot + e.duration) > slotIndex) && predicate(e)
        );
        if (found) return { ...found, displayDiv: div };
      }
      return null;
    };

    if (viewMode === 'TEACHER') {
       return searchGlobal(e => {
         if (e.teacher === selectedEntity) return true;
         if (e.type === 'ELECTIVE' && e.teacher && e.teacher.includes(selectedEntity)) return true;
         if ((e.type === 'LAB' || e.type === 'TUTORIAL' || e.type === 'MATHS_TUT') && e.batches?.some(b => b.teacher === selectedEntity)) return true;
         return false;
       });
    }

    return searchGlobal(e => {
       if (e.room === selectedEntity) return true;
       if (e.type === 'ELECTIVE' && e.room && e.room.includes(selectedEntity)) return true;
       if ((e.type === 'LAB' || e.type === 'TUTORIAL' || e.type === 'MATHS_TUT') && e.batches?.some(b => b.room === selectedEntity)) return true;
       return false;
    });
  };

  const renderCellContent = (entry: any, day: string, slotIdx: number) => {
    // 1. EMPTY SLOT RENDER (With Hints)
    if (!entry) {
        const { freeTheory, freeLabs } = getAvailableRooms(timetable, infrastructure.theoryRooms, infrastructure.labRooms, day, slotIdx);
        
        return (
            <div className="h-full w-full min-h-[100px] flex flex-col items-center justify-center relative group p-1 transition-colors hover:bg-muted/10">
               {viewMode === 'MASTER' && (
                   <>
                       <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute inset-0 flex items-center justify-center cursor-pointer rounded">
                           <Plus className="w-5 h-5 text-primary opacity-60" />
                       </div>
                       
                       {/* Available Rooms Hint - Compact & Bottom Aligned */}
                       <div className="hidden group-hover:block absolute bottom-1 right-1 left-1 text-[9px] leading-tight text-muted-foreground bg-white/95 p-1 rounded border shadow-sm text-center z-10 pointer-events-none">
                           <span className="font-bold text-primary block mb-0.5 text-[8px]">AVAIL</span>
                           <div className="truncate">T: {freeTheory.slice(0, 3).join(', ') || '-'}</div>
                           <div className="truncate">L: {freeLabs.slice(0, 2).join(', ') || '-'}</div>
                       </div>
                   </>
               )}
            </div>
        );
    }

    // 2. OCCUPIED SLOT RENDER
    const colors: Record<string, string> = {
      THEORY: "bg-blue-50/80 border-l-4 border-blue-500 text-blue-900 hover:bg-blue-100",
      LAB: "bg-orange-50/80 border-l-4 border-orange-500 text-orange-900 hover:bg-orange-100",
      MATHS_TUT: "bg-emerald-50/80 border-l-4 border-emerald-500 text-emerald-900 hover:bg-emerald-100", 
      TUTORIAL: "bg-emerald-50/80 border-l-4 border-emerald-500 text-emerald-900 hover:bg-emerald-100",
      ELECTIVE: "bg-pink-50/80 border-l-4 border-pink-500 text-pink-900 hover:bg-pink-100",
      PROJECT: "bg-purple-50/80 border-l-4 border-purple-500 text-purple-900 hover:bg-purple-100", 
    };
    
    const typeKey = (entry.type === 'MATHS_TUT' || entry.type === 'TUTORIAL') ? 'MATHS_TUT' : entry.type;
    const baseClass = `w-full h-full p-2 text-xs rounded-r-md shadow-sm transition-all flex flex-col gap-1 ${colors[typeKey] || colors.THEORY}`;

    if (entry.type === 'ELECTIVE') {
        const subjects = entry.subject ? entry.subject.split(' / ') : ['Elective'];
        const teachers = entry.teacher ? entry.teacher.split(' / ') : ['TBA'];
        const rooms = entry.room ? entry.room.split(' / ') : ['TBA'];

        return (
            <div className={baseClass}>
                <div className="flex items-center justify-between pb-1 border-b border-pink-200/50 mb-1">
                    <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider opacity-70">
                        <Layers className="w-3 h-3" /> Elective
                    </div>
                </div>
                <div className="flex flex-col gap-1.5">
                    {subjects.map((sub: string, i: number) => (
                        <div key={i} className="flex flex-col bg-white/60 p-1.5 rounded-sm border border-pink-100">
                            <span className="font-bold text-xs text-pink-950 truncate">{sub}</span>
                            <div className="flex justify-between items-center mt-0.5">
                                <span className="text-[10px] text-pink-800">{teachers[i] || 'TBA'}</span>
                                <span className="text-[10px] font-mono text-pink-700 bg-pink-100/50 px-1 rounded">{rooms[i] || 'TBA'}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if ((entry.type === 'LAB' || entry.type === 'TUTORIAL' || entry.type === 'MATHS_TUT') && viewMode === 'MASTER') {
       const isTutorial = entry.type === 'TUTORIAL' || entry.type === 'MATHS_TUT';
       const badgeColor = isTutorial ? 'bg-emerald-600' : 'bg-orange-600';
       const borderColor = isTutorial ? 'border-emerald-200/60' : 'border-orange-200/60';
       const textColor = isTutorial ? 'text-emerald-950' : 'text-orange-950';
       const subTextColor = isTutorial ? 'text-emerald-800/80' : 'text-orange-800/80';
       const headerText = isTutorial ? 'TUTORIAL' : 'LAB';

       return (
           <div className={`${baseClass} justify-start`}>
               <div className={`flex items-center justify-between mb-2 border-b ${isTutorial ? 'border-emerald-200/50' : 'border-orange-200/50'} pb-1`}>
                   <span className="font-bold text-[10px] uppercase tracking-wider opacity-80">{headerText}</span>
                   <span className="text-[9px] font-mono font-bold opacity-70 bg-white/60 px-1.5 py-0.5 rounded shadow-sm">{entry.duration === 1 ? '1h' : '2h'}</span>
               </div>
               <div className="flex flex-col gap-1.5">
                   {entry.batches?.map((b: any, i: number) => (
                       <div key={i} className={`flex items-center gap-2 bg-white/70 p-1.5 rounded border ${borderColor} shadow-sm`}>
                           <span className={`${badgeColor} text-white text-[10px] font-bold px-1.5 py-1 rounded min-w-[28px] text-center shadow-sm h-full flex items-center justify-center`}>
                               {b.batch || `B${i+1}`}
                           </span>
                           <div className="flex flex-col leading-none flex-1 min-w-0 gap-0.5">
                               <span className={`font-bold text-[11px] ${textColor} truncate`} title={b.subject}>{b.subject}</span>
                               <div className={`flex justify-between items-center w-full ${subTextColor}`}>
                                   <span className="text-[10px] truncate max-w-[60px]">{b.teacher}</span>
                                   <span className="font-mono text-[10px] bg-white/50 px-1 rounded">{b.room}</span>
                               </div>
                           </div>
                       </div>
                   ))}
               </div>
           </div>
       );
    }

    return (
        <div className={baseClass}>
            <div className="flex-1 flex flex-col justify-center">
                <div className="flex justify-between items-start">
                    <div className="font-bold text-sm leading-tight line-clamp-2 mb-1">{entry.subject}</div>
                    {entry.type === 'PROJECT' && <Briefcase className="w-3 h-3 opacity-50 flex-shrink-0" />}
                </div>
                <div className="flex items-center gap-1.5 opacity-90 text-xs">
                    <User className="w-3 h-3" />
                    <span className="truncate font-medium">{viewMode === 'TEACHER' ? entry.displayDiv : entry.teacher}</span>
                </div>
            </div>
            <div className="mt-auto pt-2 border-t border-black/5 flex items-center justify-between opacity-80">
                <div className="flex items-center gap-1 font-mono text-[10px]">
                    <MapPin className="w-3 h-3" />
                    <span>{entry.room}</span>
                </div>
                <span className="text-[9px] uppercase tracking-wider opacity-60 font-bold">{entry.type.substring(0,3)}</span>
            </div>
        </div>
    );
  };

  const handleCellClick = (div: string, day: string, slotIndex: number, timeLabel: string, existingEntry: any) => {
    if (existingEntry) {
        toast({ description: "Slot occupied. Delete to edit." });
        return;
    }
    setEditSlot({ div, day, slotIndex, timeLabel });
    setManualEntry({ type: 'THEORY', subject: '', teacher: '', room: '', duration: 1 });
    setIsDialogOpen(true);
  };

  const saveManualEntry = () => {
    if (!editSlot || !manualEntry.subject) return;
    const { div, day, slotIndex } = editSlot;
    const newTimetable = JSON.parse(JSON.stringify(timetable));
    if (!newTimetable[div]) newTimetable[div] = {};
    if (!newTimetable[div][day]) newTimetable[div][day] = [];

    const newRecord: BackendEntry = {
      slot: slotIndex,
      duration: manualEntry.duration,
      type: manualEntry.type as any,
      subject: manualEntry.subject,
      teacher: manualEntry.type === 'PROJECT' ? 'TBA' : (manualEntry.teacher || 'TBA'), // Hide teacher for Project
      room: manualEntry.room || 'TBA'
    };

    newTimetable[div][day].push(newRecord);
    setTimetable(newTimetable);
    setIsDialogOpen(false);
    toast({ title: "Entry Added" });
  };

  return (
    <div className="form-section animate-slide-up pb-10">
      {/* Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4 bg-card p-4 rounded-xl shadow-sm border border-border sticky top-0 z-30">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
            {viewMode === 'TEACHER' ? <User className="w-6 h-6 text-primary" /> : 
             viewMode === 'LAB' ? <FlaskConical className="w-6 h-6 text-primary" /> :
             <BookOpen className="w-6 h-6 text-primary" />}
          </div>
          <div>
            <h2 className="text-xl font-display font-bold">Timetable View</h2>
            <div className="flex gap-2 mt-1">
                {['MASTER', 'TEACHER', 'CLASSROOM', 'LAB'].map((m) => (
                    <button type="button" key={m} onClick={() => setViewMode(m as any)}
                        className={`text-xs px-3 py-1 rounded-full transition-colors border ${viewMode === m ? 'bg-primary text-white border-primary' : 'bg-background hover:bg-muted border-border'}`}>
                        {m}
                    </button>
                ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3 items-center">
            <Select value={selectedEntity} onValueChange={setSelectedEntity}>
                <SelectTrigger className="w-[200px] h-9 border-primary/20 bg-white">
                    <SelectValue placeholder="Select..." />
                </SelectTrigger>
                <SelectContent>
                    {viewMode === 'MASTER' && divisions.map(d => <SelectItem key={d} value={d}>{d} Division</SelectItem>)}
                    {viewMode === 'TEACHER' && faculty.map(f => <SelectItem key={f.id} value={f.name}>{f.name}</SelectItem>)}
                    {viewMode === 'CLASSROOM' && infrastructure.theoryRooms.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                    {viewMode === 'LAB' && infrastructure.labRooms.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                </SelectContent>
            </Select>
            <Button type="button" variant="outline" className="gap-2 h-9" onClick={() => toast({title: "Download Started"})}>
                <Download className="w-4 h-4" /> PDF
            </Button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="overflow-x-auto rounded-xl border border-border shadow-md bg-white">
        <table className="w-full min-w-[1200px] border-collapse">
            <thead>
                <tr className="bg-muted/30 border-b border-border h-14">
                    <th className="p-3 w-28 text-center font-bold text-muted-foreground uppercase text-xs tracking-wider border-r border-border sticky left-0 bg-white z-20 shadow-[1px_0_0_0_rgba(0,0,0,0.1)]">Day</th>
                    {timeSlots.map((slot, i) => (
                        <Fragment key={i}>
                            {i === timingData.recessAfterSlot && (
                                <th className="w-10 bg-yellow-50/50 border-r border-yellow-200/50 text-center relative p-0">
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="-rotate-90 text-[10px] font-bold text-yellow-600/70 tracking-widest uppercase whitespace-nowrap">Recess</span>
                                    </div>
                                </th>
                            )}
                            <th className="p-2 text-center border-r border-border last:border-r-0 min-w-[160px]">
                                <div className="flex flex-col items-center justify-center">
                                    <span className="text-[10px] text-muted-foreground font-mono bg-muted/50 px-2 py-0.5 rounded mb-1">{slot.label}</span>
                                    <span className="text-xs font-bold text-foreground">Slot {i + 1}</span>
                                </div>
                            </th>
                        </Fragment>
                    ))}
                </tr>
            </thead>
            <tbody>
                {timingData.workingDays.map((day) => (
                    <tr key={day} className="border-b border-border last:border-b-0">
                        <td className="p-4 font-bold text-sm text-foreground border-r border-border sticky left-0 bg-white z-10 shadow-[1px_0_0_0_rgba(0,0,0,0.1)] text-center">{day}</td>
                        {timeSlots.map((slot, i) => {
                            const realSlotIdx = getBackendSlotIndex(i);
                            const entry = getDataForCell(day, realSlotIdx);
                            const isStart = entry && entry.slot === realSlotIdx;
                            const isContinuation = entry && entry.slot < realSlotIdx;

                            return (
                                <Fragment key={i}>
                                    {i === timingData.recessAfterSlot && (
                                        <td className="bg-yellow-50/20 border-r border-yellow-100"></td>
                                    )}
                                    {!isContinuation ? (
                                        <td 
                                            colSpan={isStart ? entry.duration : 1}
                                            className="p-1 min-h-[100px] h-auto border-r border-border align-top relative group transition-colors hover:bg-muted/5"
                                            onClick={() => !entry && handleCellClick(selectedEntity, day, realSlotIdx, slot.label, entry)}
                                        >
                                            {renderCellContent(entry, day, realSlotIdx)}
                                        </td>
                                    ) : null}
                                </Fragment>
                            );
                        })}
                    </tr>
                ))}
            </tbody>
        </table>
      </div>

      {/* Unplaced Items Table */}
      {viewMode === 'MASTER' && unplacedSubjects.length > 0 && (
          <Card className="mt-8 border-dashed border-2 border-orange-200 bg-orange-50/30">
              <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-bold text-orange-800 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" /> Pending Allocations
                  </CardTitle>
              </CardHeader>
              <CardContent>
                  <Table>
                      <TableHeader>
                          <TableRow>
                              <TableHead className="w-[100px]">Division</TableHead>
                              <TableHead>Type</TableHead>
                              <TableHead>Subject</TableHead>
                              <TableHead className="text-right">Needed Load</TableHead>
                          </TableRow>
                      </TableHeader>
                      <TableBody>
                          {unplacedSubjects.flatMap((item, i) => 
                              item.subjects.map((sub, j) => (
                                  <TableRow key={`${i}-${j}`} className="hover:bg-orange-100/50">
                                      <TableCell className="font-medium text-orange-900">{item.div}</TableCell>
                                      <TableCell><Badge variant="outline" className="bg-white border-orange-300 text-orange-700">{sub.type}</Badge></TableCell>
                                      <TableCell className="text-orange-800">{sub.name}</TableCell>
                                      <TableCell className="text-right font-mono text-orange-900">{sub.load}h</TableCell>
                                  </TableRow>
                              ))
                          )}
                      </TableBody>
                  </Table>
              </CardContent>
          </Card>
      )}

      {/* Manual Entry Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Add Entry Manually</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label className="text-right">Type</Label>
                    <Select value={manualEntry.type} onValueChange={(v) => setManualEntry({...manualEntry, type: v})}>
                        <SelectTrigger className="col-span-3"><SelectValue /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="THEORY">Theory</SelectItem>
                            <SelectItem value="LAB">Lab</SelectItem>
                            <SelectItem value="PROJECT">Project</SelectItem>
                            <SelectItem value="TUTORIAL">Tutorial</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label className="text-right">Subject</Label>
                    <Input className="col-span-3" value={manualEntry.subject} onChange={e => setManualEntry({...manualEntry, subject: e.target.value})} />
                </div>
                {manualEntry.type !== 'PROJECT' && (
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Teacher</Label>
                        <Input className="col-span-3" value={manualEntry.teacher} onChange={e => setManualEntry({...manualEntry, teacher: e.target.value})} />
                    </div>
                )}
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label className="text-right">Room</Label>
                    <Input className="col-span-3" value={manualEntry.room} onChange={e => setManualEntry({...manualEntry, room: e.target.value})} />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                    <Label className="text-right">Duration (Slots)</Label>
                    <Input type="number" className="col-span-3" value={manualEntry.duration} onChange={e => setManualEntry({...manualEntry, duration: parseInt(e.target.value)})} min={1} max={2} />
                </div>
            </div>
            <DialogFooter>
                <Button type="button" onClick={() => setIsDialogOpen(false)} variant="outline">Cancel</Button>
                <Button type="button" onClick={saveManualEntry}>Save</Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};