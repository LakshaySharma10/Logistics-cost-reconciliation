# Logistics Cost Reconciliation

## 1. Problem Statement and Your Approach

The platform helps logistics companies reconcile transport costs by processing Excel uploads that contain truck details, capacities, assigned load, and associated companies.

### My Approach:
- Parsed Excel data is stored in a Django backend using models for trucks and transport companies (default sqlite is used).
- A greedy algorithm is used to optimize load distribution, prioritizing trucks with higher capacity to ensure full fleet utilization.
- Costs are calculated based on the load each company is responsible for.
- DRF is being used to create the API endpoints which are used for making frontend integrations.


## 2. Setup Instructions

> **Note:** This project uses [`uv`](https://github.com/astral-sh/uv) for the Django backend to install dependencies faster.
### How to Run the Project

#### 1. Clone the Repository

```bash
git clone https://github.com/LakshaySharma10/Logistics-cost-reconciliation.git
cd Logistics-cost-reconciliation
```
#### 2. Set Up the Django Backend

```bash
cd frnd
python -m venv venv               
source venv\Scripts\activate  

# Install dependencies
uv pip install -r requirements.txt    # or just pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```
- The backend will run at: **http://127.0.0.1:8000**

#### 3. Set Up the Next.js Frontend
```bash
cd ../frontend
npm install                   
npm run dev                    
```

- The frontend will run at: **http://localhost:3000**

### 📁 Folder Structure

```
Logistics-cost-reconciliation/
│
├── frnd/          # Django backend
│   └── manage.py
│
├── frontend/      # Next.js frontend
│   └── components
│
└── README.md
```
---
- You can use [uv](https://github.com/astral-sh/uv) for faster Python dependency management.
- Frontend is deployed at: [logistics-cost-reconciliation-beta.vercel.app](https://logistics-cost-reconciliation-beta.vercel.app)
- Backend is deployed at : [logistics-cost-reconciliation.onrender.com](https://logistics-cost-reconciliation.onrender.com)

## 3. Explanations of Complex Logic/Algorithms

A **hybrid greedy + bin-packing approach** is used to optimize truck load assignments:

- **Trucks are sorted** in **descending order of capacity**, so that larger trucks are filled first.
- **Total load** is calculated from the sum of each truck's `assigned_load`.
### Greedy Filling Phase
- Iterate through the sorted list of trucks:
  - If the `remaining_load` is **greater than or equal** to the truck's capacity:
    - Assign the truck its **full capacity**.
    - Subtract the capacity from the `remaining_load`.
- This continues until you reach a truck whose capacity is **greater than** the remaining load.

### Bin-Packing Phase (First Fit)
- The remaining trucks are **sorted in ascending order of capacity**.
- The goal is to assign the **leftover load** to the **smallest suitable truck** (tightest fit), minimizing underutilization.
- This ensures that **smaller trucks** are prioritized for small remaining loads, instead of **partially filling** larger ones.

- Finally, the optimized assignments are **saved to the database** using `bulk_update`.


## 4. Video Link
https://www.loom.com/share/c6dfcc14d30343c79b03e6d28879db2e?sid=c3d08ef6-4e06-484f-bbf7-c525771c415f
