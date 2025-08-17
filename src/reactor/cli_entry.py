from __future__ import annotations

# Thin wrappers to call existing script main() functions.

def _run(module: str, func: str = "main") -> None:  # pragma: no cover (thin wrapper)
    mod = __import__(module, fromlist=[func])
    getattr(mod, func)()


def plot_production_fom() -> None:
    _run("scripts.plot_production_fom")


def plot_stability() -> None:
    _run("scripts.plot_stability")


def run_report() -> None:
    _run("scripts.run_report")


def production_kpi() -> None:
    _run("scripts.production_kpi")


def sweep_time() -> None:
    _run("scripts.param_sweep_confinement")


def sweep_dynamic_ripple() -> None:
    _run("scripts.param_sweep_confinement")


def hardware_runner() -> None:
    _run("scripts.hardware_runner")


def sensor_noise() -> None:
    _run("scripts.sensor_noise_model")


def bench_step_loop() -> None:
    _run("scripts.bench_step_loop")


def build_artifacts() -> None:
    # One-shot builder: demo + report + KPI + plots used by the dashboard
    import os, sys, json
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), ".."))
    from scripts import demo_runner, generate_feasibility_report, run_report as rr, production_kpi as kpi
    from scripts import plot_production_fom as pf, plot_stability as ps, generate_progress_dashboard as dash

    # Demo run (minimal)
    demo_runner.main()
    # Feasibility
    generate_feasibility_report.main()
    # Integrated report
    rr.main()
    # KPI
    kpi.main()
    # Plots
    pf.main()
    ps.main()
    # Dashboard
    dash.main()
    print(json.dumps({"ok": True, "built": [
        "feasibility_gates_report.json","integrated_report.json","production_kpi.json",
        "production_fom_yield.png","stability.png","progress_dashboard.html"
    ]}))


def generate_timeline_anomalies() -> None:
    _run("scripts.generate_timeline_anomalies")


def validate_schemas() -> None:
    _run("scripts.validate_schemas")
