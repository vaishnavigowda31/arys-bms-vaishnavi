# Title & candidate details
**Title:** BMS with CAN Communication — 2s2p pack simulation  
**Candidate:** K M Vaishnavi Gowda

## Abstract
(Write a 150–200 word abstract summarizing objectives, methods, and key results.)

## Tools & AI usage
List Python, numpy, matplotlib, python-can. Document AI usage: prompts, outputs used, edits.

## Design & methodology
- Pack topology (2s2p)
- Cell model: OCV(SOC) + R_internal
- Thermal model: lumped C_th and R_th
- SOC estimation: coulomb counting with voltage correction
- Fault detection logic: thresholds and persistence

## Implementation details
Reference `src/` files. Explain main functions and control logic.

## Results (plots/screenshots)
Insert `results/plots/*` images and a short description:
- Cell voltages: behavior over drive profile
- Cell temps: cooling trigger
- SOC: balancing behavior

## Challenges & limitations
(e.g., simplistic OCV mapping, passive balancing only, no real CAN hardware)

## Conclusion
Summarize successes and improvements.

## References
- Arys Garage assignment PDF (local): /mnt/data/Arys Garage – Assignments Nov 2025 .pdf

## Appendix: Git log + run instructions
(Include `git log --oneline` and `python src/simulate.py` command)
