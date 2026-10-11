from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import csv
import joblib
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "bias_model.pkl")
METRICS_PATH = os.path.join(BASE, "model", "model_metrics.json")
model = joblib.load(MODEL_PATH)

BIAS_INFO = {
    "anchoring_bias": {"name":"Anchoring Bias","description":"Relying too heavily on the first number, fact, or piece of information encountered.","tip":"Compare several independent reference points before making a judgment."},
    "availability_bias": {"name":"Availability Bias","description":"Judging likelihood or importance based on examples that are easy to recall.","tip":"Ask whether memorable examples are actually representative of the larger situation."},
    "confirmation_bias": {"name":"Confirmation Bias","description":"Favoring information that supports an existing belief while overlooking contradictory evidence.","tip":"Actively look for evidence that could prove your current belief wrong."},
    "framing_bias": {"name":"Framing Bias","description":"Reacting differently to the same information because it is presented in different ways.","tip":"Rewrite the information in neutral terms and compare the underlying facts."},
    "bandwagon_effect": {"name":"Bandwagon Effect","description":"Adopting a belief or behavior because many other people appear to support it.","tip":"Separate popularity from evidence of quality or truth."},
    "status_quo_bias": {"name":"Status Quo Bias","description":"Preferring the current situation simply because it is familiar or already in place.","tip":"Compare the current option with alternatives as if you were choosing from scratch."},
    "sunk_cost_fallacy": {"name":"Sunk Cost Fallacy","description":"Continuing something because of resources already spent, even when continuing is not worthwhile.","tip":"Focus on future costs and benefits, not resources that cannot be recovered."},
    "loss_aversion": {"name":"Loss Aversion","description":"Feeling the pain of a loss more strongly than the pleasure of an equivalent gain.","tip":"Evaluate gains and losses using the same objective scale."},
    "optimism_bias": {"name":"Optimism Bias","description":"Underestimating the chance of negative outcomes and overestimating the chance of positive ones.","tip":"Use base rates and realistic downside scenarios when planning."},
    "negativity_bias": {"name":"Negativity Bias","description":"Giving negative information more weight or attention than equally important positive information.","tip":"Consider the complete evidence rather than letting one negative detail dominate."},
    "halo_effect": {"name":"Halo Effect","description":"Letting one positive characteristic influence your overall judgment of a person or thing.","tip":"Evaluate each relevant characteristic separately."},
    "horns_effect": {"name":"Horns Effect","description":"Letting one negative characteristic unfairly influence your overall judgment.","tip":"Separate a person's mistake or flaw from their other qualities."},
    "dunning_kruger_effect": {"name":"Dunning-Kruger Effect","description":"People with limited knowledge in an area may overestimate their competence.","tip":"Use feedback, testing, and learning evidence to calibrate confidence."},
    "recency_bias": {"name":"Recency Bias","description":"Giving disproportionate importance to the most recent information or events.","tip":"Review the full time period instead of relying mainly on what happened most recently."},
    "representativeness_heuristic": {"name":"Representativeness Heuristic","description":"Judging probability by how much something resembles a typical example while neglecting base rates.","tip":"Check statistical base rates before deciding what a pattern means."},
    "none": {"name":"No Clear Bias","description":"The text does not clearly match one of the supported cognitive-bias categories.","tip":"Keep using evidence and consider alternative explanations."}
}

EXAMPLES = {
    "anchoring_bias":"This laptop was originally ₹80,000 and is now ₹50,000, so it must be an excellent deal.",
    "availability_bias":"I saw two news stories about airplane accidents, so flying must be extremely dangerous.",
    "confirmation_bias":"I already know this diet works, so I only read reviews from people who say it worked.",
    "framing_bias":"A treatment is described as having a 90% survival rate, so I choose it; I would reject it if told it has a 10% death rate.",
    "bandwagon_effect":"Everyone in my class is buying this phone, so it must be the best phone.",
    "status_quo_bias":"Our company has always used this software, so changing to a better option would be a bad idea.",
    "sunk_cost_fallacy":"I have already spent ₹10,000 on this course, so I must finish it even though it is not helping me.",
    "loss_aversion":"I would rather keep a guaranteed ₹500 than risk losing ₹500, even though the possible gain is much larger.",
    "optimism_bias":"I don't need a backup plan because my project will definitely finish on time.",
    "negativity_bias":"The product has 99 positive reviews and one negative review, so I think it is probably terrible.",
    "halo_effect":"She is an excellent athlete, so she must also be a great manager.",
    "horns_effect":"He made one mistake in the presentation, so he is clearly bad at his job.",
    "dunning_kruger_effect":"I watched a few coding videos, so I already know more programming than experienced developers.",
    "recency_bias":"The player scored poorly in yesterday's match, so he is clearly a bad player this season.",
    "representativeness_heuristic":"He is quiet and loves books, so he must be a scientist.",
    "none":"The store opens at 9 AM and closes at 9 PM."
}

