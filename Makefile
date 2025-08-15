demo:
	python scripts/demo_runner.py --scenario examples/scenario_min.json --steps 10 --dt 1e-3
	python scripts/generate_feasibility_report.py --gamma-series "[150,150,150,120]" --dt 0.002 \
		--b-series "[5,5.01,4.99,5.02]" --E-mag "[0,1,2,3]" --out feasibility_gates_report.json --scenario-id demo-1 --fail-on-gate
