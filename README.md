# Logistics Cost Reconciliation

## 1. Problem Statement and Your Approach

The platform helps logistics companies reconcile transport costs by processing Excel uploads that contain truck details, capacities, assigned load, and associated companies.

### My Approach:
- Parsed Excel data is stored in a Django backend using models for trucks and transport companies (default sqlite is used).
- A greedy algorithm is used to optimize load distribution, prioritizing trucks with higher capacity to ensure full fleet utilization.
- Costs are calculated based on the load each company is responsible for.
- DRF is being used to create the API endpoints which are used for making frontend integrations.


## 2. Setup Instructions

### Prerequisites

### How to Run the Project

## 3. Explanations of Complex Logic/Algorithms
For the load optimization a greedy algorithm is being used something similar to one we use in knapsack problem,
- First, trucks are sorted in decreasing order of their capacity, so that trucks with higher capacity are filled first.
- Total load which the trucks need to take is calculated from the assigned_load.
- Then iterate through the sorted truck list: If the remaining load is greater than or equal to the truck's capacity, the truck is assigned its full capacity and the remaining load is reduced accordingly. If the remaining load is less than the truck’s capacity, the truck is assigned all the remaining load, and the distribution is complete.
- This leads to trucks with higher capacity getting filled first.
- Then db is updated using bulk_update.

## 4. Video Link

