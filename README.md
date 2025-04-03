
FaceCard – Facial Recognition Payment System


Features

- Facial recognition login for students
- Neural network for real-time face matching
- Parental control over child spending and allergy alerts
- POS system with live student recognition and product cart
- Wallet balance deduction and transaction history
- Admin, Worker, and Parent roles
- PostgreSQL-backed database for scalability

---

Technologies Used

- Python, Django, HTML/CSS, JavaScript
- PostgreSQL – relational database
- OpenCV – webcam and image processing
- face_recognition – facial vector extraction
- TensorFlow – neural network training
- Bootstrap – UI styling
- Pillow, psycopg2, numpy, dlib

---

Prerequisites

Before running the project, make sure you have:

- Python 3.8 or above
- PostgreSQL installed and a DB created
- Git
- Virtualenv 
- Pycharm (recommended IDE)

---

Installation

In the Pycharm terminal:

# Step 1: Clone the repo
git clone https://github.com/Yahia-K/FaceCard.git

# Step 2: Navigate to project folder
cd FaceCard_Ammara_Final/FacePay

# Step 3: Create a virtual environment
python -m venv venv

# Step 4: Navigate to project folder
cd Project_321

# Step 5: Activate the virtual environment

.\venv\Scripts\activate

# Step 6: Install dependencies
pip install -r requirements.txt


---

Database Setup

1. Create a PostgreSQL database (FaceCardDB)
2. In settings.py, update the DATABASES section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'FaceCardDB', 
        'USER': 'your_db_user',  #change to your username
        'PASSWORD': 'your_password',  # change to your password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```


3. Apply migrations:

In the Pycharm terminal:

python manage.py makemigrations
python manage.py migrate

---

Running the Project

Inside Project_321 directory

python manage.py runserver


- Visit: `http://127.0.0.1:8000/`  by clicking on the link (it will take a little time)
- Register a parent and a worker
- Login as a parent, add a kid, and scan face
- Login as a workers and use the POS system to the scan a face and make a payment
- Can go back to the parent account to see the transaction appear in the order history table.



Developed by

Ammara Nizardeen
Digital Solutions Group – FaceCard Backend & System Implementation
