import { useState } from 'react';
import { CurriculumData, LabSubject, TheorySubject } from '@/types/timetable';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { BookOpen, Plus, Trash2, Beaker, Clock, Wand2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface Step3CurriculumProps {
  data: CurriculumData;
  onUpdate: (data: CurriculumData) => void;
}

export const Step3Curriculum = ({ data, onUpdate }: Step3CurriculumProps) => {
  const [activeTab, setActiveTab] = useState<'theory' | 'labs'>('theory');

  // --- DEFAULT DATA LOADER (Short Codes Only) ---
  const loadDefaults = () => {
    
    // 1. THEORY SUBJECTS
    const defaultTheory: TheorySubject[] = [
      // --- SE ---
      { id: 'se-cnnd', name: 'CNND', code: 'CNND', year: 'SE', weeklyLoad: 3, type: 'Theory' },
      { id: 'se-bmd', name: 'BMD', code: 'BMD', year: 'SE', weeklyLoad: 2, type: 'Theory' },
      { id: 'se-dt', name: 'DT', code: 'DT', year: 'SE', weeklyLoad: 2, type: 'Theory' },
      { id: 'se-mdm', name: 'MDM', code: 'MDM', year: 'SE', weeklyLoad: 3, type: 'Theory' },
      { id: 'se-pp', name: 'PP', code: 'PP', year: 'SE', weeklyLoad: 2, type: 'Theory' },
      { id: 'se-os', name: 'OS', code: 'OS', year: 'SE', weeklyLoad: 3, type: 'Theory' },
      { id: 'se-oe', name: 'OE', code: 'OE', year: 'SE', weeklyLoad: 2, type: 'Theory' },
      { id: 'se-math', name: 'Maths-4', code: 'Maths-4', year: 'SE', weeklyLoad: 2, type: 'Theory' },

      // --- TE ---
      { id: 'te-dmbi', name: 'DMBI', code: 'DMBI', year: 'TE', weeklyLoad: 3, type: 'Theory' },
      { id: 'te-aids', name: 'AIDS', code: 'AIDS', year: 'TE', weeklyLoad: 3, type: 'Theory' },
      { id: 'te-webx', name: 'WebX', code: 'WebX', year: 'TE', weeklyLoad: 3, type: 'Theory' },
      { id: 'te-wt', name: 'WT', code: 'WT', year: 'TE', weeklyLoad: 3, type: 'Theory' },
      // TE Electives
      { id: 'te-ehf', name: 'EHF', code: 'EHF', year: 'TE', weeklyLoad: 3, type: 'Elective' },
      { id: 'te-git', name: 'GIT', code: 'GIT', year: 'TE', weeklyLoad: 3, type: 'Elective' },

      // --- BE ---
      { id: 'be-bdlt', name: 'BDLT', code: 'BDLT', year: 'BE', weeklyLoad: 3, type: 'Theory' },
      { id: 'be-bda', name: 'BDA', code: 'BDA', year: 'BE', weeklyLoad: 3, type: 'Theory' },
      { id: 'be-pm', name: 'PM', code: 'PM', year: 'BE', weeklyLoad: 3, type: 'Theory' },
      // BE Electives
      { id: 'be-uid', name: 'UID', code: 'UID', year: 'BE', weeklyLoad: 3, type: 'Elective' },
      { id: 'be-ccs', name: 'CCS', code: 'CCS', year: 'BE', weeklyLoad: 3, type: 'Elective' },
    ];

    // 2. LABS & TUTORIALS
    const defaultLabs: LabSubject[] = [
      // --- SE Labs ---
      { id: 'se-ndl', name: 'NDL', code: 'NDL', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'se-ul', name: 'UL', code: 'UL', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'se-lab-dt', name: 'DT', code: 'DT', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'se-lab-bmd', name: 'BMD', code: 'BMD', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'se-lab-pp', name: 'PP', code: 'PP', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'se-lab-mdm', name: 'MDM', code: 'MDM', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      // SE Tutorial
      { id: 'se-math-tut', name: 'Maths Tut', code: 'Maths Tut', year: 'SE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 1, isSpecial: true, type: 'Tutorial' },

      // --- TE Labs ---
      { id: 'te-bil', name: 'BIL', code: 'BIL', year: 'TE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'te-wl', name: 'WL', code: 'WL', year: 'TE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'te-sl', name: 'SL', code: 'SL', year: 'TE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'te-dspyl', name: 'DSPYL', code: 'DSPYL', year: 'TE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'te-mpwa', name: 'MPWA', code: 'MPWA', year: 'TE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },

      // --- BE Labs ---
      { id: 'be-bdlt-lab', name: 'BDLT Lab', code: 'BDLT Lab', year: 'BE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
      { id: 'be-ccl', name: 'CCL', code: 'CCL', year: 'BE', batchCount: 3, sessionsPerWeek: 1, durationPerSession: 2, isSpecial: false, type: 'Lab' },
    ];

    onUpdate({
      theorySubjects: defaultTheory,
      labSubjects: defaultLabs
    });

    toast({
      title: "Data Loaded",
      description: "Subjects loaded with Short Codes.",
    });
  };

  const addTheorySubject = () => {
    const newSubject: TheorySubject = {
      id: crypto.randomUUID(),
      name: '',
      code: '',
      year: 'SE',
      weeklyLoad: 3,
      type: 'Theory',
    };
    onUpdate({
      ...data,
      theorySubjects: [...data.theorySubjects, newSubject],
    });
  };

  const addLabSubject = () => {
    const newSubject: LabSubject = {
      id: crypto.randomUUID(),
      name: '',
      code: '',
      year: 'SE',
      batchCount: 3,
      sessionsPerWeek: 1,
      durationPerSession: 2, // Default 2 hours
      isSpecial: false,
      type: 'Lab', // Default
    };
    onUpdate({
      ...data,
      labSubjects: [...data.labSubjects, newSubject],
    });
  };

  const updateTheorySubject = (id: string, field: keyof TheorySubject, value: any) => {
    const updated = data.theorySubjects.map((sub) =>
      sub.id === id ? { ...sub, [field]: value } : sub
    );
    onUpdate({ ...data, theorySubjects: updated });
  };

  const updateLabSubject = (id: string, field: keyof LabSubject, value: any) => {
    const updated = data.labSubjects.map((sub) =>
      sub.id === id ? { ...sub, [field]: value } : sub
    );
    onUpdate({ ...data, labSubjects: updated });
  };

  const removeTheorySubject = (id: string) => {
    onUpdate({ ...data, theorySubjects: data.theorySubjects.filter((s) => s.id !== id) });
  };

  const removeLabSubject = (id: string) => {
    onUpdate({ ...data, labSubjects: data.labSubjects.filter((s) => s.id !== id) });
  };

  return (
    <div className="form-section animate-slide-up">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full gradient-navy flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-gold" />
          </div>
          <div>
            <h2 className="section-title mb-0">Curriculum Setup</h2>
            <p className="text-muted-foreground text-sm">Define subjects, electives, and labs/tutorials</p>
          </div>
        </div>
        <Button onClick={loadDefaults} variant="outline" className="gap-2 border-purple-200 hover:bg-purple-50 text-purple-700">
          <Wand2 className="w-4 h-4" /> Load Defaults
        </Button>
      </div>

      <div className="flex gap-2 mb-6 border-b border-border">
        <button
          onClick={() => setActiveTab('theory')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'theory' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Theory & Electives
        </button>
        <button
          onClick={() => setActiveTab('labs')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'labs' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Labs & Tutorials
        </button>
      </div>

      <div className="space-y-4">
        {activeTab === 'theory' ? (
          <>
            {data.theorySubjects.map((subject) => (
              <Card key={subject.id} className={`p-4 border-l-4 ${subject.type === 'Elective' ? 'border-l-purple-500 bg-purple-50/30' : 'border-l-blue-500'}`}>
                <div className="grid gap-4 md:grid-cols-12 items-end">
                  <div className="md:col-span-2">
                    <Label className="text-xs">Class</Label>
                    <Select value={subject.year} onValueChange={(val) => updateTheorySubject(subject.id, 'year', val)}>
                      <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="SE">SE</SelectItem>
                        <SelectItem value="TE">TE</SelectItem>
                        <SelectItem value="BE">BE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="md:col-span-2">
                    <Label className="text-xs">Type</Label>
                    <Select value={subject.type} onValueChange={(val) => updateTheorySubject(subject.id, 'type', val)}>
                      <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Theory">Theory</SelectItem>
                        <SelectItem value="Elective">Elective</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="md:col-span-3">
                    <Label className="text-xs">Subject Name</Label>
                    <Input value={subject.name} onChange={(e) => updateTheorySubject(subject.id, 'name', e.target.value)} className="h-9" />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="text-xs">Code</Label>
                    <Input value={subject.code} onChange={(e) => updateTheorySubject(subject.id, 'code', e.target.value)} className="h-9" />
                  </div>
                  <div className="md:col-span-2">
                    <Label className="text-xs">Hrs/Week</Label>
                    <Input type="number" min={1} max={10} value={subject.weeklyLoad} onChange={(e) => updateTheorySubject(subject.id, 'weeklyLoad', parseInt(e.target.value))} className="h-9" />
                  </div>
                  <div className="md:col-span-1 flex justify-end">
                    <Button variant="ghost" size="icon" onClick={() => removeTheorySubject(subject.id)} className="text-destructive h-9 w-9">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
            <Button onClick={addTheorySubject} className="w-full gap-2 border-dashed" variant="outline"><Plus className="w-4 h-4" /> Add Theory</Button>
          </>
        ) : (
          <>
            {data.labSubjects.map((subject) => (
              <Card key={subject.id} className={`p-4 border-l-4 ${subject.type === 'Tutorial' ? 'border-l-green-500 bg-green-50/30' : 'border-l-orange-500'}`}>
                <div className="grid gap-4 md:grid-cols-12 items-end">
                  {/* Class Selection */}
                  <div className="md:col-span-1">
                    <Label className="text-xs">Class</Label>
                    <Select value={subject.year} onValueChange={(val) => updateLabSubject(subject.id, 'year', val)}>
                      <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="SE">SE</SelectItem>
                        <SelectItem value="TE">TE</SelectItem>
                        <SelectItem value="BE">BE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Type Selection: Lab vs Tutorial */}
                  <div className="md:col-span-2">
                    <Label className="text-xs">Type</Label>
                    <Select value={subject.type} onValueChange={(val) => updateLabSubject(subject.id, 'type', val)}>
                      <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Lab">Lab</SelectItem>
                        <SelectItem value="Tutorial">Tutorial</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Name */}
                  <div className="md:col-span-3">
                    <Label className="text-xs">Name</Label>
                    <Input value={subject.name} onChange={(e) => updateLabSubject(subject.id, 'name', e.target.value)} className="h-9" placeholder={subject.type === 'Lab' ? 'DBMS Lab' : 'Maths Tut'} />
                  </div>

                  {/* Sessions Per Week */}
                  <div className="md:col-span-1">
                    <Label className="text-xs">Sessions</Label>
                    <Input type="number" min={1} value={subject.sessionsPerWeek} onChange={(e) => updateLabSubject(subject.id, 'sessionsPerWeek', parseInt(e.target.value))} className="h-9" />
                  </div>

                  {/* Duration (Hours) */}
                  <div className="md:col-span-2">
                    <Label className="text-xs flex items-center gap-1"><Clock className="w-3 h-3"/> Hrs/Sess</Label>
                    <Input type="number" min={1} max={4} value={subject.durationPerSession} onChange={(e) => updateLabSubject(subject.id, 'durationPerSession', parseInt(e.target.value))} className="h-9" />
                  </div>

                  {/* Special Room Checkbox */}
                  <div className="md:col-span-2 flex items-center gap-2 h-9 border rounded px-2 bg-background/50">
                    <Checkbox id={`special-${subject.id}`} checked={subject.isSpecial} onCheckedChange={(c) => updateLabSubject(subject.id, 'isSpecial', c as boolean)} />
                    <Label htmlFor={`special-${subject.id}`} className="text-xs cursor-pointer truncate">Special Room</Label>
                  </div>

                  {/* Delete */}
                  <div className="md:col-span-1 flex justify-end">
                    <Button variant="ghost" size="icon" onClick={() => removeLabSubject(subject.id)} className="text-destructive h-9 w-9">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
            <Button onClick={addLabSubject} className="w-full gap-2 border-dashed" variant="outline"><Beaker className="w-4 h-4" /> Add Lab / Tutorial</Button>
          </>
        )}
      </div>
    </div>
  );
};