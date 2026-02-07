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

**generate_schedule()** - Takes the demand forecast and employee list, then assigns specific employees to specific shifts 

**handle_call_off()** - When an employee calls in sick, it removes them from the schedule and suggests the best replacement candidate.

**calculate_impact_metrics()** - Analyzes the schedule to show KPIs like total labor cost, coverage rate, understaffed/overstaffed shifts for the manager dashboard.


#### AI Models 
For AI, a clustering model and others were used. It classifies each place into clusters and forms predictions based on user input and the models predict how many staff are needed and decides which specific employees work which specific shifts to meet that demand optimally.

**Standard Active (Cluster 0)**: Steady demand, predictable shifts

**Seasonal High Performers (Cluster 1)**: Surge staffing during seasons

**Inactive/Churned (Cluster 2)**: Minimal/no staffing needed

**Core High Performers (Cluster 3)**: Maximum staff, premium scheduling

**Dormant Edge Cases (Cluster 4)**: On-call staff only

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

## Team Members 
* **Database: Jumana Moussa**
  
Technical Member, went through the data checked if it is relevant to our team and changed any necessary data for the machine to better understand it. Also wrote the data_dictionary.md, which has all provided data with where it was provided, description of it, the type of data, if it used, and modifications that needed to be done
* **AI Modeling: Nadine Donia**

Technical Member, assesst and developed an modeling tool used for the processing data and training the model to create accurate predicitons based on client input
* **Backend Developer: Arwa Hossam**

Technical Member, used python to turn forecasts from the model and data into staffing decisions, created the logic behind required staff, employee scoring, call-off handling, and finally calculated covergae gaps, labor costs, and understaffing/overstaffing
* **Frontend Developer: Asmaa Elshabshiri**

Technical Member, made the system usable, visual, and understandable. 
Build Streamlit app with tabs: Forecast Overview, Recommended Schedule, Disruption Mode (call-off), Business Impact
Display: Forecast charts, Staffing tables, Buttons & sliders, Connect UI to backend functions
* **Business Consultant: Rana Wagdy**

Nontechnical Member, translated the solution into business value, created and organized the README file, and involved in the shift planning for the Shift Wizard, its delivrables and comparison of before and after scheduling processes, and help frontend with insight callouts


 
