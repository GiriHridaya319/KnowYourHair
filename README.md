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

