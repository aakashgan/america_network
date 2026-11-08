# NFIP Claims XGBoost Damage-Fraction Estimator

**Target:** `buildingDamageAmount / buildingPropertyValue`, retaining only records with positive comparable property value and a ratio in `[0, 1]`. This is a claim-record damage-severity target, not a building-failure probability.

**Training source:** FEMA OpenFEMA NFIP Claims API (`NfipClaims`), acquired locally by `ml-training/train.py`. The raw cache is not committed. The model uses water depth, floors, occupancy, foundation, elevation/build-era flags, and year of loss; it excludes payments and settlement fields to avoid target leakage.

**Experiment:** The local artifact records its actual training/test count and held-out grouped-event metrics in `ml-training/artifacts/model_metadata.json`. NFIP claims are selected insurance claims, not a random sample of all exposed buildings. Richardson inputs are synthetic scenario assumptions and must not be treated as property observations or forecasts.
