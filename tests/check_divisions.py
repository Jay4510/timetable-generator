#!/usr/bin/env python3

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_generator.settings')
django.setup()

from timetable_app.models import Division, Year

def check_and_create_divisions():
    """Check if divisions exist and create them if they don't"""
    
    print("Checking divisions in database...")
    
    # Check existing divisions
    divisions = Division.objects.all()
    print(f"Found {divisions.count()} divisions:")
    for div in divisions:
        print(f"  - {div.year.name} {div.name} (ID: {div.id})")
    
    # If no divisions, create some
    if divisions.count() == 0:
        print("\nNo divisions found. Creating sample divisions...")
        
        # Check if years exist
        years = Year.objects.all()
        print(f"Found {years.count()} years:")
        for year in years:
            print(f"  - {year.name} (ID: {year.id})")
        
        if years.count() == 0:
            print("Creating sample years...")
            se_year = Year.objects.create(name="SE", description="Second Year Engineering")
            te_year = Year.objects.create(name="TE", description="Third Year Engineering") 
            be_year = Year.objects.create(name="BE", description="Final Year Engineering")
            print(f"Created years: {se_year.name}, {te_year.name}, {be_year.name}")
        else:
            se_year = years.filter(name="SE").first()
            te_year = years.filter(name="TE").first()
            be_year = years.filter(name="BE").first()
        
        # Create divisions
        divisions_to_create = [
            (se_year, "A", 3),
            (se_year, "B", 3),
            (te_year, "A", 3),
            (te_year, "B", 3),
            (be_year, "A", 3),
            (be_year, "B", 3),
        ]
        
        for year, div_name, batches in divisions_to_create:
            if year:
                division = Division.objects.create(
                    year=year,
                    name=div_name,
                    num_batches=batches
                )
                print(f"Created division: {year.name} {div_name} with {batches} batches")
    
    # Final check
    print(f"\nFinal division count: {Division.objects.count()}")
    
    # Test the API endpoint logic
    print("\nTesting API endpoint logic...")
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
    
    print(f"API would return: {division_data}")
    return division_data

if __name__ == "__main__":
    check_and_create_divisions()
