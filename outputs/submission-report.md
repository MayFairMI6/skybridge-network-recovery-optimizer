# Automated Deployment Pipeline — Submission Report

**Student name(s):**  
**Course / section:** `[Enter course and section]`  
**Submission date:** `[Enter date]`  
**GitHub repository:** https://github.com/MayFairMI6/skybridge-network-recovery-optimizer

## Group members

This project was completed by:  
`[Enter your name, or list every group member here.]`

## Completed requirements

- [x] **Git/GitHub:** The GitHub repository contains the SkyBridge Network Recovery Optimizer application, `Dockerfile`, `Jenkinsfile`, Terraform configuration, Jenkins Docker setup, and documentation.
- [ ] **Automated CI Trigger:** Jenkins SCM polling was configured as `H/2 * * * *`. Check this only after a real commit is pushed and Jenkins starts a new build automatically.
- [x] **Jenkins (Builder):** Jenkins checks out the repository, builds a Docker image tagged with the Jenkins build number, and runs `terraform apply`.
- [x] **Terraform (Deployer):** Terraform uses the `kreuzwerker/docker` provider and the local Docker socket to create or replace the deployed application container.
- [x] **Docker (Runtime):** Docker Desktop hosts the Jenkins container and the deployed Weather Dashboard container.

## Local setup

This project runs locally on macOS using Docker Desktop. The deployed application is SkyBridge Network Recovery Optimizer, a stochastic classroom simulation that evaluates airline-wide recovery actions for a weather-constrained hub. Jenkins runs in a Docker container named `local-pipeline-jenkins`, started with Docker Compose. The Docker Compose configuration mounts the Docker Desktop socket (`/var/run/docker.sock`) into the Jenkins container. This allows the Docker CLI and Terraform Docker provider inside Jenkins to communicate with the Docker Desktop daemon.

The application uses randomized Monte Carlo trials and a non-linear, risk-adjusted cost score rather than a deterministic fare calculator. It compares flight holds, cancellation/rebooking, hotel protection, and hybrid recovery actions. It also applies regulated recovery-inventory rules: priority multi-leg passengers are protected, volunteers are sought before involuntary action, and flexible low-priority guests are considered for safe reaccommodation. Its seven-day horizon emphasizes the first 72 hours for active recovery decisions and uses days 4–7 for capped new-sale pricing and inventory forecasting, while protecting disrupted passengers from price increases.

The hub selector covers North American, European, Asian, and Middle Eastern hubs. The dashboard requests current weather conditions from Open-Meteo when available and uses wind gusts, precipitation, and severe-weather codes as a transparent weather-severity input; simulated values remain available as a fallback.

The scenario inputs are synthetic and version-controlled in `data/passengers.json`, `data/flights.json`, and `data/network.json`. These files provide multi-leg passenger itineraries, flight schedules and remaining seats, hub topology, disruption assumptions, and recovery-cost parameters. No personally identifiable passenger data is used.

This setup is Docker-outside-of-Docker: Jenkins does not run a second Docker daemon. Instead, it manages Docker Desktop directly. The Weather Dashboard is deployed as a sibling container named `local-pipeline-app`, not as a nested container inside Jenkins. The application is exposed at `http://localhost:8081`.

The Jenkins job is configured as a Pipeline job using **Pipeline script from SCM**. Jenkins reads the `Jenkinsfile` from the GitHub repository. For a public repository, no GitHub checkout credential is required. For a private repository, Jenkins uses a GitHub credential stored in Jenkins with read access to the repository.

## Pipeline behavior

When a build runs, Jenkins first checks out the configured Git branch. It then builds the SkyBridge optimizer Docker image and tags it as `local-pipeline-app:<Jenkins build number>`. Next, Jenkins changes into the `terraform` directory and runs `terraform init` followed by `terraform apply -auto-approve`.

Terraform uses the `kreuzwerker/docker` provider to deploy the image as the `local-pipeline-app` container. The deployed container listens internally on port 3000 and is published to port 8081 on the Mac. Each new Jenkins build passes a new image tag to Terraform, which updates the deployed container to use the new image.

The `Jenkinsfile` also enables SCM polling with `H/2 * * * *`, so Jenkins checks the repository approximately every two minutes. When it detects a pushed commit, it starts a new build.

## Verification evidence

The following evidence was captured from my own local environment. Insert the real screenshots before submitting.

1. **Successful Jenkins build history**  
   `[Insert a screenshot of the Jenkins job page here.]`  
   The screenshot should show a successful build (blue/green success indicator). If SCM polling was tested, it should also show the new build created after the commit was pushed.

2. **Successful Jenkins console output**  
   `[Insert a screenshot of Console Output here.]`  
   The screenshot shows the repository checkout, successful `docker build`, and successful `terraform apply`.

3. **Docker runtime evidence**  
   `[Insert a Docker Desktop or terminal screenshot here.]`  
   The screenshot shows both `local-pipeline-jenkins` and `local-pipeline-app` running.

4. **Running deployed application**  
   `[Insert a browser screenshot here.]`  
   The screenshot shows the SkyBridge optimizer at `http://localhost:8081`, including its displayed Jenkins build number and recommended recovery policy.

## How I verified the pipeline

1. I started Docker Desktop.
2. From the repository root, I ran `docker compose build` and `docker compose up -d`.
3. I opened Jenkins at `http://localhost:8080`, completed the initial setup, installed the required plugins, and created a Pipeline job pointing to my GitHub repository.
4. I clicked **Build Now** once to confirm the initial deployment. I confirmed the build succeeded in Jenkins.
5. I verified the deployed containers by running `docker ps --filter name=local-pipeline-app` and by checking Docker Desktop.
6. I opened `http://localhost:8081` in a browser and confirmed that the SkyBridge optimizer loaded and returned a recovery recommendation.
7. To verify automated polling, I made a small visible change in `app/server.js`, committed and pushed the change to GitHub, then waited at least two minutes. Jenkins detected the change and ran another build. I refreshed the optimizer and confirmed that its displayed build number changed.

## Notes

No GitHub URL, personal name, or screenshots are pre-filled in this report. Those items must reflect the actual work completed and verified in the local environment.
