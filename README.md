🛠️ How to Run This Project Locally
Follow these steps to set up and run the project on your local machine:

1. Clone the Repository
Download the project files using Git:
git clone https://github.com/your-username/taskflow.git
cd taskflow

2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate

3. Install Required Packages
Use the requirements.txt to install all dependencies:
pip install -r requirements.txt

4. Initialize the Database
Open a Python shell or create a setup script:
python
Then run:
python

from app import db
db.create_all()
exit()
Alternatively, if you use a setup.py or init_db.py script, you can run:
python init_db.py

5. Run the Flask App
Make sure you're in the virtual environment, then run:
flask run
By default, the app runs at:
cpp
http://127.0.0.1:5000/

6. Create an Account & Start Using
Visit the home page.
Register a new account.
Log in and start managing your tasks!

