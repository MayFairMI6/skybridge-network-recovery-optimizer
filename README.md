# SkyBridge Network Recovery Optimizer

A course project combining an airline-recovery simulation with a local Jenkins → Docker → Terraform deployment pipeline. The dashboard asks how different recovery policies behave under synthetic disruption assumptions; the pipeline makes application updates repeatable.

## What is implemented

`app/server.js` serves a browser dashboard that samples disruption scenarios and compares hold, cancellation/rebooking, hotel, and hybrid policies using an authored risk-adjusted cost score. Inspectable passenger, flight, and network fixtures live in `data/`. The browser also requests public weather, news, and volcanic-ash signals.

My project work in this repository covers the dashboard, scenario fixtures, deployment configuration, and optional Python prediction/training scaffold. The [commit history](https://github.com/MayFairMI6/skybridge-network-recovery-optimizer/commits/main/) and [original pipeline report](outputs/submission-report.md) provide implementation and demonstration evidence.

## Architecture and technical choices

- **Application:** Node.js HTTP server; browser-side JavaScript simulation and HTML/CSS presentation.
- **Deployment:** Jenkins polls Git, builds a numbered Docker image, and passes its tag to Terraform. Terraform replaces the local app container through the Docker provider. Jenkins and the app are sibling containers on the host daemon.
- **Prediction scaffold:** `ml/predictor.py` uses fixed, hand-authored coefficients. `ml/train_model.py` can fit standardized logistic regression to a separately supplied labeled CSV. The current predictor does not load that training output.

## Evidence and limitations

The committed report and screenshots document historical local pipeline demonstrations. They are deployment evidence, not validation of recovery policy quality.

The current repository contains no held-out operational benchmark, trained model artifact, probability-calibration study, or measured improvement over an airline baseline. “Probability,” “forecast,” and “risk” values in the prototype are heuristic simulation outputs. News counts and advisory text checks are rough signals, not verified airport closures or calibrated event probabilities. Failed requests can leave low/default signals; those must not be interpreted as evidence of clear conditions.

Fixtures are synthetic. Random sampling uses `Math.random()` without an experiment seed, and external responses change, so repeated dashboard runs are not an exact reproducible benchmark. The next research step would be a seeded evaluation harness, explicit source-availability states, baselines, and held-out data with permitted use.

## Run the dashboard

Install Node.js, then from the repository root:

```sh
node app/server.js
```

Open `http://localhost:3000`. The application uses Node's built-in modules; the optional Python service and Jenkins are not required for this path. Browser requests to external sources require network access and may fail because of provider or browser restrictions.

For the complete local deployment setup, see [Jenkins, Docker, and Terraform instructions](docs/LOCAL_PIPELINE.md). This coursework setup gives Jenkins access to the host Docker socket; use it only in a trusted local environment.

## Optional model-training scaffold

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r ml/requirements-ml.txt
python ml/train_model.py path/to/your_joined_data.csv
```

The input columns are defined in [training_schema.csv](ml/training_schema.csv). Obtain data under its provider's terms. Fitting this script does not perform a train/test evaluation or connect the model to the dashboard.
