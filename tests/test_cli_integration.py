import json
import subprocess
import sys


def test_cli_demo_and_gate(tmp_path):
    # demo without timeline file (prints JSON)
    out = subprocess.check_output([sys.executable, "-m", "reactor.cli", "demo", "--steps", "2", "--dt", "0.001", "--seed", "1"])  # noqa: E501
    data = json.loads(out.decode("utf-8"))
    assert data["done"] is True

    # generate a minimal feasibility report (stable=false) and run gate
    feas = tmp_path / "feas.json"
    feas.write_text(json.dumps({"stable": True, "gamma_stats": {"gamma_max": 200}}))
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"gamma_min": 140.0}))
    code = subprocess.call([sys.executable, "scripts/metrics_gate.py", "--metrics", str(metrics), "--report", str(feas)])
    assert code == 0


def test_param_sweep_and_run_report(tmp_path):
    # sweep outputs
    csvp = tmp_path / "sweep.csv"
    jsonp = tmp_path / "sweep.json"
    jsonlp = tmp_path / "sweep.jsonl"
    subprocess.check_call([sys.executable, "scripts/param_sweep_confinement.py", "--out", str(csvp), "--json-out", str(jsonp), "--jsonl-out", str(jsonlp)])  # noqa: E501
    assert csvp.exists() and jsonp.exists() and jsonlp.exists()

    # channel report and run_report merge
    chp = tmp_path / "channel_report.json"
    subprocess.check_call([sys.executable, "scripts/generate_channel_report.py", "--out", str(chp)])
    feas = tmp_path / "feas.json"
    feas.write_text(json.dumps({"stable": True}))
    tim = tmp_path / "timeline_summary.json"
    tim.write_text(json.dumps({"counts": {"events": 0}}))
    rr = tmp_path / "run_report.json"
    subprocess.check_call([sys.executable, "scripts/run_report.py", "--feasibility", str(feas), "--timeline-summary", str(tim), "--channel-report", str(chp), "--out", str(rr)])  # noqa: E501
    data = json.loads(rr.read_text())
    assert "channel_fom_summary" in data
