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
        
        '''
        
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
            SET idSoil = (
                SELECT CAST(latitudeDD AS TEXT) || '_' || CAST(longitudeDD AS TEXT)
                FROM Coordinates 
                WHERE Coordinates.name = Soil.idSoil
            )
            WHERE EXISTS (
                SELECT 1 FROM Coordinates WHERE Coordinates.name = Soil.idSoil
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
        '''
        
        # Step 5: Add soil texture columns to Soil table
        print("\n5. Adding soil texture columns to Soil table...")
        
        # SQLite does not support "ADD COLUMN IF NOT EXISTS", so inspect the
        # table schema first and add only the missing texture columns.
        cursor.execute("PRAGMA table_info(Soil)")
        soil_columns = {row[1].lower() for row in cursor.fetchall()}
        created_texture_columns = []

        for column in ("Silt", "Sand", "Clay"):
            if column.lower() in soil_columns:
                print(f"   Column '{column}' already exists")
                continue

            cursor.execute(f'ALTER TABLE Soil ADD COLUMN "{column}" REAL')
            soil_columns.add(column.lower())
            created_texture_columns.append(column)
            print(f"   Column '{column}' created")
        
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
        
        # Populate only columns created during this execution. Existing columns
        # and their values are left unchanged.
        if created_texture_columns:
            column_names = ", ".join(created_texture_columns)
            print(f"   Updating newly created columns: {column_names}...")
            assignments = ",\n            ".join(
                f'''"{column}" = (
                SELECT SoilTypes."{column}"
                FROM SoilTypes
                WHERE UPPER(TRIM(SoilTypes.SoilTextureType)) = UPPER(TRIM(Soil.SoilTextureType))
            )'''
                for column in created_texture_columns
            )
            cursor.execute(f"""
                UPDATE Soil
                SET {assignments}
                WHERE EXISTS (
                    SELECT 1 FROM SoilTypes
                    WHERE UPPER(TRIM(SoilTypes.SoilTextureType)) = UPPER(TRIM(Soil.SoilTextureType))
                )
            """)
            print(f"      Updated {cursor.rowcount} rows with texture values")
        else:
            print("   Texture columns already exist; values left unchanged")
        
        # Set extp and totp to -99
        print("   Setting extp and totp to -99...")
        cursor.execute("UPDATE Soil SET extp = -99, totp = -99")
        print(f"      Updated {cursor.rowcount} rows")
        
        '''
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
            SET idsim = idPoint || '_' || CAST(CAST(StartYear AS INTEGER) AS TEXT) || '_' || idMangt || '_' || idOption
        """)
        print(f"   Updated {cursor.rowcount} rows")
        '''
        # Step 8: Add DSCROP column to ListCultOption table
        print("\n8. Adding DSCROP column to ListCultOption table...")
        try:
            cursor.execute("ALTER TABLE ListCultOption ADD COLUMN DSCROP TEXT")
            print("   Column 'DSCROP' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'DSCROP' already exists")
            else:
                raise
        
        # Set DSCROP value to 'CER047'
        print("   Setting DSCROP to 'CER047'...")
        cursor.execute("UPDATE ListCultOption SET DSCROP = 'CER047'")
        print(f"      Updated {cursor.rowcount} rows")
        
        # Step 9: Add DHarvest column to CropManagement table
        print("\n9. Adding DHarvest column to CropManagement table...")
        try:
            cursor.execute("ALTER TABLE CropManagement ADD COLUMN DHarvest INTEGER")
            print("   Column 'DHarvest' created")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   Column 'DHarvest' already exists")
            else:
                raise
        
        # Set DHarvest value to 200
        print("   Setting DHarvest to 200...")
        cursor.execute("UPDATE CropManagement SET DHarvest = 200")
        print(f"      Updated {cursor.rowcount} rows")
        
        '''
        # Step 10: Verify the changes
        print("\n10. Verifying changes...")
        cursor.execute("SELECT idPoint, name, latitudeDD, longitudeDD FROM Coordinates LIMIT 5")
        print("   Sample from Coordinates table:")
        for row in cursor.fetchall():
            print(f"      idPoint: {row[0]}, name: {row[1]}, lat: {row[2]}, lon: {row[3]}")
        
        cursor.execute("SELECT idsim, idPoint, idSoil, StartYear, idMangt, idOption FROM SimUnitList LIMIT 5")
        print("   Sample from SimUnitList table:")
        for row in cursor.fetchall():
            print(f"      idsim: {row[0]}, idPoint: {row[1]}, idSoil: {row[2]}, year: {row[3]}, idMangt: {row[4]}, idOption: {row[5]}")
        
        cursor.execute("SELECT idSoil, SoilTextureType, Clay, Silt, Sand, extp, totp FROM Soil LIMIT 5")
        print("   Sample from Soil table:")
        for row in cursor.fetchall():
            print(f"      idPoint: {row[0]}, TextureType: {row[1]}, Clay: {row[2]}, Silt: {row[3]}, Sand: {row[4]}, extp: {row[5]}, totp: {row[6]}")
        '''
        # Commit changes
        conn.commit()
        print("\n✓ All changes committed successfully!")
        
        # add Column DSCROP IN ListCultOption table
        
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



