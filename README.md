# Event Driven Molecular Dynamics

## Objective
Simulate a 2D gas using an **event-driven molecular dynamics** approach and
analyze how macroscopic properties emerge from elastic particle collisions.

## Methodology
- Event-driven simulation (no fixed timestep)
- Priority queue of predicted collision events
- Elastic particle–particle and particle–wall interactions
- Two connected chambers with variable available area

## Results
- System reaches a clear stationary (equilibrium) regime
- Increasing available area reduces collision frequency and pressure
- Pressure shows near-linear dependence on inverse area (A⁻¹)
- Mean Squared Displacement grows linearly with time, indicating **normal diffusion**

## Conclusion
The simulator produces **physically consistent and stable results** using
purely event-driven dynamics.  
Macroscopic observables (pressure and diffusion) naturally emerge from
microscopic collision rules, validating both the modeling approach and the
event scheduling strategy.

---

## Additional Material

- **Presentation**: Full methodology, equations, plots, and error analysis are
  documented in the slides used for the oral defense:
  `/analysis/SdS_TP3_2025Q2G02_Presentación.pdf`

- **Simulation Videos**:
    - L = 0.03 → https://youtu.be/4367M5zXpqo
    - L = 0.09 → https://youtu.be/ipwSF2M4pAY


---

## Execution (Reproducibility)

### Compile
```bash
javac Simulator/src/*.java -d out/production/SDS-TP3
````

### Generate Initial Conditions

```bash
java -cp out/production/SDS-TP3 Generator 300 0.09 0.01 0.0015 5
```

### Run Simulation

```bash
java -cp out/production/SDS-TP3 Simulator 300 0.09 1 1000 ./inputs ./outputs
```

### Optional Visualization

```bash
python3 animator.py outputs/N_300_L0.090/output_*.csv --fps 20 --writer ffmpeg
```
