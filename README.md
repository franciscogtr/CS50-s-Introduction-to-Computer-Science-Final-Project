# Barber Agenda 
### A web application built with Flask and integrated with SQLite to efficiently manage barbershop appointments.
## Description:
### ✨ Main Features
The application has two main routes:
#### 🏪 Barbershop/Barber Route
Complete management dashboard\
CRUD operations for barbers and services\
Full control over appointments
### 👤 Client Route
Public access to services\
Booking at any registered barbershop\
Intuitive and responsive interface

## 🚀 How It Works
**Initial Registration:** First, register a barbershop in the system\
**Setup:** After logging in, register the barbers and services associated with the barbershop\
**Client Access:** The client route will be automatically available via homepage\
**Appointments:** Clients can book services by passing the barbershop's username via GET parameter in the URL
## 🔮 Future Vision
In a future deployment, each barbershop will receive a personalized link with their username pre-loaded to share with their clients.
## 🎯 Features by Profile
### Barbershop
Own dashboard with full control\
Barber management (CRUD)\
Service management (CRUD)\
View all appointments
### Barber
Personal dashboard\
Weekly schedule view\
Access to own appointments
### Client
Public access to booking routes\
View available services\
Make appointments
## 🔒 Authentication and Security
**Public Routes:** Free access for clients\
**View Routes:** Accessible by authenticated barbers and barbershops\
**Management Routes:** Exclusive to authenticated barbershops\
Unique username and password system for each barber and barbershop
## 🗄️ Database
The system uses SQLite with referential integrity ensured through:

Foreign keys in barbers referencing barbershops\
Foreign keys in services referencing barbershops\
Foreign keys in appointments referencing service, barber, and barbershop

## 🛠️ Technologies
**Frontend** HTML5 CSS3 Bootstrap v5.2\
**Backend:** Flask (Python)\
**Database:** SQLite\
**Architecture:** Web Application

## 💻 Installation
### Prerequisites
Python 3.14 or higher\
Git
## Step by Step
**Clone the repository**\
**Navigate to the project directory**\
`cd cs50`\
**Create a Python virtual environment**\
`python -m venv cs50`\
**Activate the virtual environment**\
On Windows:\
`cs50\Scripts\activate`\
On Linux/Mac:\
`source cs50/bin/activate`\
**Install the dependencies**\
`pip install -r requirements.txt`\
**Run the application**\
`flask run --debug`
