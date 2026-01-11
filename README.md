# DC Council Vote Tracker

The Council of the District of Columbia hosts a Legislative Information Management System (LIMS) which provides access to information about the legislative activities of the council via API. This project has now been updated to host a Flask-based website that showcases the processed results.

---

## Flask Website Setup

### Prerequisites
- Python 3.x installed in your system

### Installation Steps
1. Clone the repository and switch to the `convert-to-flask-website` branch:
   ```bash
   git clone https://github.com/bberg/dc-council-vote-track.git
   cd dc-council-vote-track
   git checkout convert-to-flask-website
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Web Application
   ```bash
   flask run
   ```
   The website will be available at `http://127.0.0.1:5000/` by default.

---

## Original Usage (Vote Processing Script)

### Example
```bash
python3 dc_council.py <token> 23 1
```

### Output
Example Output: [Output CSV File](outputListOfVotes_1_23.csv)

### Details
```bash
python3 dc_council.py <token> <councilPeriodId> <legislationType>
```

- **token**: A LIMS developer access token is required. Get the token [here](https://lims.dccouncil.us/developerRegistration)
- **councilPeriodId**: Council Period ID, default = 24 (2021-2022)
- **legislationType**: Legislation Type, default = 1 (Bill)

*Periods 20-24 have been tested.*

*Type 1 (Bill) has been tested.*

---

## Design

This repository processes data from LIMS and now also provides results via a website interface. For more details, see the structure of the codebase.

- Original script: Automates API and OCR tasks to generate vote data
- Flask addition: Hosts the newly structured information

---

## LIMS Information
- [LIMS Website](https://lims.dccouncil.us/)
- [API Documentation](https://lims.dccouncil.us/api/help/index.html)
- [Developer Registration](https://lims.dccouncil.us/developerRegistration)