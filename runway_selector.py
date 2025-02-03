import requests
import math
import re
from datetime import datetime
from typing import Dict, List, Tuple
import os

class Runway:
    def __init__(self, rwy1: str, rwy2: str, hdg1: int, hdg2: int, airport: str):
        self.rwy1 = rwy1
        self.rwy2 = rwy2
        self.hdg1 = hdg1
        self.hdg2 = hdg2
        self.airport = airport

def parse_runways(filename: str) -> Dict[str, List[Runway]]:
    runways = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('['):
                parts = line.strip().split()
                if len(parts) >= 9:
                    airport = parts[8]
                    runway = Runway(parts[0], parts[1], int(parts[2]), int(parts[3]), airport)
                    if airport not in runways:
                        runways[airport] = []
                    runways[airport].append(runway)
    return runways

def parse_metar(metar: str) -> dict:
    """Parse METAR string to extract wind information.
    
    Args:
        metar: Raw METAR string
        
    Returns:
        Dictionary containing:
        - direction: wind direction in degrees or 'VRB' for variable
        - speed: wind speed in knots
        - raw_metar: original METAR string
        Returns None if parsing fails
    """
    if not metar:
        return None
        
    try:
        # Parse wind information
        wind_match = re.search(r'(VRB|(\d{3}))(\d{2,3})KT', metar)
        if not wind_match:
            return None
            
        direction = wind_match.group(1)
        speed = int(wind_match.group(3))
        
        # Handle VRB winds
        if direction == 'VRB':
            return {'direction': 'VRB', 'speed': speed, 'raw_metar': metar}
        else:
            return {'direction': int(direction), 'speed': speed, 'raw_metar': metar}
            
    except Exception as e:
        print(f"Error parsing METAR '{metar}': {e}")
        return None

def get_all_metars() -> Dict[str, dict]:
    metars = {}
    try:
        # Get all Norwegian METARs
        response = requests.get('https://metar.vatsim.net/EN')
        if response.status_code == 200:
            norwegian_metars = response.text.strip().split('\n')
            for metar in norwegian_metars:
                icao = metar.split()[0]
                wind_data = parse_metar(metar)
                if wind_data:
                    metars[icao] = wind_data
        
        # Get ESKS METAR separately
        response = requests.get('https://metar.vatsim.net/metar.php?id=ESKS')
        if response.status_code == 200:
            metar = response.text.strip()
            wind_data = parse_metar(metar)
            if wind_data:
                metars['ESKS'] = wind_data
                
    except Exception as e:
        print(f"Error fetching METARs: {e}")
    
    return metars

def calculate_wind_components(runway_hdg: int, wind_dir: int, wind_speed: int) -> Tuple[float, float]:
    # Convert to radians
    runway_rad = math.radians(runway_hdg)
    wind_rad = math.radians(wind_dir)
    
    # Calculate headwind and crosswind components
    headwind = wind_speed * math.cos(wind_rad - runway_rad)
    crosswind = wind_speed * math.sin(wind_rad - runway_rad)
    
    return (headwind, abs(crosswind))

def select_runway_enzv(wind_data: dict) -> str:
    if not wind_data:
        return "18"  # Default to runway 18 if no wind data
    
    # Calculate components for both runway directions
    rwy18_hw, rwy18_xw = calculate_wind_components(177, wind_data['direction'], wind_data['speed'])
    rwy36_hw, rwy36_xw = calculate_wind_components(357, wind_data['direction'], wind_data['speed'])
    rwy10_hw, rwy10_xw = calculate_wind_components(100, wind_data['direction'], wind_data['speed'])
    rwy28_hw, rwy28_xw = calculate_wind_components(280, wind_data['direction'], wind_data['speed'])
    
    # First check 18/36
    best_18_36 = "18" if rwy18_hw > rwy36_hw else "36"
    best_18_36_xw = rwy18_xw if best_18_36 == "18" else rwy36_xw
    
    # Only use 10/28 if crosswind on 18/36 is significant (> 15 knots)
    if best_18_36_xw > 15:
        best_10_28 = "10" if rwy10_hw > rwy28_hw else "28"
        return best_10_28
    
    return best_18_36

# Preferred runways for when wind direction cannot be determined
PREFERRED_RUNWAYS = {
    'ENBR': '17',
    'ENTO': '18',
    'ENRY': '30',
    'ENZV': '18',
    'ENHD': '13',
    'ENAL': '24',
    'ENML': '07',
    'ENKB': '07',
    'ENVA': '09',
    'ENBO': '07',
    'ENTC': '18',
    'ENCN': '21',
    'ENRO': '31',
    'ENSG': '24',
    'ENFL': '07',
    'ENEV': '17',
    'ENDU': '28',
    'ENAT': '11',
    'ENNA': '34',
    'ENKR': '24',
    'ENSB': '09',
    'ENNO': '12',
    'ENSD': '26',
    'ENSO': '14',
    'ENMS': '33',
    'ENBN': '03',
    'ENST': '20',
    'ENRA': '31',
    'ENLK': '02',
    'ENSH': '36',
    'ENAN': '14',
    'ENOL': '15'
}

