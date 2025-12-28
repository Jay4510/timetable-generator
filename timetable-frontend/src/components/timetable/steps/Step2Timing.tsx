import { TimingData } from '@/types/timetable';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Clock, Coffee } from 'lucide-react';

interface Step2TimingProps {
  data: TimingData;
  onUpdate: (data: TimingData) => void;
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export const Step2Timing = ({ data, onUpdate }: Step2TimingProps) => {
  const handleDayToggle = (day: string, checked: boolean) => {
    const updatedDays = checked
      ? [...data.workingDays, day]
      : data.workingDays.filter((d) => d !== day);
    onUpdate({ ...data, workingDays: updatedDays });
  };

  const calculateTime = (startStr: string, minutesToAdd: number) => {
    if (!startStr) return '00:00';
    const [h, m] = startStr.split(':').map(Number);
    const totalMins = h * 60 + m + minutesToAdd;
    const newH = Math.floor(totalMins / 60);
    const newM = totalMins % 60;
    const displayH = newH > 12 ? newH - 12 : newH;
    const ampm = newH >= 12 ? 'PM' : 'AM';
    return `${displayH}:${newM.toString().padStart(2, '0')} ${ampm}`;
  };

  const handleNumberChange = (field: keyof TimingData, value: string) => {
    const num = parseInt(value);
    if (isNaN(num)) onUpdate({ ...data, [field]: 0 }); 
    else onUpdate({ ...data, [field]: num });
  };

  return (
    <div className="form-section animate-slide-up">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-full gradient-navy flex items-center justify-center">
          <Clock className="w-6 h-6 text-gold" />
        </div>
        <div>
          <h2 className="section-title mb-0">Timing & Grid Configuration</h2>
          <p className="text-muted-foreground text-sm">Set up your daily schedule parameters</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        
        <div className="space-y-2">
          <Label className="input-label">College Start Time</Label>
          <Input
            type="time"
            value={data.startTime}
            onChange={(e) => onUpdate({ ...data, startTime: e.target.value })}
            className="h-12"
          />
        </div>

        <div className="space-y-2">
          <Label className="input-label">Lecture Duration (mins)</Label>
          <Select
            value={data.slotDuration.toString()}
            onValueChange={(value) => onUpdate({ ...data, slotDuration: parseInt(value) })}
          >
            <SelectTrigger className="h-12"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[45, 50, 60, 90].map(d => <SelectItem key={d} value={d.toString()}>{d} mins</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        {/* FIXED RECESS SELECTOR */}
        <div className="space-y-2">
          <Label className="input-label">Recess Starts After</Label>
          <Select
            value={data.recessAfterSlot.toString()}
            onValueChange={(value) => onUpdate({ ...data, recessAfterSlot: parseInt(value) })}
          >
            <SelectTrigger className="h-12"><SelectValue /></SelectTrigger>
            <SelectContent>
              {[3, 4, 5, 6].map((slot) => {
                const breakStart = calculateTime(data.startTime, slot * data.slotDuration);
                return (
                  <SelectItem key={slot} value={slot.toString()}>
                    {slot} Lectures (Break at {breakStart})
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label className="input-label">Recess Duration (mins)</Label>
          <div className="relative">
            <Input
              type="number"
              min={15}
              max={120}
              step={5}
              value={data.recessDuration || ''}
              onChange={(e) => handleNumberChange('recessDuration', e.target.value)}
              className="h-12 pl-10"
              placeholder="45"
            />
            <Coffee className="w-4 h-4 text-muted-foreground absolute left-3 top-4" />
          </div>
        </div>
      </div>

      <div className="mt-6">
        <div className="space-y-2 max-w-[200px]">
          <Label className="input-label">Total Grid Slots</Label>
          <div className="text-xs text-muted-foreground mb-1">(Lectures + 1 Recess Slot)</div>
          <Input
            type="number"
            min={5}
            max={15}
            value={data.totalSlots || ''} 
            onChange={(e) => handleNumberChange('totalSlots', e.target.value)}
            className="h-12"
            placeholder="e.g. 9"
          />
        </div>
      </div>

      <div className="mt-8">
        <Label className="input-label mb-4 block">Working Days</Label>
        <div className="flex flex-wrap gap-3">
          {DAYS.map((day) => (
            <label
              key={day}
              className={`
                flex items-center gap-2 px-4 py-3 rounded-lg border-2 cursor-pointer transition-all
                ${data.workingDays.includes(day)
                  ? 'border-accent bg-accent/10 text-foreground'
                  : 'border-border bg-card hover:border-accent/50 text-muted-foreground'
                }
              `}
            >
              <Checkbox
                checked={data.workingDays.includes(day)}
                onCheckedChange={(checked) => handleDayToggle(day, checked as boolean)}
              />
              <span className="font-medium">{day}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Visual Preview - Helps verify index */}
      <div className="mt-8">
        <Label className="input-label mb-2 block">Day Structure Preview</Label>
        <div className="flex w-full h-12 rounded-lg overflow-hidden border border-border">
          {Array.from({ length: data.totalSlots }).map((_, i) => {
             const isRecess = i === data.recessAfterSlot;
             return (
               <div 
                 key={i} 
                 className={`flex-1 flex items-center justify-center text-xs font-mono border-r last:border-r-0 border-white/20
                   ${isRecess ? 'bg-yellow-100 text-yellow-700 font-bold' : 'bg-accent/10 text-muted-foreground'}
                 `}
                 title={isRecess ? "Recess" : `Slot ${i}`}
               >
                 {isRecess ? "R" : (i < data.recessAfterSlot ? i + 1 : i)}
               </div>
             )
          })}
        </div>
        <div className="flex justify-between text-xs text-muted-foreground mt-2 px-1">
            <span>{calculateTime(data.startTime, 0)}</span>
            <span>{calculateTime(data.startTime, (data.recessAfterSlot * data.slotDuration))} (Break)</span>
            <span>{calculateTime(data.startTime, ((data.totalSlots - 1) * data.slotDuration) + (data.recessDuration || 0))}</span>
        </div>
      </div>
    </div>
  );
};