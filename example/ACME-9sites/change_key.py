#!/usr/bin/env python3
"""
Script to update idPoint keys in MasterInput.db
Changes idPoint from original values to latitudeDD_longitudeDD format
Updates all foreign key references in related tables
"""

import sqlite3
from pathlib import Path
import sys

def update_database_keys(db_path: str = "MasterInput.db"):
    """
    Update idPoint keys in MasterInput.db and all related tables
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"Connected to {db_path}")
        
        # Step 1: Create backup column "name" in Coordinates table
        print("\n1. Creating 'name' column in Coordinates table...")
        try:
            cursor.execute("ALTER TABLE Coordinates ADD COLUMN name TEXT")
            print("   Column 'name' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'name' already exists")
            else:
                raise
        
        # Step 2: Copy current idPoint values to name column
        print("\n2. Copying idPoint values to 'name' column...")
        cursor.execute("UPDATE Coordinates SET name = idPoint")
        print(f"   Copied {cursor.rowcount} values")
        
        # Step 3: Get mapping of old idPoint to new format (latitudeDD_longitudeDD)
        print("\n3. Creating idPoint mapping...")
        cursor.execute("SELECT idPoint, latitudeDD, longitudeDD FROM Coordinates")
        rows = cursor.fetchall()
        
        mapping = {}
        for old_id, lat, lon in rows:
            new_id = f"{lat}_{lon}"
            mapping[old_id] = new_id
            print(f"   {old_id} -> {new_id}")
        
        # Step 4: Update foreign keys in related tables
        print("\n4. Updating foreign keys in related tables...")
        
        # Update Coordinate_years table
        print("   Updating Coordinate_years.idPoint...")
        cursor.execute("""
            UPDATE Coordinate_years 
            SET idPoint = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = Coordinate_years.idPoint
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = Coordinate_years.idPoint
            )
        """)
        print(f"      Updated {cursor.rowcount} rows")
        
        # Update Soil table
        print("   Updating Soil.idPoint...")
        cursor.execute("""
            UPDATE Soil 
            SET idPoint = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = Soil.idPoint
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = Soil.idPoint
            )
        """)
        print(f"      Updated {cursor.rowcount} rows")
        
        # Update RAClimateD table
        print("   Updating RAClimateD.idPoint...")
        cursor.execute("""
            UPDATE RAClimateD 
            SET idPoint = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = RAClimateD.idPoint
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = RAClimateD.idPoint
            )
        """)
        print(f"      Updated {cursor.rowcount} rows")
        
        # Update SimUnitList table - idPoint
        print("   Updating SimUnitList.idPoint...")
        cursor.execute("""
            UPDATE SimUnitList 
            SET idPoint = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = SimUnitList.idPoint
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = SimUnitList.idPoint
            )
        """)
        print(f"      Updated {cursor.rowcount} rows")
        
        # Update SimUnitList table - idSoil
        print("   Updating SimUnitList.idSoil...")
        cursor.execute("""
            UPDATE SimUnitList 
            SET idSoil = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = SimUnitList.idSoil
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = SimUnitList.idSoil
            )
        """)
        print(f"      Updated {cursor.rowcount} rows")
        
        # Step 5: Add soil texture columns to Soil table
        print("\n5. Adding soil texture columns to Soil table...")
        
        # Add clay column
        try:
            cursor.execute("ALTER TABLE Soil ADD COLUMN clay REAL")
            print("   Column 'clay' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'clay' already exists")
            else:
                raise
        
        # Add silt column
        try:
            cursor.execute("ALTER TABLE Soil ADD COLUMN silt REAL")
            print("   Column 'silt' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'silt' already exists")
            else:
                raise
        
        # Add sand column
        try:
            cursor.execute("ALTER TABLE Soil ADD COLUMN sand REAL")
            print("   Column 'sand' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'sand' already exists")
            else:
                raise
        
        # Add extp column
        try:
            cursor.execute("ALTER TABLE Soil ADD COLUMN extp REAL")
            print("   Column 'extp' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'extp' already exists")
            else:
                raise
        
        # Add totp column
        try:
            cursor.execute("ALTER TABLE Soil ADD COLUMN totp REAL")
            print("   Column 'totp' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'totp' already exists")
            else:
                raise
        
        # Update clay, silt, sand from SoilTypes table
        print("   Checking SoilTextureType matching...")
        
        # Diagnostic: Check unmatched values
        cursor.execute("""
            SELECT DISTINCT Soil.SoilTextureType 
            FROM Soil 
            WHERE NOT EXISTS (
                SELECT 1 FROM SoilTypes 
                WHERE TRIM(UPPER(SoilTypes.SoilTextureType)) = TRIM(UPPER(Soil.SoilTextureType))
            )
        """)
        unmatched = cursor.fetchall()
        if unmatched:
            print(f"   WARNING: {len(unmatched)} unmatched SoilTextureType values in Soil table:")
            for row in unmatched:
                print(f"      '{row[0]}'")
        
        print("   Updating clay, silt, sand values from SoilTypes table...")
        cursor.execute("""
            UPDATE Soil 
            SET clay = (
                SELECT SoilTypes.clay 
                FROM SoilTypes 
                WHERE TRIM(UPPER(SoilTypes.SoilTextureType)) = TRIM(UPPER(Soil.SoilTextureType))
            ),
            silt = (
                SELECT SoilTypes.silt 
                FROM SoilTypes 
                WHERE TRIM(UPPER(SoilTypes.SoilTextureType)) = TRIM(UPPER(Soil.SoilTextureType))
            ),
            sand = (
                SELECT SoilTypes.sand 
                FROM SoilTypes 
                WHERE TRIM(UPPER(SoilTypes.SoilTextureType)) = TRIM(UPPER(Soil.SoilTextureType))
            )
            WHERE EXISTS (
                SELECT 1 FROM SoilTypes 
                WHERE TRIM(UPPER(SoilTypes.SoilTextureType)) = TRIM(UPPER(Soil.SoilTextureType))
            )
        """)
        print(f"      Updated {cursor.rowcount} rows with texture values")
        
        # Set extp and totp to -99
        print("   Setting extp and totp to -99...")
        cursor.execute("UPDATE Soil SET extp = -99, totp = -99")
        print(f"      Updated {cursor.rowcount} rows")
        
        # Step 6: Update idPoint in Coordinates table
        print("\n6. Updating idPoint in Coordinates table...")
        cursor.execute("""
            UPDATE Coordinates 
            SET idPoint = CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
        """)
        print(f"   Updated {cursor.rowcount} rows")
        
        # Step 7: Update idsim in SimUnitList table
        print("\n7. Updating idsim in SimUnitList table...")
        cursor.execute("""
            UPDATE SimUnitList 
            SET idsim = idPoint || '_' || CAST(CAST(year AS INTEGER) AS TEXT) || '_' || idMangt || '_' || idOption
        """)
        print(f"   Updated {cursor.rowcount} rows")
        
        # Step 8: Verify the changes
        print("\n8. Verifying changes...")
        cursor.execute("SELECT idPoint, name, latitudeDD, longitudeDD FROM Coordinates LIMIT 5")
        print("   Sample from Coordinates table:")
        for row in cursor.fetchall():
            print(f"      idPoint: {row[0]}, name: {row[1]}, lat: {row[2]}, lon: {row[3]}")
        
        cursor.execute("SELECT idsim, idPoint, idSoil, year, idMangt, idOption FROM SimUnitList LIMIT 5")
        print("   Sample from SimUnitList table:")
        for row in cursor.fetchall():
            print(f"      idsim: {row[0]}, idPoint: {row[1]}, idSoil: {row[2]}, year: {row[3]}, idMangt: {row[4]}, idOption: {row[5]}")
        
        cursor.execute("SELECT idPoint, SoilTextureType, clay, silt, sand, extp, totp FROM Soil LIMIT 5")
        print("   Sample from Soil table:")
        for row in cursor.fetchall():
            print(f"      idPoint: {row[0]}, TextureType: {row[1]}, clay: {row[2]}, silt: {row[3]}, sand: {row[4]}, extp: {row[5]}, totp: {row[6]}")
        
        # Commit changes
        conn.commit()
        print("\n✓ All changes committed successfully!")
        
        # Optional: Drop the 'name' column if no longer needed
        # print("\n9. Dropping temporary 'name' column...")
        # cursor.execute("ALTER TABLE Coordinates DROP COLUMN name")
        # conn.commit()
        # print("   'name' column dropped")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error occurred: {e}")
        print("   All changes rolled back")
        raise
    
    finally:
        conn.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    # Get database filename from command line argument
    if len(sys.argv) < 2:
        print("Usage: python change_key.py <database_file.db>")
        print("Example: python change_key.py MasterInput.db")
        sys.exit(1)
    
    db_filename = sys.argv[1]
    db_file = Path(db_filename)
    
    if not db_file.exists():
        print(f"Error: {db_file} not found")
        print(f"Current directory: {Path.cwd()}")
        sys.exit(1)
    
    update_database_keys(str(db_file))
    print("\n✓ Database update completed!")