# Airports to ignore (uncontrolled/no METAR)
IGNORED_AIRPORTS = {
    'ENRE', 'ENGK', 'ENLI', 'ENKJ', 'ENHA', 
    'ENEG', 'ENJA', 'ENBM', 'ENAX'
}

def get_engm_config() -> Tuple[List[str], str]:
    print("\nENGM Runway Configuration:")
    print("1. 19 MPO (Mixed Parallel Operations)")
    print("2. 01 MPO (Mixed Parallel Operations)")
    print("3. 19 SPO (Segregated Parallel Operations - 19L DEP, 19R ARR)")
    print("4. 01 SPO (Segregated Parallel Operations - 01L DEP, 01R ARR)")
    print("5. 19 SRO (Single Runway Operations - 19R)")
    print("6. 01 SRO (Single Runway Operations - 01L)")
    
    while True:
        try:
            choice = input("Select runway configuration (1-6): ")
            if choice in ['1', '2', '3', '4', '5', '6']:
                if choice == '1':  # 19 MPO
                    return ['19L', '19R'], "MPO"
                elif choice == '2':  # 01 MPO
                    return ['01L', '01R'], "MPO"
                elif choice == '3':  # 19 SPO
                    return ['19L', '19R'], "SPO"
                elif choice == '4':  # 01 SPO
                    return ['01L', '01R'], "SPO"
                elif choice == '5':  # 19 SRO
                    return ['19R'], "SRO"
                else:  # 01 SRO
                    return ['01L'], "SRO"
        except ValueError:
            pass
        print("Invalid choice. Please enter a number between 1 and 6.")

def update_engm_runways(filename: str, runways: List[str], mode: str):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find the ENGM lines
    arr_line_idx = None
    dep_line_idx = None
    for i, line in enumerate(lines):
        if line.startswith('ENGM_ARR'):
            arr_line_idx = i
        elif line.startswith('ENGM_DEP'):
            dep_line_idx = i
    
    if arr_line_idx is not None and dep_line_idx is not None:
        if mode == "SPO":
            # For Segregated Parallel Operations:
            # 19 config: 19R for arrivals, 19L for departures
            # 01 config: 01R for arrivals, 01L for departures
            if '19' in runways[0]:
                lines[arr_line_idx] = f'ENGM_ARR:19R\n'
                lines[dep_line_idx] = f'ENGM_DEP:19L\n'
            else:
                lines[arr_line_idx] = f'ENGM_ARR:01R\n'
                lines[dep_line_idx] = f'ENGM_DEP:01L\n'
        elif mode == "MPO":
            # For Mixed Parallel Operations, both runways can be used for both operations
            lines[arr_line_idx] = f'ENGM_ARR:{runways[0]},{runways[1]}\n'
            lines[dep_line_idx] = f'ENGM_DEP:{runways[0]},{runways[1]}\n'
        else:  # SRO
            # Single Runway Operations uses the same runway for both
            lines[arr_line_idx] = f'ENGM_ARR:{runways[0]}\n'
            lines[dep_line_idx] = f'ENGM_DEP:{runways[0]}\n'
        
        with open(filename, 'w') as f:
            f.writelines(lines)

