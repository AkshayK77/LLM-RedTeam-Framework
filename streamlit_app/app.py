import os
import requests
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

API_BASE = "http://localhost:8080"
GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
    "allam-2-7b",
]

CATEGORIES = [
    "roleplay_persona",
    "privilege_escalation",
    "encoding_tricks",
    "many_shot",
    "multilingual",
    "narrative_fictional",
]

st.set_page_config(page_title="LLM Red-Teaming Framework", layout="wide")
st.title("LLM Red-Teaming Framework")

tab1, tab2 = st.tabs(["Run Benchmark", "Interactive Test"])

# ── Tab 1: Run Benchmark ──────────────────────────────────────────────────────
with tab1:
    st.header("Run Benchmark")

    selected_model = st.selectbox("Select Model", MODELS, key="bench_model")
    selected_categories = st.multiselect(
        "Attack Categories", CATEGORIES, default=CATEGORIES, key="bench_cats"
    )

    if st.button("Run Benchmark", type="primary"):
        if not selected_categories:
            st.error("Select at least one attack category.")
        else:
            try:
                resp = requests.post(
                    f"{API_BASE}/jobs",
                    json={"model_id": selected_model, "categories": selected_categories},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                st.session_state["job_id"] = data["job_id"]
                st.success(f"Job submitted: `{data['job_id']}`")
            except Exception as e:
                st.error(f"Failed to submit job: {e}")

    # Fragment auto-reruns every 3s independently — does NOT rerun the full app,
    # so Tab 2 stays fully interactive while a benchmark is running.
    @st.fragment(run_every=3)
    def job_status_panel():
        if "job_id" not in st.session_state:
            return

        job_id = st.session_state["job_id"]
        st.subheader(f"Job: `{job_id}`")

        try:
            r = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
            r.raise_for_status()
            job_data = r.json()
            status = job_data.get("status", "unknown")
        except Exception as e:
            st.error(f"Poll error: {e}")
            return

        if status == "complete":
            st.success("Status: **complete**")

            asr_table = job_data.get("asr_table", {})
            if asr_table:
                import pandas as pd

                df = pd.DataFrame(
                    list(asr_table.items()), columns=["Category", "ASR"]
                ).set_index("Category")

                def color_asr(val):
                    r_val = int(255 * val)
                    g_val = int(255 * (1 - val))
                    return f"background-color: rgb({r_val},{g_val},80)"

                st.dataframe(df.style.applymap(color_asr, subset=["ASR"]))

            if st.button("View Full Report", key="view_report"):
                try:
                    rep = requests.get(f"{API_BASE}/reports/{job_id}", timeout=10)
                    rep.raise_for_status()
                    report = rep.json()

                    st.subheader("Full Report")
                    st.metric("Mean ASR", f"{report['mean_asr']:.1%}")
                    col1, col2 = st.columns(2)
                    col1.metric("Weakest Category (highest ASR)", report["weakest_category"])
                    col2.metric("Strongest Category (lowest ASR)", report["strongest_category"])

                    st.subheader("Baseline Comparison")
                    rows = []
                    for cat, vals in report["comparison_to_baseline"].items():
                        rows.append(
                            {
                                "Category": cat,
                                "Model ASR": f"{vals['model_asr']:.1%}",
                                "Baseline ASR": f"{vals['baseline_asr']:.1%}"
                                if vals["baseline_asr"] is not None
                                else "N/A",
                                "Delta": f"{vals['delta']:+.1%}"
                                if vals["delta"] is not None
                                else "N/A",
                            }
                        )
                    import pandas as pd
                    st.dataframe(pd.DataFrame(rows).set_index("Category"))
                except Exception as e:
                    st.error(f"Failed to fetch report: {e}")

        elif status == "failed":
            st.error("Status: **failed**")
        else:
            st.info(f"Status: **{status}**")

    job_status_panel()

# ── Tab 2: Interactive Test ───────────────────────────────────────────────────
with tab2:
    st.header("Interactive Test")

    it_model = st.selectbox("Select Model", MODELS, key="it_model")
    prompt_source = st.radio(
        "Prompt Source", ["Type a custom prompt", "Choose from OSB-Bench library"]
    )

    prompt_text = ""

    if prompt_source == "Type a custom prompt":
        prompt_text = st.text_area("Enter your prompt", height=150, key="custom_prompt")
    else:
        try:
            all_prompts = requests.get(f"{API_BASE}/prompts", timeout=10).json()
        except Exception as e:
            st.error(f"Could not load prompts: {e}")
            all_prompts = {}

        if all_prompts:
            cat_choice = st.selectbox("Category", list(all_prompts.keys()), key="it_cat")
            cat_prompts = all_prompts.get(cat_choice, [])
            if cat_prompts:
                prompt_labels = [
                    f"{p['prompt_id']} — {p.get('harmful_request') or p['text'][:60]}"
                    for p in cat_prompts
                ]
                prompt_idx = st.selectbox(
                    "Select Prompt",
                    range(len(prompt_labels)),
                    format_func=lambda i: prompt_labels[i],
                    key="it_prompt_sel",
                )
                prompt_text = cat_prompts[prompt_idx]["text"]
                st.text_area("Selected Prompt (preview)", value=prompt_text, height=100, disabled=True)

    if st.button("Run", type="primary", key="it_run"):
        if not prompt_text.strip():
            st.warning("Enter or select a prompt first.")
        else:
            with st.spinner("Getting completion…"):
                try:
                    resp = GROQ_CLIENT.chat.completions.create(
                        model=it_model,
                        messages=[{"role": "user", "content": prompt_text}],
                        max_tokens=512,
                        temperature=0.7,
                    )
                    completion = resp.choices[0].message.content
                except Exception as e:
                    st.error(f"Groq API error: {e}")
                    completion = None

            if completion:
                st.subheader("Model Completion")
                st.text_area("Response", value=completion, height=200, disabled=True)

                with st.spinner("Classifying…"):
                    try:
                        cr = requests.post(
                            f"{API_BASE}/classify",
                            json={"prompt_text": prompt_text, "completion": completion},
                            timeout=30,
                        )
                        cr.raise_for_status()
                        verdict = cr.json()
                    except Exception as e:
                        st.error(f"Classifier error: {e}")
                        verdict = None

                if verdict:
                    score = verdict.get("score", 0)
                    flagged = verdict.get("flagged", False)
                    reasoning = verdict.get("reasoning", "")

                    if score == 1:
                        st.error("Jailbreak Detected")
                    else:
                        st.success("Refused")

                    if flagged:
                        st.warning("Partial Compliance — Flagged for Review")

                    st.caption(f"**Reasoning:** {reasoning}")
