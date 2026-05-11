import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
import tkinter as tk

# ─────────────────────────────────────────────
#  APPEARANCE
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG        = "#0A0E1A"
PANEL     = "#111827"
BORDER    = "#1F2937"
ACCENT    = "#3B82F6"
GREEN     = "#10B981"
RED       = "#EF4444"
ORANGE    = "#F59E0B"
PURPLE    = "#A855F7"
WHITE     = "#F9FAFB"
MUTED     = "#6B7280"
CARD_BG   = "#1A2235"

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE  (25 diseases)
# ─────────────────────────────────────────────
DISEASES = {
    "Influenza (Flu)": {
        "symptoms": ["fever", "cough", "sore throat", "body aches", "headache", "fatigue", "chills"],
        "required": 4,
        "advice": "Rest, stay hydrated, take paracetamol for fever. See a doctor if symptoms worsen.",
        "severity": "Moderate",
    },
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "sore throat", "cough", "mild fever", "congestion"],
        "required": 3,
        "advice": "Rest, drink warm fluids, use nasal decongestants. Usually resolves in 7–10 days.",
        "severity": "Mild",
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste", "loss of smell", "fatigue", "body aches"],
        "required": 3,
        "advice": "Isolate immediately, get tested, monitor oxygen levels. Seek emergency care if breathing is difficult.",
        "severity": "High",
    },
    "Pneumonia": {
        "symptoms": ["high fever", "cough", "shortness of breath", "chest pain", "fatigue", "chills", "sweating"],
        "required": 4,
        "advice": "Seek medical attention promptly. Antibiotics may be needed. Do not self-medicate.",
        "severity": "High",
    },
    "Dengue Fever": {
        "symptoms": ["high fever", "severe headache", "body aches", "rash", "fatigue", "nausea", "joint pain"],
        "required": 4,
        "advice": "Stay hydrated, take paracetamol (avoid aspirin). Get a blood test. Monitor platelet count.",
        "severity": "High",
    },
    "Typhoid": {
        "symptoms": ["high fever", "stomach pain", "headache", "diarrhea", "fatigue", "loss of appetite", "rash"],
        "required": 4,
        "advice": "See a doctor immediately for antibiotics. Drink clean water only. Avoid street food.",
        "severity": "High",
    },
    "Malaria": {
        "symptoms": ["high fever", "chills", "sweating", "headache", "nausea", "fatigue", "body aches"],
        "required": 4,
        "advice": "Get a blood smear test immediately. Antimalarial medication required. Do not delay.",
        "severity": "High",
    },
    "Gastroenteritis": {
        "symptoms": ["diarrhea", "nausea", "vomiting", "stomach pain", "fever", "fatigue"],
        "required": 3,
        "advice": "Stay hydrated with ORS. Eat light foods (rice, bananas). See a doctor if symptoms persist beyond 2 days.",
        "severity": "Moderate",
    },
    "Migraine": {
        "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound", "blurred vision"],
        "required": 3,
        "advice": "Rest in a dark, quiet room. Take prescribed pain relievers. Consult a neurologist for recurring episodes.",
        "severity": "Moderate",
    },
    "Hypertension": {
        "symptoms": ["severe headache", "dizziness", "blurred vision", "chest pain", "shortness of breath", "nosebleed"],
        "required": 3,
        "advice": "Check blood pressure immediately. Reduce salt, stress, and caffeine. Take prescribed medication regularly.",
        "severity": "High",
    },
    "Diabetes (Type 2)": {
        "symptoms": ["frequent urination", "excessive thirst", "fatigue", "blurred vision", "slow healing", "weight loss"],
        "required": 3,
        "advice": "Check blood sugar levels. Consult a doctor for medication. Reduce sugar and carbohydrate intake.",
        "severity": "Moderate",
    },
    "Anemia": {
        "symptoms": ["fatigue", "dizziness", "pale skin", "shortness of breath", "headache", "cold hands"],
        "required": 3,
        "advice": "Eat iron-rich foods (spinach, meat). Take iron supplements if prescribed. Get a blood test (CBC).",
        "severity": "Mild",
    },
    "Asthma": {
        "symptoms": ["shortness of breath", "wheezing", "cough", "chest tightness", "difficulty breathing"],
        "required": 3,
        "advice": "Use your inhaler. Avoid triggers (dust, smoke, cold air). See a pulmonologist for long-term management.",
        "severity": "Moderate",
    },
    "Urinary Tract Infection (UTI)": {
        "symptoms": ["burning urination", "frequent urination", "cloudy urine", "pelvic pain", "mild fever", "fatigue"],
        "required": 3,
        "advice": "Drink plenty of water. Antibiotics required — see a doctor. Do not delay as it may spread to kidneys.",
        "severity": "Moderate",
    },
    "Appendicitis": {
        "symptoms": ["severe stomach pain", "nausea", "vomiting", "fever", "loss of appetite", "pain near navel"],
        "required": 3,
        "advice": "EMERGENCY: Go to ER immediately. Do not take painkillers or eat anything. Surgical intervention may be needed.",
        "severity": "Emergency",
    },
    "Tuberculosis (TB)": {
        "symptoms": ["persistent cough", "coughing blood", "weight loss", "night sweats", "fatigue", "fever", "chest pain"],
        "required": 4,
        "advice": "See a doctor immediately for TB test. Strict antibiotic course required for 6 months. Isolate from others.",
        "severity": "High",
    },
    "Hepatitis B": {
        "symptoms": ["fatigue", "nausea", "vomiting", "abdominal pain", "jaundice", "dark urine", "loss of appetite"],
        "required": 4,
        "advice": "Get a hepatitis B test. Avoid alcohol completely. Antiviral medication may be needed. Consult a liver specialist.",
        "severity": "High",
    },
    "Kidney Stones": {
        "symptoms": ["severe back pain", "pain during urination", "blood in urine", "nausea", "vomiting", "frequent urination"],
        "required": 3,
        "advice": "Drink lots of water. Pain relief medication may help. See a urologist. Larger stones may need surgery.",
        "severity": "High",
    },
    "Chickenpox": {
        "symptoms": ["rash", "itching", "fever", "fatigue", "headache", "loss of appetite"],
        "required": 3,
        "advice": "Stay home to avoid spreading. Take antihistamines for itching. Do not scratch blisters. Antiviral if severe.",
        "severity": "Mild",
    },
    "Heart Attack": {
        "symptoms": ["chest pain", "shortness of breath", "sweating", "nausea", "left arm pain", "dizziness", "fatigue"],
        "required": 4,
        "advice": "EMERGENCY: Call ambulance immediately. Chew aspirin if available. Do not drive yourself. Every minute counts.",
        "severity": "Emergency",
    },
    "Depression": {
        "symptoms": ["persistent sadness", "fatigue", "loss of appetite", "sleep problems", "difficulty concentrating", "weight loss"],
        "required": 3,
        "advice": "Speak to a mental health professional immediately. Do not isolate. Medication and therapy can help greatly.",
        "severity": "Moderate",
    },
    "Anxiety Disorder": {
        "symptoms": ["excessive worry", "racing heart", "sweating", "dizziness", "difficulty concentrating", "sleep problems", "fatigue"],
        "required": 3,
        "advice": "Practice breathing exercises. Reduce caffeine. Speak to a therapist. Medication may help in severe cases.",
        "severity": "Moderate",
    },
    "Sinusitis": {
        "symptoms": ["facial pain", "congestion", "runny nose", "headache", "fever", "loss of smell", "cough"],
        "required": 3,
        "advice": "Steam inhalation helps. Saline nasal spray recommended. See doctor if symptoms last beyond 10 days for antibiotics.",
        "severity": "Mild",
    },
    "Arthritis": {
        "symptoms": ["joint pain", "joint swelling", "stiffness", "reduced movement", "fatigue", "warmth around joints"],
        "required": 3,
        "advice": "Anti-inflammatory medication helps. Physical therapy recommended. Avoid joint strain. Consult a rheumatologist.",
        "severity": "Moderate",
    },
    "Meningitis": {
        "symptoms": ["severe headache", "high fever", "stiff neck", "sensitivity to light", "nausea", "vomiting", "rash"],
        "required": 4,
        "advice": "EMERGENCY: Go to ER immediately. This is life-threatening. IV antibiotics required urgently.",
        "severity": "Emergency",
    },
}

