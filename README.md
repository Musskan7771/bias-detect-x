# Cognitive Bias Detector v7

A Flask + scikit-learn educational web application that detects patterns of 15 cognitive biases plus No Clear Bias.

## Dataset
- 16 categories
- 100 examples per category
- 1,600 total examples

## ML model
- TF-IDF vectorization with unigrams and bigrams
- Logistic Regression classifier
- 80/20 stratified holdout evaluation
- Final prediction model retrained on all 1,600 examples

## Website features
1. Dark/light mode
2. Model Performance page
3. Statistics dashboard with bar + donut charts
4. Bias search
5. Possible related-bias warning
6. Sample Text Library for shopping, education, workplace, finance, social media and everyday decisions
7. Export history to CSV and individual reports to PDF
8. Model information panel
9. Project/Viva guide
10. Result animations and responsive UI
11. History and New Chat at top-right
12. 16 bias information cards
13. Explainable result, practical tip and category scores

## Run
```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python train_model.py
python app.py
```
Open http://127.0.0.1:5000

Educational prototype only; not a psychological diagnosis.