def select_runway(airport: str, runway_data: List[Runway], wind_data: dict) -> Tuple[str, str, bool]:
    message = ""
    should_print = False  # Flag to determine if we should print the message
    
    if not wind_data:
        # Check if there's a preferred runway for this airport
        if airport in PREFERRED_RUNWAYS:
            selected = PREFERRED_RUNWAYS[airport]
            message = f"No wind data available - using preferred runway {selected}"
        else:
            selected = runway_data[0].rwy1
            message = f"No wind data available - defaulting to runway {selected}"
        should_print = True
        return selected, message, should_print
    
    # Special case for ENGM with variable winds or low visibility
    if airport == 'ENGM':
        if wind_data.get('direction') == 'VRB' or 'FZFG' in wind_data['raw_metar']:
            print(f"\nENGM current conditions: {wind_data['raw_metar']}")
            runways, mode = get_engm_config()
            message = f"Using {mode} mode with runways {', '.join(runways)}"
            should_print = True
            return runways, message, should_print
    
    # Handle variable winds
    if wind_data.get('direction') == 'VRB':
        if airport in PREFERRED_RUNWAYS:
            selected = PREFERRED_RUNWAYS[airport]
            message = f"Wind is {wind_data['raw_metar']}, using preferred runway {selected}"
        else:
            # Get the lowest numbered runway if no preference is set
            lowest_rwy = min([min(int(r.rwy1.rstrip('LRC')), int(r.rwy2.rstrip('LRC'))) for r in runway_data])
            for runway in runway_data:
                if int(runway.rwy1.rstrip('LRC')) == lowest_rwy:
                    selected = runway.rwy1
                elif int(runway.rwy2.rstrip('LRC')) == lowest_rwy:
                    selected = runway.rwy2
            message = f"Wind is {wind_data['raw_metar']}, no preferred runway - using runway {selected}"
        should_print = True
        return selected, message, should_print
    
    # For all other airports, calculate components for all runways
    best_runway = None
    best_headwind = float('-inf')
    max_crosswind = 25  # Maximum acceptable crosswind component
    
    for runway in runway_data:
        # Check both directions of the runway
        hdg1_hw, hdg1_xw = calculate_wind_components(runway.hdg1, wind_data['direction'], wind_data['speed'])
        hdg2_hw, hdg2_xw = calculate_wind_components(runway.hdg2, wind_data['direction'], wind_data['speed'])
        
        # If crosswind is too strong, skip this runway
        if min(hdg1_xw, hdg2_xw) > max_crosswind:
            continue
            
        # Choose the direction with better headwind
        if hdg1_hw > hdg2_hw:
            if hdg1_hw > best_headwind and hdg1_xw <= max_crosswind:
                best_runway = runway.rwy1
                best_headwind = hdg1_hw
        else:
            if hdg2_hw > best_headwind and hdg2_xw <= max_crosswind:
                best_runway = runway.rwy2
                best_headwind = hdg2_hw
    
    # If no runway found within crosswind limits, choose the one with least crosswind
    if not best_runway:
        min_crosswind = float('inf')
        for runway in runway_data:
            _, hdg1_xw = calculate_wind_components(runway.hdg1, wind_data['direction'], wind_data['speed'])
            _, hdg2_xw = calculate_wind_components(runway.hdg2, wind_data['direction'], wind_data['speed'])
            
            if hdg1_xw < min_crosswind:
                min_crosswind = hdg1_xw
                best_runway = runway.rwy1
            if hdg2_xw < min_crosswind:
                min_crosswind = hdg2_xw
                best_runway = runway.rwy2
        should_print = True  # Print when we had to choose based on minimum crosswind
    
    message = f"Selected runway {best_runway} based on wind {wind_data['direction']}@{wind_data['speed']}KT"
    return best_runway, message, should_print

def update_rwy_file(filename: str, airport: str, runway: str):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Create new content
    new_lines = []
    for line in lines:
        if line.startswith(f'ACTIVE_RUNWAY:{airport}:'):
            continue
        new_lines.append(line)
    
    # Add new active runway for both departure (1) and arrival (0)
    new_lines.append(f'ACTIVE_RUNWAY:{airport}:{runway}:1\n')
    new_lines.append(f'ACTIVE_RUNWAY:{airport}:{runway}:0\n')
    
    # Write back to file
    with open(filename, 'w') as f:
        f.writelines(new_lines)

def main():
    # Get runway data
    runways = parse_runways('runway.txt')
    
    # Get all METARs in one go
    all_metars = get_all_metars()
    
    # Get all .rwy files in the directory
    rwy_files = [f for f in os.listdir() if f.endswith('.rwy')]
    if not rwy_files:
        print("No .rwy files found in directory")
        return
        
    print(f"Found {len(rwy_files)} .rwy file(s)")
    print("Updating runways based on current conditions...")
    print("-" * 50)
    
    # Process each airport
    for airport, runway_data in runways.items():
        # Skip ignored airports
        if airport in IGNORED_AIRPORTS:
            continue
            
        # Get METAR for the airport
        wind_data = all_metars.get(airport)
        
        if wind_data:
            # Select runway based on wind
            selected_runway, message, should_print = select_runway(airport, runway_data, wind_data)
            
            # Update all .rwy files
            for rwy_file in rwy_files:
                if airport == 'ENGM' and isinstance(selected_runway, list):
                    # Special handling for ENGM when multiple runways are returned
                    mode = "SPO" if "Segregated" in message else "MPO" if "MPO" in message else "SRO"
                    update_engm_runways(rwy_file, selected_runway, mode)
                else:
                    update_rwy_file(rwy_file, airport, selected_runway)
            
            if should_print:
                print(f"{airport}: {message}")
        else:
            print(f"Could not fetch wind data for {airport}")
    
    print("-" * 50)
    print("Runway update complete!")
    print("Press Enter to exit...")
    try:
        input()
    except:
        pass  # If running without console, just exit

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