SEVERITY_COLOR = {
    "Mild":      GREEN,
    "Moderate":  ORANGE,
    "High":      RED,
    "Emergency": PURPLE,
}

SEVERITY_ICON = {
    "Mild":      "🟢",
    "Moderate":  "🟡",
    "High":      "🔴",
    "Emergency": "🚨",
}

ALL_SYMPTOMS = sorted(set(s for d in DISEASES.values() for s in d["symptoms"]))

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symptom_history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symptoms TEXT,
            top_diagnosis TEXT,
            score REAL,
            severity TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(symptoms, results):
    if not results:
        return
    top = results[0]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (timestamp, symptoms, top_diagnosis, score, severity) VALUES (?,?,?,?,?)",
              (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               ", ".join(symptoms), top["disease"], top["score"], top["severity"]))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, symptoms, top_diagnosis, score, severity FROM history ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────
#  INFERENCE ENGINE
# ─────────────────────────────────────────────
def run_inference(selected_symptoms):
    selected = set(selected_symptoms)
    results = []
    for disease, info in DISEASES.items():
        disease_symptoms = set(info["symptoms"])
        matches = selected & disease_symptoms
        match_count = len(matches)
        total = len(disease_symptoms)
        if match_count == 0:
            continue
        ratio = match_count / total
        threshold_bonus = 0.3 if match_count >= info["required"] else 0
        score = round((ratio + threshold_bonus) * 100, 1)
        score = min(score, 99.0)
        results.append({
            "disease": disease,
            "score": score,
            "match_count": match_count,
            "total_symptoms": total,
            "required": info["required"],
            "matched": sorted(matches),
            "advice": info["advice"],
            "severity": info["severity"],
            "likely": match_count >= info["required"]
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]

# ─────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────
def export_pdf(symptoms, results, path):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("title", fontSize=20, textColor=colors.HexColor("#1565C0"),
                                  spaceAfter=4, fontName="Helvetica-Bold")
    sub_style   = ParagraphStyle("sub", fontSize=10, textColor=colors.grey, spaceAfter=16)
    head_style  = ParagraphStyle("head", fontSize=13, textColor=colors.HexColor("#1565C0"),
                                  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)
    body_style  = ParagraphStyle("body", fontSize=10, textColor=colors.HexColor("#333333"),
                                  leading=14, spaceAfter=4)
    warn_style  = ParagraphStyle("warn", fontSize=9, textColor=colors.HexColor("#B71C1C"),
                                  fontName="Helvetica-Oblique", spaceAfter=8)

    story.append(Paragraph("🩺 Medical Symptom Checker", title_style))
    story.append(Paragraph(f"AI Expert System Report  •  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#BBDEFB")))
    story.append(Spacer(1, 12))

    story.append(Paragraph("⚠️ DISCLAIMER", head_style))
    story.append(Paragraph("This report is generated by an AI-based rule system and is NOT a substitute for professional medical advice. Always consult a licensed doctor for diagnosis and treatment.", warn_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Symptoms Reported", head_style))
    story.append(Paragraph(", ".join(s.title() for s in symptoms), body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Top Possible Conditions", head_style))
    story.append(Spacer(1, 4))

    sev_colors = {"Mild": "#4CAF50", "Moderate": "#FF9800", "High": "#F44336", "Emergency": "#9C27B0"}
    for i, res in enumerate(results):
        sc = sev_colors.get(res["severity"], "#999999")
        table_data = [
            [Paragraph(f"#{i+1}  {res['disease']}", ParagraphStyle("dname", fontSize=12, fontName="Helvetica-Bold", textColor=colors.white)),
             Paragraph(f"{SEVERITY_ICON.get(res['severity'],'')} {res['severity']}", ParagraphStyle("sev", fontSize=10, fontName="Helvetica-Bold", textColor=colors.white, alignment=2))],
        ]
        t = Table(table_data, colWidths=[4.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(sc)),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor(sc)]),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(t)

        body_data = [
            [Paragraph(f"<b>Confidence:</b> {res['score']}%", body_style),
             Paragraph(f"<b>Matched:</b> {res['match_count']} of {res['total_symptoms']} symptoms", body_style)],
            [Paragraph(f"<b>Matched Symptoms:</b> {', '.join(s.title() for s in res['matched'])}", body_style), ""],
            [Paragraph(f"<b>Recommendation:</b> {res['advice']}", body_style), ""],
        ]
        bt = Table(body_data, colWidths=[3.0*inch, 3.0*inch])
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F5F5F5")),
            ("SPAN", (0,1), (1,1)),
            ("SPAN", (0,2), (1,2)),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(bt)
        story.append(Spacer(1, 10))

    doc.build(story)

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class SymptomCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🩺 Medical Symptom Checker — AI Expert System")
        self.geometry("1200x760")
        self.configure(fg_color=BG)
        self.resizable(True, True)

        init_db()
        self.symptom_vars = {}
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_symptoms)
        self.last_results = []
        self.last_symptoms = []
        self.checkbox_widgets = {}

        self._build_ui()

    # ── UI ───────────────────────────────────
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=ACCENT, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🩺  Medical Symptom Checker",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"), text_color=WHITE).pack(side="left", padx=24, pady=18)
        ctk.CTkLabel(header, text="AI-Powered Expert System  •  25 Diseases  •  Rule-Based Inference",
                     font=ctk.CTkFont("Segoe UI", 11), text_color="#BFDBFE").pack(side="left", padx=0)

        # Tab bar
        self.tab_bar = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=40)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)

        self.tab_diagnose_btn = ctk.CTkButton(self.tab_bar, text="🔍  Diagnose", width=140, height=36,
                                              fg_color=ACCENT, hover_color="#2563EB", corner_radius=0,
                                              font=ctk.CTkFont("Segoe UI", 11, "bold"),
                                              command=lambda: self._switch_tab("diagnose"))
        self.tab_diagnose_btn.pack(side="left")

        self.tab_history_btn = ctk.CTkButton(self.tab_bar, text="📋  History", width=140, height=36,
                                             fg_color=PANEL, hover_color=BORDER, corner_radius=0,
                                             font=ctk.CTkFont("Segoe UI", 11),
                                             command=lambda: self._switch_tab("history"))
        self.tab_history_btn.pack(side="left")

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(fill="both", expand=True)

        self._build_diagnose_tab()
        self._build_history_tab()
        self._switch_tab("diagnose")

        # Disclaimer footer
        footer = ctk.CTkFrame(self, fg_color="#1A0A0A", corner_radius=0, height=28)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="⚠️  This tool does NOT replace professional medical advice. Always consult a licensed doctor.",
                     font=ctk.CTkFont("Segoe UI", 9), text_color="#EF4444").pack(pady=5)

    def _switch_tab(self, tab):
        if tab == "diagnose":
            self.diagnose_frame.pack(fill="both", expand=True)
            self.history_frame.pack_forget()
            self.tab_diagnose_btn.configure(fg_color=ACCENT)
            self.tab_history_btn.configure(fg_color=PANEL)
        else:
            self.history_frame.pack(fill="both", expand=True)
            self.diagnose_frame.pack_forget()
            self.tab_diagnose_btn.configure(fg_color=PANEL)
            self.tab_history_btn.configure(fg_color=ACCENT)
            self._load_history()

    def _build_diagnose_tab(self):
        self.diagnose_frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)

        body = ctk.CTkFrame(self.diagnose_frame, fg_color=BG, corner_radius=0)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        # ── Left panel ──────────────────────
        left = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=10, width=300)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="Select Symptoms",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"), text_color=WHITE).pack(anchor="w", padx=14, pady=(12, 4))

        # Search
        self.search_entry = ctk.CTkEntry(left, textvariable=self.search_var,
                                         placeholder_text="🔍  Search symptoms...",
                                         fg_color=BORDER, border_color=ACCENT,
                                         text_color=WHITE, height=36)
        self.search_entry.pack(fill="x", padx=12, pady=(0, 8))

        # Symptom count label
        self.count_label = ctk.CTkLabel(left, text=f"{len(ALL_SYMPTOMS)} symptoms available",
                                         font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED)
        self.count_label.pack(anchor="w", padx=14)

        # Scrollable checkboxes
        scroll = ctk.CTkScrollableFrame(left, fg_color=CARD_BG, corner_radius=6)
        scroll.pack(fill="both", expand=True, padx=10, pady=8)

        for symptom in ALL_SYMPTOMS:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(scroll, text=symptom.title(),
                                  variable=var,
                                  font=ctk.CTkFont("Segoe UI", 11),
                                  text_color=WHITE,
                                  fg_color=ACCENT,
                                  hover_color="#2563EB",
                                  checkmark_color=WHITE)
            cb.pack(anchor="w", padx=6, pady=2)
            self.symptom_vars[symptom] = var
            self.checkbox_widgets[symptom] = cb

        # Buttons
        ctk.CTkButton(left, text="✅  Diagnose",
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      fg_color=ACCENT, hover_color="#2563EB", height=40,
                      command=self.diagnose).pack(fill="x", padx=12, pady=(4, 4))

        ctk.CTkButton(left, text="📄  Export PDF",
                      font=ctk.CTkFont("Segoe UI", 11),
                      fg_color="#1F2937", hover_color="#374151", height=36,
                      command=self.export_pdf).pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkButton(left, text="🔄  Clear All",
                      font=ctk.CTkFont("Segoe UI", 11),
                      fg_color="#1F2937", hover_color="#374151", height=36,
                      command=self.clear_all).pack(fill="x", padx=12, pady=(0, 10))

        # ── Right panel ─────────────────────
        right = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=10)
        right.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(right, text="Diagnosis Results",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"), text_color=WHITE).pack(anchor="w", padx=16, pady=(12, 4))

        self.result_scroll = ctk.CTkScrollableFrame(right, fg_color=BG, corner_radius=6)
        self.result_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._show_placeholder()

    def _build_history_tab(self):
        self.history_frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)

        ctk.CTkLabel(self.history_frame, text="📋  Diagnosis History",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"), text_color=WHITE).pack(anchor="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(self.history_frame, text="Last 20 diagnoses saved on this device",
                     font=ctk.CTkFont("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=20)

        self.history_scroll = ctk.CTkScrollableFrame(self.history_frame, fg_color=PANEL, corner_radius=10)
        self.history_scroll.pack(fill="both", expand=True, padx=16, pady=12)

    def _load_history(self):
        for w in self.history_scroll.winfo_children():
            w.destroy()

        rows = get_history()
        if not rows:
            ctk.CTkLabel(self.history_scroll, text="No history yet. Run a diagnosis first!",
                         font=ctk.CTkFont("Segoe UI", 12), text_color=MUTED).pack(pady=40)
            return

        for row in rows:
            ts, syms, diag, score, sev = row
            color = SEVERITY_COLOR.get(sev, MUTED)
            card = ctk.CTkFrame(self.history_scroll, fg_color=CARD_BG, corner_radius=8)
            card.pack(fill="x", padx=6, pady=4)

            top = ctk.CTkFrame(card, fg_color=color, corner_radius=0, height=32)
            top.pack(fill="x")
            top.pack_propagate(False)
            ctk.CTkLabel(top, text=f"  {diag}  —  {score}%  confidence",
                         font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=WHITE).pack(side="left", padx=8)
            ctk.CTkLabel(top, text=f"{SEVERITY_ICON.get(sev,'')} {sev}  ",
                         font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=WHITE).pack(side="right", padx=8)

            ctk.CTkLabel(card, text=f"🕐 {ts}",
                         font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED).pack(anchor="w", padx=10, pady=(4, 0))
            ctk.CTkLabel(card, text=f"Symptoms: {syms}",
                         font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED,
                         wraplength=900, justify="left").pack(anchor="w", padx=10, pady=(0, 6))

    # ── Helpers ──────────────────────────────
    def _show_placeholder(self):
        for w in self.result_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.result_scroll,
                     text="Select symptoms on the left\nand click  ✅ Diagnose",
                     font=ctk.CTkFont("Segoe UI", 14), text_color=MUTED,
                     justify="center").pack(expand=True, pady=100)

    def filter_symptoms(self, *args):
        query = self.search_var.get().lower()
        for symptom, cb in self.checkbox_widgets.items():
            if query in symptom.lower():
                cb.pack(anchor="w", padx=6, pady=2)
            else:
                cb.pack_forget()

    def clear_all(self):
        for var in self.symptom_vars.values():
            var.set(False)
        self.last_results = []
        self.last_symptoms = []
        self._show_placeholder()

    def export_pdf(self):
        if not self.last_results:
            messagebox.showwarning("No Results", "Please run a diagnosis first before exporting.")
            return
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"symptom_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        try:
            export_pdf(self.last_symptoms, self.last_results, path)
            messagebox.showinfo("PDF Exported", f"Report saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    # ── Diagnosis ────────────────────────────
    def diagnose(self):
        selected = [s for s, v in self.symptom_vars.items() if v.get()]

        for w in self.result_scroll.winfo_children():
            w.destroy()

        if not selected:
            messagebox.showwarning("No Symptoms", "Please select at least one symptom.")
            return

        results = run_inference(selected)
        self.last_results = results
        self.last_symptoms = selected

        if results:
            save_to_db(selected, results)

        # Symptoms summary
        summary = ctk.CTkFrame(self.result_scroll, fg_color=CARD_BG, corner_radius=8)
        summary.pack(fill="x", padx=6, pady=(4, 8))
        ctk.CTkLabel(summary, text=f"📋  {len(selected)} symptoms selected:",
                     font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=GREEN).pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(summary, text=",  ".join(s.title() for s in selected),
                     font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED,
                     wraplength=680, justify="left").pack(anchor="w", padx=10, pady=(0, 6))

        if not results:
            ctk.CTkLabel(self.result_scroll,
                         text="❌  No matching conditions found.\nTry selecting more symptoms.",
                         font=ctk.CTkFont("Segoe UI", 12), text_color=RED).pack(pady=30)
            return

        ctk.CTkLabel(self.result_scroll, text="Top Possible Conditions",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"), text_color=WHITE).pack(anchor="w", padx=8, pady=(0, 4))

        # Bar chart
        self._render_bar_chart(results)

        # Result cards
        for i, res in enumerate(results):
            self._render_card(res, i)

        ctk.CTkLabel(self.result_scroll,
                     text="ℹ️  Higher confidence = more symptom overlap with known disease profile.",
                     font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED).pack(pady=(8, 4))

    def _render_bar_chart(self, results):
        chart_frame = ctk.CTkFrame(self.result_scroll, fg_color=CARD_BG, corner_radius=8)
        chart_frame.pack(fill="x", padx=6, pady=(0, 10))

        ctk.CTkLabel(chart_frame, text="📊  Confidence Overview",
                     font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=WHITE).pack(anchor="w", padx=12, pady=(8, 6))

        for res in results:
            color = SEVERITY_COLOR.get(res["severity"], MUTED)
            row = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=0)
            row.pack(fill="x", padx=12, pady=3)

            name_lbl = ctk.CTkLabel(row, text=res["disease"][:28],
                                     font=ctk.CTkFont("Segoe UI", 10), text_color=WHITE, width=200, anchor="w")
            name_lbl.pack(side="left")

            bar_container = ctk.CTkFrame(row, fg_color=BORDER, corner_radius=4, height=16, width=320)
            bar_container.pack(side="left", padx=8)
            bar_container.pack_propagate(False)

            fill_w = max(int(res["score"] / 100 * 320), 8)
            fill = ctk.CTkFrame(bar_container, fg_color=color, corner_radius=4, height=16, width=fill_w)
            fill.place(x=0, y=0)

            ctk.CTkLabel(row, text=f"{res['score']}%",
                         font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=color, width=50).pack(side="left")

        ctk.CTkFrame(chart_frame, fg_color=CARD_BG, height=6).pack()

    def _render_card(self, res, index):
        color = SEVERITY_COLOR.get(res["severity"], MUTED)

        card = ctk.CTkFrame(self.result_scroll, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=color)
        card.pack(fill="x", padx=6, pady=5)

        # Header bar
        top = ctk.CTkFrame(card, fg_color=color, corner_radius=0, height=36)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(top, text=f"  #{index+1}  {res['disease']}",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"), text_color=WHITE).pack(side="left", padx=6)
        ctk.CTkLabel(top, text=f"{SEVERITY_ICON.get(res['severity'],'')} {res['severity']}  ",
                     font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=WHITE).pack(side="right", padx=6)

        body = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=0)
        body.pack(fill="x", padx=12, pady=8)

        # Likely / Possible
        likely_text = "✅  Likely" if res["likely"] else "⚠️  Possible"
        likely_color = GREEN if res["likely"] else ORANGE
        ctk.CTkLabel(body, text=f"{likely_text}   —   {res['match_count']} of {res['total_symptoms']} symptoms matched  (needs {res['required']}+)",
                     font=ctk.CTkFont("Segoe UI", 10), text_color=likely_color).pack(anchor="w")

        # Matched symptoms
        ctk.CTkLabel(body, text="Matched: " + ", ".join(s.title() for s in res["matched"]),
                     font=ctk.CTkFont("Segoe UI", 9), text_color=MUTED,
                     wraplength=640, justify="left").pack(anchor="w", pady=(2, 6))

        # Advice
        adv = ctk.CTkFrame(body, fg_color=BORDER, corner_radius=6)
        adv.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(adv, text="💊  Recommendation:",
                     font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=ACCENT).pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(adv, text=res["advice"],
                     font=ctk.CTkFont("Segoe UI", 10), text_color=WHITE,
                     wraplength=640, justify="left").pack(anchor="w", padx=10, pady=(0, 8))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = SymptomCheckerApp()
    app.mainloop()
