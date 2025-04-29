# **KnowYourHair – Hair Loss Risk Prediction and Prevention Web Application**  
🚧 **Status:** Currently Working On It 🚧  

## **Overview**  
Many individuals experience **hair loss**, with androgenetic alopecia being the most common type, affecting **80% of men and 50% of women** worldwide. Studies show that **16% of men aged 18-29** and **53% of men aged 40-49** experience moderate to extensive hair loss (T Rhodes, 1998).  

To address this, **KnowYourHair** is an AI-powered **web application** designed to predict an individual's **future risk of hair loss** based on factors like **family history, lifestyle, nutrition, stress, and environmental conditions**.  

### **Key Features**  
✔ **Predicts Hair Loss Risk** (Low, Medium, High)  
✔ **Personalized Timeline for Hair Loss Probability**  
✔ **Prevention Tips** (Nutrition, Hair Care, Dermatologist Consultation)  
✔ **Search & Book Appointments with Dermatologists**  
✔ **Hair Care Products & Medications with Purchase Option**  
✔ **Educational Content on Hair Health & Myths**  
✔ **Admin & Agent Management for Clinics & Products**  

## **Risk Categories & Prediction Approach**  
- **Low Risk** → No significant risk detected. Recommendation: Maintain hair health.  
- **Medium Risk** → Moderate risk detected. Hair loss prediction = *(average affected age) + 5 years*.  
- **High Risk** → Severe risk detected. Hair loss prediction = *(average affected age)*.  

🛠 *Factors Considered for Prediction:*  
- **Genetics**, **Chemical Product Usage**, **Chronic Illness**, **Sleep Disturbances**  
- **Water Quality**, **Stress**, **Diet & Nutrition**  

## **Aims & Objectives**  
### **Aim**  
To develop a **web application** that predicts hair loss risk early and provides **preventive solutions**, including:  
- Personalized risk assessment  
- Hair care recommendations  
- Professional dermatologist consultations  
- Hair product purchases  

### **Objectives**  
#### **1. Predictive Analysis**  
- Use **Kaggle dataset** to train a machine learning model for hair loss prediction.  
- Implement an **AI model** that can handle complex datasets and capture non-linear interactions.  

#### **2. User Interactions**  
- Develop a **user-friendly, responsive web interface**.  
- Enable **user registration, login, and profile management** for personalized recommendations.  

#### **3. Product & Clinic Integration**  
- Allow users to **browse & purchase hair care products**.  
- Implement **clinic search & appointment booking** for consultations.  

#### **4. Admin & Agent Management**  
- **Admin panel** for content approval & user management.  
- **Agent dashboard** for clinic & product registration (requires admin approval).  

## **Technology Stack**  
- **Backend:** Python (django), Machine Learning (Scikit-learn)  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** sqlite3
- **Data Handling:** Pandas, NumPy  
- **ML Model:** Random forest


---

### 🗂 Project Structure

```
📁 KnowYourHair/             # Registration & validation logic
📁 base/                     # Common logic for all users
📁 clinic/                   # Clinic tools & views
📁 dataset/                  # Data storage & export functionality
📁 hairfallprediction/       # ML model & prediction logic
📁 media/                    # Static/media assets
📁 notebook/                 # Jupyter notebooks for experiments
📁 product/                  # Product recommendation system
📁 user/                     # User profile, access control
📄 db.sqlite3                # Pre-configured database
📄 requirements.txt          # Python dependencies
📄 run_tests.py              # Runs all test files
📄 test_hairfall_predictor.py  # Tests for prediction
📄 test_product_recommender.py # Tests for product recommender
📄 manage.py                 # Django management script
📄 README.md                 # Project documentation
```

---

## 🛠 Installation & Setup

Follow these steps to set up and run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/GiriHridaya319/KnowYourHair.git
cd KnowYourHair
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

---

## 🧪 Running Unit Tests

To test all modules:
```bash
python run_tests.py
```

Or run specific test files:
```bash
python test_hairfall_predictor.py
python test_product_recommender.py
```

---

## 💾 Database

This project uses SQLite. No setup needed — the `db.sqlite3` file is pre-included and ready to use.

---

## 📌 Notes

- Use Python 3.7+ (recommended)
- A virtual environment is recommended for local development
- Exported survey data is handled in the `dataset/` directory
- Jupyter notebooks for training/testing are inside the `notebook/` folder

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change or improve.

---

## 📃 License

This project is licensed under the **MIT License**.

---

## 🙌 Acknowledgments

Made with ❤️ by Hridaya Giri.
