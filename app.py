"""HackPilot – main Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from hackpilot.features.feasibility import analyze_feasibility
from hackpilot.features.idea_generator import generate_ideas
from hackpilot.features.pitch import generate_pitch
from hackpilot.features.planner import build_plan
from hackpilot.features.readme_gen import generate_readme
from hackpilot.models import HackathonContext, ProjectIdea

st.set_page_config(page_title="HackPilot", page_icon="🚀", layout="wide")
st.title("🚀 HackPilot")
st.caption("Your AI-powered hackathon copilot.")

# ── Sidebar: hackathon context ────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Hackathon Context")
    theme = st.text_input("Theme", placeholder="e.g. Sustainable Cities")
    team_size = st.number_input("Team size", min_value=1, max_value=5, value=2, step=1)
    duration = st.selectbox("Duration (hours)", [12, 24, 36, 48], index=1)
    tech_input = st.text_input(
        "Preferred technologies",
        placeholder="e.g. Python, React, Firebase",
    )
    preferred_tech = [t.strip() for t in tech_input.split(",") if t.strip()]

    ctx = HackathonContext(
        theme=theme,
        team_size=int(team_size),
        duration_hours=int(duration),
        preferred_tech=preferred_tech,
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["💡 Ideas", "🔍 Feasibility", "🗓 Plan", "🎤 Pitch", "📄 README"])

# ── Tab 1 – Idea Generator ────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("💡 Idea Generator")

    if not ctx.theme.strip():
        st.warning("Enter a hackathon theme in the sidebar to get started.")
    else:
        if st.button("Generate Ideas", type="primary", key="gen_ideas"):
            try:
                api_key: str = st.secrets["GEMINI_API_KEY"]
            except KeyError:
                st.error("GEMINI_API_KEY not found in Streamlit secrets.")
                st.stop()

            with st.spinner("Generating ideas with Gemini…"):
                try:
                    st.session_state["ideas"] = generate_ideas(ctx, api_key)
                    st.session_state["selected_idea"] = None
                    # Clear downstream state
                    for key in ("feasibility", "plan", "pitch", "readme"):
                        st.session_state.pop(key, None)
                except Exception as e:
                    st.error(f"Generation failed: {e}")
                    st.stop()

        ideas: list[ProjectIdea] = st.session_state.get("ideas", [])
        if ideas:
            st.markdown("### Select an idea to continue")
            for i, idea in enumerate(ideas):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([6, 2, 2])
                    with col1:
                        st.markdown(f"**{idea.title}**")
                        st.caption(idea.problem_statement)
                        st.write(idea.solution_summary)
                    with col2:
                        diff_color = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
                        st.metric(
                            "Difficulty",
                            f"{diff_color.get(idea.difficulty, '')} {idea.difficulty}",
                        )
                        st.metric("Innovation", f"{idea.innovation_score}/10")
                    with col3:
                        if st.button("Select", key=f"select_{i}"):
                            st.session_state["selected_idea"] = idea
                            st.session_state["ctx"] = ctx
                            for key in ("feasibility", "plan", "pitch", "readme"):
                                st.session_state.pop(key, None)

            selected = st.session_state.get("selected_idea")
            if selected:
                st.success(
                    f"✅ Selected: **{selected.title}** — head to the Feasibility tab."
                )

# ── Tab 2 – Feasibility Analyzer ─────────────────────────────────────────────
with tabs[1]:
    st.subheader("🔍 Feasibility Analyzer")
    selected_f2: ProjectIdea | None = st.session_state.get("selected_idea")

    if selected_f2 is None:
        st.warning("Select an idea on the Ideas tab first.")
    else:
        st.markdown(f"**Analyzing:** {selected_f2.title}")
        if st.button("Run Feasibility Check", type="primary", key="run_feasibility"):
            try:
                api_key_f2: str = st.secrets["GEMINI_API_KEY"]
            except KeyError:
                st.error("GEMINI_API_KEY not found in Streamlit secrets.")
                st.stop()
            with st.spinner("Analyzing feasibility…"):
                try:
                    st.session_state["feasibility"] = analyze_feasibility(
                        selected_f2, ctx, api_key_f2
                    )
                    for key in ("plan", "pitch", "readme"):
                        st.session_state.pop(key, None)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.stop()

        report = st.session_state.get("feasibility")
        if report is not None:
            verdict = "✅ Feasible" if report.is_feasible else "⚠️ Risky"
            col1, col2 = st.columns(2)
            col1.metric("Verdict", verdict)
            col2.metric("Confidence", f"{report.confidence}/10")

            with st.container(border=True):
                st.markdown("**Risks**")
                for r in report.risks:
                    st.markdown(f"- {r}")

            with st.container(border=True):
                st.markdown("**Recommendations**")
                for r in report.recommendations:
                    st.markdown(f"- {r}")

            st.success("Feasibility done — head to the Plan tab.")

# ── Tab 3 – Execution Planner ─────────────────────────────────────────────────
with tabs[2]:
    st.subheader("🗓 Execution Planner")
    selected_p: ProjectIdea | None = st.session_state.get("selected_idea")
    feasibility_p = st.session_state.get("feasibility")

    if selected_p is None:
        st.warning("Select an idea on the Ideas tab first.")
    elif feasibility_p is None:
        st.warning("Run the Feasibility Check first.")
    else:
        st.markdown(f"**Planning:** {selected_p.title}")
        if st.button("Generate Plan", type="primary", key="gen_plan"):
            try:
                api_key_f3: str = st.secrets["GEMINI_API_KEY"]
            except KeyError:
                st.error("GEMINI_API_KEY not found in Streamlit secrets.")
                st.stop()
            with st.spinner("Building execution plan…"):
                try:
                    st.session_state["plan"] = build_plan(
                        selected_p, feasibility_p, ctx, api_key_f3
                    )
                    for key in ("pitch", "readme"):
                        st.session_state.pop(key, None)
                except Exception as e:
                    st.error(f"Planning failed: {e}")
                    st.stop()

        plan = st.session_state.get("plan")
        if plan is not None:
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("**MVP Scope**")
                    for f in plan.mvp_scope:
                        st.markdown(f"- {f}")
            with col2:
                with st.container(border=True):
                    st.markdown("**Stretch Goals**")
                    for g in plan.stretch_goals:
                        st.markdown(f"- {g}")

            st.markdown("**Milestones**")
            for ms in plan.milestones:
                with st.container(border=True):
                    st.markdown(f"⏱ **H+{ms.time_offset_hours}h** — {ms.title}")
                    st.caption(ms.description)

            st.success("Plan ready — head to the Pitch tab.")

# ── Tab 4 – Elevator Pitch ────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("🎤 Elevator Pitch Generator")
    selected_p4: ProjectIdea | None = st.session_state.get("selected_idea")
    plan_p4 = st.session_state.get("plan")

    if selected_p4 is None:
        st.warning("Select an idea on the Ideas tab first.")
    elif plan_p4 is None:
        st.warning("Generate an execution plan first.")
    else:
        st.markdown(f"**Pitching:** {selected_p4.title}")
        if st.button("Generate Pitch", type="primary", key="gen_pitch"):
            try:
                api_key_f4: str = st.secrets["GEMINI_API_KEY"]
            except KeyError:
                st.error("GEMINI_API_KEY not found in Streamlit secrets.")
                st.stop()
            with st.spinner("Crafting your pitch…"):
                try:
                    st.session_state["pitch"] = generate_pitch(
                        selected_p4, plan_p4, api_key_f4
                    )
                    st.session_state.pop("readme", None)
                except Exception as e:
                    st.error(f"Pitch generation failed: {e}")
                    st.stop()

        pitch = st.session_state.get("pitch")
        if pitch is not None:
            with st.container(border=True):
                st.markdown(f"### 🏷️ _{pitch.tagline}_")
            with st.container(border=True):
                st.markdown("**60-second pitch**")
                st.write(pitch.pitch_text)
                st.code(pitch.pitch_text, language=None)
            st.success("Pitch ready — head to the README tab.")

# ── Tab 5 – README Generator ──────────────────────────────────────────────────
with tabs[4]:
    st.subheader("📄 README Generator")
    selected_p5: ProjectIdea | None = st.session_state.get("selected_idea")
    plan_p5 = st.session_state.get("plan")

    if selected_p5 is None:
        st.warning("Select an idea on the Ideas tab first.")
    elif plan_p5 is None:
        st.warning("Generate an execution plan first.")
    else:
        st.markdown(f"**Generating README for:** {selected_p5.title}")
        if st.button("Generate README", type="primary", key="gen_readme"):
            try:
                api_key_f5: str = st.secrets["GEMINI_API_KEY"]
            except KeyError:
                st.error("GEMINI_API_KEY not found in Streamlit secrets.")
                st.stop()
            with st.spinner("Writing your README…"):
                try:
                    st.session_state["readme"] = generate_readme(
                        selected_p5, plan_p5, ctx, api_key_f5
                    )
                except Exception as e:
                    st.error(f"README generation failed: {e}")
                    st.stop()

        readme = st.session_state.get("readme")
        if readme is not None:
            st.markdown("**Preview**")
            with st.expander("Rendered preview", expanded=True):
                st.markdown(readme.markdown)
            st.code(readme.markdown, language="markdown")
            st.caption("Copy the block above and paste into your repo's README.md.")
