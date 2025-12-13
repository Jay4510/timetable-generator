from rest_framework import serializers
from .models import Teacher, Year, Division, Room, Lab, Subject, TimeSlot, Session, TimetableVersion


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'


class DivisionSerializer(serializers.ModelSerializer):
    year_name = serializers.CharField(source='year.name', read_only=True)
    
    class Meta:
        model = Division
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    year_name = serializers.CharField(source='year.name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    room_name = serializers.SerializerMethodField()
    lab_name = serializers.CharField(source='lab.name', allow_null=True, read_only=True)
    timeslot_info = serializers.SerializerMethodField()
    year_division = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 
            'subject_name', 
            'teacher_name', 
            'room_name', 
            'lab_name', 
            'timeslot_info',
            'batch_number',
            'year_division'
        ]

    def get_room_name(self, obj):
        """Return room name, handling both regular rooms and lab rooms"""
        if obj.room:
            return obj.room.name
        elif obj.lab:
            return obj.lab.name
        return None

    def get_timeslot_info(self, obj):
        return f"{obj.timeslot.day} {obj.timeslot.start_time.strftime('%H:%M')}-{obj.timeslot.end_time.strftime('%H:%M')}"

    def get_year_division(self, obj):
        return f"{obj.subject.year.name} {obj.subject.division.name}"


class TimetableVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableVersion
        fields = '__all__'