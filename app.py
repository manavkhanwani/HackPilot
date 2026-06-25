"""HackPilot – main Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from hackpilot.ai_provider import (
    OLLAMA_DEFAULT_MODELS,
    ConfigurationError,
    Provider,
)
from hackpilot.features.feasibility import analyze_feasibility
from hackpilot.features.idea_generator import generate_ideas
from hackpilot.features.pitch import generate_pitch
from hackpilot.features.planner import build_plan
from hackpilot.features.readme_gen import generate_readme
from hackpilot.language import LANGUAGE_OPTIONS, Language
from hackpilot.models import HackathonContext, ProjectIdea
from hackpilot.pipeline import PipelineResult, run_pipeline

st.set_page_config(page_title="HackPilot", page_icon="🚀", layout="wide")
st.title("🚀 HackPilot")
st.caption("Your AI-powered hackathon copilot.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Language selector ──────────────────────────────────────────────────
    st.header("🌐 Language")
    selected_lang_str: str = st.selectbox(
        "Output language",
        LANGUAGE_OPTIONS,
        index=0,
        help="All AI-generated content will be in this language.",
    )
    language = Language(selected_lang_str)

    st.divider()

    # ── AI Provider selector ───────────────────────────────────────────────
    st.header("🤖 AI Provider")
    provider_options = [p.value for p in Provider]
    selected_provider_str: str = st.selectbox(
        "Provider",
        provider_options,
        index=0,
        help="Gemini uses Google Cloud; Ollama runs models locally.",
    )
    provider = Provider(selected_provider_str)

    gemini_api_key: str = ""
    ollama_model: str = OLLAMA_DEFAULT_MODELS[0]

    if provider is Provider.GEMINI:
        # ── BYOK: Bring Your Own Key ───────────────────────────────────────
        byok = st.text_input(
            "Gemini API Key (optional)",
            type="password",
            placeholder="Leave blank to use secrets",
            help=(
                "Paste your own Gemini key here. "
                "If blank, the key from Streamlit secrets is used. "
                "Your key is never logged or stored."
            ),
        )
        gemini_api_key = byok  # may be empty string; resolution happens in ai_provider

    else:  # Ollama
        available_models = OLLAMA_DEFAULT_MODELS.copy()
        custom_model = st.text_input(
            "Custom Ollama model (optional)",
            placeholder="e.g. codellama:13b",
            help="Leave blank to pick from the list below.",
        )
        if custom_model.strip():
            available_models = [custom_model.strip()] + available_models

        ollama_model = st.selectbox(
            "Ollama model",
            available_models,
            index=0,
        )
        st.caption(
            "Make sure Ollama is running locally: `ollama serve`  \n"
            f"Model in use: `{ollama_model}`"
        )

    st.divider()

    # ── Hackathon context ──────────────────────────────────────────────────
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


# ── Shared kwargs forwarded to every feature call ─────────────────────────────
_ai_kwargs: dict = dict(
    provider=provider,
    gemini_api_key=gemini_api_key,
    ollama_model=ollama_model,
    language=language,


    
)


def _handle_config_error(exc: Exception) -> None:
    """Display a friendly error for configuration issues and stop execution."""
    if isinstance(exc, ConfigurationError):
        st.error(str(exc))
        if provider is Provider.GEMINI:
            st.info(
                "💡 Add `GEMINI_API_KEY` to your Streamlit secrets, "
                "or enter a key in the sidebar."
            )
    else:
        st.error(f"Unexpected error: {exc}")
    st.stop()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["💡 Ideas", "🔍 Feasibility", "🗓 Plan", "🎤 Pitch", "📄 README", "⚡ Pipeline"])

# ── Tab 1 – Idea Generator ────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("💡 Idea Generator")

    if not ctx.theme.strip():
        st.warning("Enter a hackathon theme in the sidebar to get started.")
    else:
        if st.button("Generate Ideas", type="primary", key="gen_ideas"):
            with st.spinner("Generating ideas…"):
                try:
                    st.session_state["ideas"] = generate_ideas(
                                                                    ctx,
                                                                    api_key=gemini_api_key,
                                                                    provider=provider,
                                                                    ollama_model=ollama_model,
                                                                    language=language,
                                                                )
                    st.session_state["selected_idea"] = None
                    for key in ("feasibility", "plan", "pitch", "readme"):
                        st.session_state.pop(key, None)
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)

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
            with st.spinner("Analyzing feasibility…"):
                try:
                    st.session_state["feasibility"] = analyze_feasibility(
                        selected_f2, ctx, **_ai_kwargs
                    )
                    for key in ("plan", "pitch", "readme"):
                        st.session_state.pop(key, None)
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)

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
            with st.spinner("Building execution plan…"):
                try:
                    st.session_state["plan"] = build_plan(
                        selected_p, feasibility_p, ctx, **_ai_kwargs
                    )
                    for key in ("pitch", "readme"):
                        st.session_state.pop(key, None)
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)

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
            with st.spinner("Crafting your pitch…"):
                try:
                    st.session_state["pitch"] = generate_pitch(
                        selected_p4, plan_p4, **_ai_kwargs
                    )
                    st.session_state.pop("readme", None)
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)

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
            with st.spinner("Writing your README…"):
                try:
                    st.session_state["readme"] = generate_readme(
                        selected_p5, plan_p5, ctx, **_ai_kwargs
                    )
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)

        readme = st.session_state.get("readme")
        if readme is not None:
            st.markdown("**Preview**")
            with st.expander("Rendered preview", expanded=True):
                st.markdown(readme.markdown)
            st.code(readme.markdown, language="markdown")
            st.caption("Copy the block above and paste into your repo's README.md.")

# ── Tab 6 – Pipeline (end-to-end auto-run) ────────────────────────────────────
with tabs[5]:
    st.subheader("⚡ Full Pipeline")
    st.caption(
        "Runs all five features back-to-back on your hackathon context. "
        "Each step has an automated gate check — a failing gate stops the pipeline early."
    )

    if not ctx.theme.strip():
        st.warning("Enter a hackathon theme in the sidebar first.")
    else:
        if st.button("🚀 Run Full Pipeline", type="primary", key="run_pipeline"):
            st.session_state.pop("pipeline_result", None)

            # Live status placeholder
            status_box = st.empty()
            step_labels = [
                "Idea Generator",
                "Feasibility Analyzer",
                "Execution Planner",
                "Elevator Pitch",
                "README Generator",
            ]

            with st.spinner("Pipeline running…"):
                # Show a live progress indicator while the pipeline runs
                progress = st.progress(0)
                status_box.info("🔄 Starting pipeline…")

                try:
                    pipeline_result: PipelineResult = run_pipeline(
                        ctx,
                        provider=provider,
                        gemini_api_key=gemini_api_key,
                        ollama_model=ollama_model,
                        language=language,
                    )
                    st.session_state["pipeline_result"] = pipeline_result
                    progress.progress(100)
                    status_box.empty()
                except (ConfigurationError, RuntimeError) as e:
                    _handle_config_error(e)
                except Exception as e:
                    st.error(f"Pipeline error: {e}")

        pr: PipelineResult | None = st.session_state.get("pipeline_result")

        if pr is not None:
            # ── Summary banner ────────────────────────────────────────────────
            total_steps = len(pr.steps)
            passed_steps = sum(1 for s in pr.steps if s.success and s.all_gates_passed)

            if pr.succeeded:
                st.success(f"✅ Pipeline complete — all {total_steps}/5 steps passed.")
            else:
                st.error(
                    f"❌ Pipeline stopped at step {total_steps}/5. "
                    f"{passed_steps} step(s) passed."
                )

            st.divider()

            # ── Per-step breakdown ────────────────────────────────────────────
            step_icons = ["💡", "🔍", "🗓", "🎤", "📄"]
            for idx, step in enumerate(pr.steps):
                icon = step_icons[idx] if idx < len(step_icons) else "🔷"
                gate_summary = (
                    f"{step.gates_passed}/{len(step.gates)} gate(s) passed"
                    if step.gates
                    else "no gates run"
                )
                header_status = "✅" if (step.success and step.all_gates_passed) else "❌"

                with st.expander(
                    f"{header_status} Step {idx + 1}: {icon} {step.step_name} "
                    f"— {gate_summary} · {step.elapsed_s:.1f}s",
                    expanded=not (step.success and step.all_gates_passed),
                ):
                    if not step.success:
                        st.error(f"Step failed: {step.error}")
                    else:
                        # Show each gate result
                        for gate in step.gates:
                            if gate.passed:
                                st.success(f"✅ **{gate.name}**: {gate.message}")
                            else:
                                st.error(f"❌ **{gate.name}**: {gate.message}")
                                if gate.detail:
                                    st.caption(gate.detail)

                        # Step-specific output previews
                        if step.step_name == "Idea Generator" and isinstance(step.output, list):
                            st.markdown(f"**Top idea selected:** {step.output[0].title}")
                            st.caption(step.output[0].solution_summary)

                        elif step.step_name == "Feasibility Analyzer" and step.output:
                            rep = step.output
                            verdict = "✅ Feasible" if rep.is_feasible else "⚠️ Risky"
                            c1, c2 = st.columns(2)
                            c1.metric("Verdict", verdict)
                            c2.metric("Confidence", f"{rep.confidence}/10")

                        elif step.step_name == "Execution Planner" and step.output:
                            p = step.output
                            st.markdown(
                                f"**MVP scope:** {len(p.mvp_scope)} feature(s) · "
                                f"**Milestones:** {len(p.milestones)}"
                            )

                        elif step.step_name == "Elevator Pitch" and step.output:
                            st.markdown(f"*{step.output.tagline}*")

                        elif step.step_name == "README Generator" and step.output:
                            st.code(step.output.markdown[:400] + "…", language="markdown")

            # ── Sync pipeline outputs back to session state for other tabs ────
            if pr.succeeded:
                st.divider()
                st.markdown("**Pipeline outputs loaded into all tabs automatically.**")
                if pr.final_idea:
                    st.session_state["selected_idea"] = pr.final_idea
                    st.session_state["ctx"] = ctx
                    st.session_state["ideas"] = (
                        pr.steps[0].output if isinstance(pr.steps[0].output, list) else [pr.final_idea]
                    )
                if pr.final_feasibility:
                    st.session_state["feasibility"] = pr.final_feasibility
                if pr.final_plan:
                    st.session_state["plan"] = pr.final_plan
                if pr.final_pitch:
                    st.session_state["pitch"] = pr.final_pitch
                if pr.final_readme:
                    st.session_state["readme"] = pr.final_readme
                st.info("💡 Switch to any tab to view, copy, or iterate on individual results.")
