# Local automated deployment pipeline

This repository demonstrates a local CI/CD pipeline for macOS and Docker Desktop using **SkyBridge Network Recovery Optimizer**, a stochastic classroom simulation of airline recovery during a weather-constrained hub disruption:

`GitHub commit -> Jenkins SCM polling -> Docker image build -> Terraform apply -> Docker app container`

It meets the Git/GitHub, Jenkins builder, Terraform deployer, and Docker runtime requirements. SCM polling is included every two minutes.

## Application scenario

SkyBridge is a **stochastic, non-linear decision-support simulation** for a weather-constrained airline hub. It samples uncertain storm duration, hub capacity, turbulence exposure, recovery-seat availability, and future demand; it then compares hold, cancellation, same-day rebooking, hotel, and hybrid recovery policies using a risk-adjusted network-cost score.

The application uses a two-speed, seven-day recovery horizon: the first 72 hours are the active recovery window for holds, cancellations, hotels, rebooking, and recovery inventory; days 4–7 provide a capped new-sale fare and inventory forecast. Disruption-affected passengers receive fare protection; new sales are capped rather than surge-priced. Critical multi-leg passengers are protected, volunteers are sought before any involuntary action, and only flexible low-priority itineraries are considered for safe reaccommodation. All passenger, inventory, and cost values are simulated for classroom use.

The hub selector includes North American, European, Asian, Middle Eastern, Australian, and New Zealand hubs, including DXB, DOH, DEL, SIN, HKG, NRT, ICN, SYD, MEL, and AKL. The browser requests current conditions from the no-key [Open-Meteo forecast API](https://open-meteo.com/en/docs) and converts wind gusts, precipitation, and severe-weather codes into the forecast-severity input. If the API is unavailable, the simulator continues using its fallback severity value.

Synthetic input data is committed in `data/passengers.json`, `data/flights.json`, and `data/network.json`. The app loads these records at startup, so the passenger itineraries, flight seats/statuses, hub topology, disruption assumptions, and recovery costs are inspectable and reproducible. No real passenger information is used.

## Architecture

Jenkins runs in a Docker container. Its `/var/run/docker.sock` is mounted from the Docker Desktop host, so the Docker CLI and Terraform Docker provider inside Jenkins manage the **host Docker daemon**. This pattern is commonly called Docker-outside-of-Docker. The application container is therefore a sibling of Jenkins, not nested inside it.

The Jenkins build tags each image with its Jenkins build number. Terraform replaces the stable `local-pipeline-app` container with the newly tagged image and exposes it at `http://localhost:8081`.

## Prerequisites

- macOS with Docker Desktop running
- A GitHub account and repository you control
- Git installed locally
- Internet access during Jenkins builds (Terraform downloads the provider on first run)

Before starting, check that Docker Desktop works:

```sh
docker version
```

## Start Jenkins

From the repository root:

```sh
docker compose build
docker compose up -d
docker compose logs -f jenkins
```

Open `http://localhost:8080`. Obtain the unlock password with:

```sh
docker exec local-pipeline-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Complete the setup wizard and create an administrator account. To stop Jenkins later, run `docker compose down`; the named `jenkins_home` volume preserves configuration and build history.

### Docker socket note

The compose file mounts `/var/run/docker.sock` and runs this local coursework controller as `root` inside the Jenkins container because Docker Desktop exposes the socket as root-owned in this setup. This is required for Jenkins to invoke the host daemon. Do not expose the Jenkins port beyond your local machine: access to the Docker socket is effectively host-level Docker control.

## Required Jenkins plugins and credentials

During the setup wizard choose **Install suggested plugins**, then ensure these are installed under **Manage Jenkins -> Plugins**:

- Pipeline
- Git
- Pipeline: SCM Step
- Credentials Binding
- Docker Pipeline (recommended for Docker integration; this Jenkinsfile uses the CLI directly)

For a public GitHub repository, no checkout credential is required. For a private repository, create a GitHub fine-grained personal access token with read-only **Contents** access to that repository. In Jenkins, go to **Manage Jenkins -> Credentials -> System -> Global credentials**, add it as **Username with password** (GitHub username + token), and select it in the job configuration. Never commit the token.

## Create the pipeline job

1. Push this directory to your own GitHub repository (see below).
2. In Jenkins, choose **New Item** -> enter `local-deployment-pipeline` -> choose **Pipeline** -> **OK**.
3. Under **Pipeline**, select **Pipeline script from SCM**.
4. Choose **Git**, enter your repository HTTPS URL, select the credential if the repository is private, and set branch specifier to `*/main` (or your default branch).
5. Keep script path as `Jenkinsfile`, then save.
6. Click **Build Now**. The first build downloads the Terraform provider and deploys the app.

The `pollSCM('H/2 * * * *')` trigger in `Jenkinsfile` checks the repository about every two minutes. After a new commit is pushed, Jenkins should create a build without clicking **Build Now**. Jenkins polling needs the Git repository URL and credentials configured in the job.

## Push to GitHub

Create an empty repository in your GitHub account, then run (replace the placeholder):

```sh
git init
git add .
git commit -m "Create local automated deployment pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Verify the deployment

After a successful Jenkins build:

```sh
docker ps --filter name=local-pipeline-app
curl http://localhost:8081
docker logs local-pipeline-app
```

The optimizer reports the Jenkins build number. To prove polling, edit a visible scenario value or heading in `app/server.js`, commit, and push it. Wait up to two minutes plus normal checkout/build time; the Jenkins build history should show a new successful build. Open the app afterward and confirm its displayed build number changed.

## Required screenshots for the report

Capture real screenshots after your own successful run:

1. Jenkins job page showing at least one successful build (and preferably the build history after a commit-triggered build).
2. The Console Output for that build, showing `docker build` and `terraform apply` completed successfully.
3. Docker Desktop Containers view or `docker ps` showing both `local-pipeline-jenkins` and `local-pipeline-app` running.
4. Browser at `http://localhost:8081` showing the SkyBridge optimizer recommendation and its build number.
5. Optional but useful: Jenkins job configuration showing **Pipeline script from SCM** and/or the GitHub commit history showing the triggering commit.

Do not use sample or fabricated screenshots.

## Cleanup

To remove only the deployed app, run Terraform from a Jenkins workspace or use `docker rm -f local-pipeline-app`. To stop Jenkins while preserving its settings, run `docker compose down`. Removing the `jenkins_home` volume permanently deletes Jenkins configuration and history, so only do that intentionally.
