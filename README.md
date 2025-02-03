# AutoRunway

A Python script that automatically updates active runways for Norwegian airports based on real-time METAR data from VATSIM. 
It's designed to help air traffic controllers by automatically selecting the most appropriate runways based on current wind conditions.

## How it works

- Automatically fetches METAR data for all Norwegian airports from VATSIM
- Selects optimal runways based on wind direction and speed
- Special handling for variable wind conditions
- Dedicated handling for Oslo Airport (ENGM) with multiple operational modes:
  - Mixed Operations (MPO)
  - Segregated Operations
  - Single Runway Operations
- Updates all .rwy files in the same folder simultaneously
- Fallback to preferred runways when vind data is variable/calm.

## Installation

1. Ensure you have Python installed on your system
2. Clone this repository
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start
1. Double-click `update_runways.bat` to run the script
2. For ENGM during variable winds or low visibility, you'll be prompted to select a runway configuration:
   1. 19 MPO (Mixed Operations)
   2. 01 MPO (Mixed Operations)
   3. 19 Segregated (19L Departures, 19R Arrivals)
   4. 01 Segregated (01L Departures, 01R Arrivals)
   5. 19 Single (19R only)
   6. 01 Single (01L only)

## Preferred Runway Configuration

The script includes predefined preferred runways for various airports when wind data is unavailable:

- ENBR: 17
- ENTO: 18
- ENRY: 30
- ENZV: 18
- ENHD: 13
- ENAL: 24
- ENML: 07
- ENKB: 07
- ENVA: 09
- ENBO: 07
- ENTC: 18
- ENCN: 21
- ENRO: 31
- ENSG: 24
- ENFL: 07
- ENEV: 17
- ENDU: 28
- ENAT: 11
- ENNA: 34
- ENKR: 24
- ENSB: 09
- ENNO: 12
- ENSD: 26
- ENSO: 14
- ENMS: 33
- ENBN: 03
- ENST: 20
- ENRA: 31
- ENLK: 02
- ENSH: 36
- ENAN: 14
- ENOL: 15
