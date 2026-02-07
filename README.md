# DIHxAUC_Khaliha3alaAllah

## Description
For this project, the Client (QuickServer) have had a repeating issue of Shift Planning, where the fluctuations in the week plan that vary with no prediction of demand makes it difficult to assess how many workers are needed and the risk of overstaffing leading to a harsh increase in labor costs. To solve this problem, Our team has built a Shift Wizard, an Intellegent System that assess Client Data such as work schedules, PTO, suprise events, and more through a curated database that outputs a next best move and schedule to fit the Client's requests.  

## Features 
### 1. Demand Forecast per shift (Next 7 Days):
* Inputs: Historical sales/orders, day-of-week, hour/shift, holidays/events flag, weather conditions
* Output: Expected demand level per shift (e.g., orders/hour)

### 2. Staffing Recommendations 
* Converts forecasted demand to required staff count per role (cashier, kitchen, runner)
* Handles Constraints:
  * Minimum staff per shift
  * Max weekly hours per employee
  * PTO / unavailablity
  * Skill matching (deciding roles based on skill sets)

### 3. Disruption Mode
* Recommends best replacement or shift swap incase of staff call off
* Shows: “coverage gap”, “best candidate”, “estimated impact”

### 4. Manager Dashboard
* “This week schedule health”: under/overstaffed shifts, projected labor cost, risk alerts
* “What-if” slider: service-level target vs labor cost

## Core services
### 1. Forecast Service
* Takes history + context → predicts demand per shift

### 2. Recommendation Service
* Converts demand to staffing requirement
* Matches employees to shifts with constraints
* Outputs recommended actions

### 3. Impact Calculator
* Labor cost estimater
* Understaffing risk score
* Simple “service quality proxy” (e.g., expected wait time)

## Technologies Used
#### Frontend 
For Frontend services such as managing the interface and creative design, StreamLit was used. 

#### Backend 
For Backend services, to ensure a cohesive and integrated code as to aviod any errors and overcrowding, Python was used. 

#### AI Models 
For AI, a clustering model was used. It classifies each place into clusters and forms predictions based on user input. 

#### Database 
The Data for shifts and other important information was provided by the client's CSV and were filtered to only use relevant information needed for the system. 

## Installation
For the installation process, there are several dependencies that need to be installed to ensure that the Shift Wizard works reliably. 
* **Streamlit**: For the web dashboard and UI
* **Pandas**: For data manipulation and CSV handling
* **Numpy**: For numerical operations
* **Scikit-learn**: For the KMeans clustering and data scaling
* **Ortools**: For the Google CP-SAT scheduling optimization
* **Matplotlib**: For the forecast visualization charts

#### Supporting / System
* **Protobuf**: Required by OR-Tools for data serialization
* **Pathlib**: (Built-in) For file path management
* **Json**: (Built-in) For parsing store hours data
 