SAMPLE_LIBRARY = {
    "Shopping": ["This shirt costs ₹3,000, but it was originally ₹6,000, so it must be a great deal.", "Everyone is buying this phone, so it must be the best phone.", "The celebrity promoting this product is successful, so the product must be excellent."],
    "Education": ["I got one excellent mark, so I know I will top every exam.", "I failed one test, so I am definitely bad at this subject.", "I already paid for the course, so I have to finish it even though it is not useful."],
    "Workplace": ["We have always used this software, so changing it would be a bad idea.", "She gave one great presentation, so she must be excellent at every part of her job.", "He made one mistake, so he is clearly incompetent."],
    "Finance": ["The stock rose yesterday, so it will definitely keep rising.", "I don't want to sell because I already lost ₹20,000 on this investment.", "I would rather avoid losing ₹500 than take a chance to gain ₹1,500."],
    "Social Media": ["Millions of people follow this influencer, so everything they recommend must be trustworthy.", "I only follow posts that agree with my opinion.", "I saw one scary post about a disease, so I think it is extremely common."],
    "Everyday Decisions": ["The last restaurant I visited was terrible, so restaurants in this area must be bad.", "He drives a luxury car, so he must be very successful.", "The shop is open from 9 AM to 9 PM."]
}

with open(METRICS_PATH, "r", encoding="utf-8") as f:
    MODEL_METRICS = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", biases=BIAS_INFO, examples=EXAMPLES, sample_library=SAMPLE_LIBRARY, metrics=MODEL_METRICS)

@app.route("/performance")
def performance():
    return render_template("performance.html", metrics=MODEL_METRICS, biases=BIAS_INFO)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error":"Please enter some text."}), 400
    probs = model.predict_proba([text])[0]
    classes = model.classes_
    scores = {str(c): round(float(p)*100,2) for c,p in zip(classes,probs)}
    best_index = int(probs.argmax())
    label = str(classes[best_index])
    confidence = round(float(probs[best_index])*100,2)
    ranked = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    info = BIAS_INFO.get(label, BIAS_INFO["none"])
    possible = [{"key":k,"name":BIAS_INFO.get(k,BIAS_INFO["none"])["name"],"score":v} for k,v in ranked[1:4] if v >= 8 and (confidence-v) <= 22]
    return jsonify({"bias":label,"bias_name":info["name"],"confidence":confidence,"scores":scores,"description":info["description"],"tip":info["tip"],"why_detected":f"The wording most closely matches the learned language patterns for {info['name']}. The model compared it with all 16 supported categories and assigned this category the highest probability.","possible_biases":possible})

@app.route("/download-report", methods=["POST"])
def download_report():
    data=request.get_json(silent=True) or {}
    text=str(data.get("text") or ""); bias_name=str(data.get("bias_name") or "Unknown"); confidence=str(data.get("confidence") or "0"); description=str(data.get("description") or ""); why=str(data.get("why_detected") or ""); tip=str(data.get("tip") or "")
    buffer=BytesIO(); pdf=canvas.Canvas(buffer,pagesize=A4); width,height=A4; y=height-60
    pdf.setTitle("Cognitive Bias Analysis Report"); pdf.setFont("Helvetica-Bold",18); pdf.drawString(50,y,"Cognitive Bias Analysis Report"); y-=35
    for title,value in [("Input Text",text),("Detected Bias",bias_name),("Confidence",f"{confidence}%"),("Why This Was Detected",why),("Explanation",description),("Practical Tip",tip)]:
        pdf.setFont("Helvetica-Bold",12); pdf.drawString(50,y,title); y-=18; pdf.setFont("Helvetica",10)
        for line in simpleSplit(value,"Helvetica",10,width-100):
            if y<60: pdf.showPage(); y=height-60; pdf.setFont("Helvetica",10)
            pdf.drawString(50,y,line); y-=14
        y-=12
    pdf.setFont("Helvetica-Oblique",9); pdf.drawString(50,35,"Educational prototype only. This is not a psychological diagnosis."); pdf.save(); buffer.seek(0)
    return send_file(buffer,as_attachment=True,download_name="cognitive_bias_report.pdf",mimetype="application/pdf")

@app.route("/download-history-csv", methods=["POST"])
def download_history_csv():
    items=(request.get_json(silent=True) or {}).get("history") or []
    output=StringIO(); writer=csv.writer(output); writer.writerow(["Date/Time","Bias","Confidence","Text"])
    for x in items: writer.writerow([x.get("time",""),x.get("bias",""),x.get("confidence",""),x.get("text","")])
    mem=BytesIO(output.getvalue().encode("utf-8-sig")); mem.seek(0)
    return send_file(mem,as_attachment=True,download_name="cognitive_bias_history.csv",mimetype="text/csv")

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
