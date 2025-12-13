#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_generator.settings')
django.setup()

from timetable_app.models import Division, Year

def create_divisions():
    """Create divisions if they don't exist"""
    
    print("=== CREATING DIVISIONS ===")
    
    # Check existing divisions
    existing_divisions = Division.objects.count()
    print(f"Existing divisions: {existing_divisions}")
    
    if existing_divisions > 0:
        print("Divisions already exist:")
        for div in Division.objects.select_related('year').all():
            print(f"  - {div.year.name} {div.name} (ID: {div.id}, Batches: {div.num_batches})")
        return
    
    # Check if years exist
    years = Year.objects.all()
    print(f"Existing years: {years.count()}")
    
    if years.count() == 0:
        print("Creating years...")
        se_year = Year.objects.create(name="SE", description="Second Year Engineering")
        te_year = Year.objects.create(name="TE", description="Third Year Engineering") 
        be_year = Year.objects.create(name="BE", description="Final Year Engineering")
        print(f"Created years: {se_year.name}, {te_year.name}, {be_year.name}")
    else:
        se_year = years.filter(name="SE").first()
        te_year = years.filter(name="TE").first()
        be_year = years.filter(name="BE").first()
        
        # Create missing years if needed
        if not se_year:
            se_year = Year.objects.create(name="SE", description="Second Year Engineering")
        if not te_year:
            te_year = Year.objects.create(name="TE", description="Third Year Engineering")
        if not be_year:
            be_year = Year.objects.create(name="BE", description="Final Year Engineering")
    
    # Create divisions
    divisions_to_create = [
        (se_year, "A", 3),
        (se_year, "B", 3),
        (te_year, "A", 3),
        (te_year, "B", 3),
        (be_year, "A", 3),
        (be_year, "B", 3),
    ]
    
    print("Creating divisions...")
    for year, div_name, batches in divisions_to_create:
        if year:
            division, created = Division.objects.get_or_create(
                year=year,
                name=div_name,
                defaults={'num_batches': batches}
            )
            if created:
                print(f"✓ Created division: {year.name} {div_name} with {batches} batches")
            else:
                print(f"- Division already exists: {year.name} {div_name}")
    
    # Final verification
    final_count = Division.objects.count()
    print(f"\nFinal division count: {final_count}")
    
    print("\n=== TESTING API RESPONSE ===")
    divisions = Division.objects.select_related('year').all()
    division_data = []
    
    for division in divisions:
        division_data.append({
            'id': division.id,
            'name': division.name,
            'year_name': division.year.name,
            'key': f"{division.year.name}_{division.name}",
            'display_name': f"{division.year.name} {division.name}",
            'num_batches': division.num_batches
        })
    
    print("API response would be:")
    import json
    print(json.dumps(division_data, indent=2))
    
    return division_data

if __name__ == "__main__":
    create_divisions()
