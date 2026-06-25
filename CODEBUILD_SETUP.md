# AWS CodeBuild / CodePipeline Setup Guide

This guide walks through setting up the CI/CD pipeline that builds and deploys the
app for the Hive Monitoring project:
GitHub → CodePipeline → CodeBuild → ECR + S3 + Elastic Beanstalk.

The MySQL database is provisioned by a **separate** pipeline — see
[INFRA_SETUP.md](INFRA_SETUP.md). Run that one first; this pipeline reads the
resulting connection details from SSM Parameter Store rather than creating any
database infrastructure itself.

---

## Prerequisites

You need:
- An AWS account with admin access (or sufficient IAM permissions)
- The project pushed to a GitHub repository
- AWS CLI installed locally (for the one-time setup steps below)

---

## Step 1 — Create S3 Buckets

Two S3 buckets are required.

**Frontend bucket** (serves the built React app via CloudFront):
1. Go to **S3 → Create bucket**
2. Name: e.g. `hive-frontend` (must be globally unique)
3. Region: `us-east-1`
4. Uncheck "Block all public access" (CloudFront needs to read it)
5. Enable static website hosting: index document = `index.html`, error document = `index.html`

**Deployment artifacts bucket** (CodeBuild uploads EB bundles here):
1. Create another bucket: e.g. `hive-eb-deployments`
2. Keep "Block all public access" ON
3. Same region as everything else

Update `buildspec.yml` variables:
```
FRONTEND_S3_BUCKET: "hive-frontend"
EB_BUCKET:          "hive-eb-deployments"
```

---

## Step 2 — Create ECR Repository

1. Go to **ECR → Create repository**
2. Name: `hive-backend`
3. Visibility: Private
4. Click **Create repository**
5. Copy the repository name and update `buildspec.yml`:
   ```
   ECR_REPOSITORY: "hive-backend"
   AWS_ACCOUNT_ID: "your-12-digit-account-id"
   ```

---

## Step 3 — Create Elastic Beanstalk Application and Environment

1. Go to **Elastic Beanstalk → Create application**
2. Application name: `hive-backend-app`
3. Platform: **Docker** → Platform branch: **Docker running on 64bit Amazon Linux 2023**
4. Click **Create environment** → Web server environment
5. Environment name: `hive-backend-env`
6. For initial deployment, choose "Sample application" — CodePipeline will deploy the real image
7. Under **Configure more options → Network**: place it in the same VPC where the MySQL EC2 host (see [INFRA_SETUP.md](INFRA_SETUP.md)) will run

Update `buildspec.yml`:
```
EB_APPLICATION_NAME: "hive-backend-app"
EB_ENVIRONMENT_NAME: "hive-backend-env"
```

**Set EB environment variables** (Configuration → Software → Environment properties):

| Key | Value |
|-----|-------|
| `DATABASE_URL` | set automatically by `buildspec.yml` on every deploy from the `/hive/db/*` SSM parameters written by the infra pipeline — no manual entry needed once that pipeline has run |
| `SECRET_KEY` | your Django secret key |
| `DEBUG` | `False` |
| `DEVELOP` | `False` |
| `PORT` | `80` |
| `GUNICORN_HOST` | `127.0.0.1:8000` |

---

## Step 4 — Create the CodeBuild IAM Role

CodeBuild needs permissions to push to ECR, write to S3, deploy to EB, and read the database connection details from Parameter Store.

1. Go to **IAM → Roles → Create role**
2. Trusted entity: **AWS service → CodeBuild**
3. Attach these managed policies:
   - `AWSCodeBuildAdminAccess`
   - `AmazonEC2ContainerRegistryPowerUser`
   - `AmazonS3FullAccess`
   - `AWSElasticBeanstalkFullAccess`
4. Add an inline policy granting read access to the database parameters
   written by the infra pipeline (see [INFRA_SETUP.md](INFRA_SETUP.md) Step 4):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["ssm:GetParameter"],
       "Resource": "arn:aws:ssm:us-east-1:*:parameter/hive/db/*"
     }]
   }
   ```
5. Name the role: `CodeBuildHiveRole`

---

## Step 5 — Connect GitHub to AWS via CodeStar Connection

This allows CodePipeline to watch your GitHub repository without storing credentials.

1. Go to **CodePipeline → Settings → Connections → Create connection**
2. Provider: **GitHub**
3. Connection name: `hive-github`
4. Click **Connect to GitHub** and authorise the AWS Connector app
5. Select your repository and click **Connect**
6. Copy the connection ARN — you will need it in the next step

---

## Step 6 — Create the CodeBuild Project

1. Go to **CodeBuild → Create build project**
2. **Project name**: `hive-backend-build`
3. **Source**:
   - Provider: **GitHub** (via CodeStar connection created above)
   - Repository: select your repo
   - Branch: `master`
4. **Environment**:
   - Managed image: **Ubuntu**
   - Runtime: **Standard**
   - Image: `aws/codebuild/standard:7.0`
   - Privileged: **YES** (required for Docker builds)
   - Service role: `CodeBuildHiveRole` (created in Step 4)
5. **VPC**: not required. This project only talks to ECR, S3, Elastic
   Beanstalk, and SSM Parameter Store — all public AWS API endpoints — it no
   longer needs network access into the VPC (that's only needed by the
   separate infra pipeline; see [INFRA_SETUP.md](INFRA_SETUP.md)).
6. **Buildspec**: select **Use a buildspec file** — CodeBuild reads `buildspec.yml` from the repo root
7. Click **Create build project**

---

## Step 7 — Create the CodePipeline

This wires GitHub → CodeBuild into a single automated pipeline.

1. Go to **CodePipeline → Create pipeline**
2. **Pipeline name**: `hive-pipeline`
3. **Service role**: create a new one or reuse an existing pipeline role
4. **Source stage**:
   - Provider: **GitHub (Version 2)**
   - Connection: select `hive-github`
   - Repository: your repo
   - Branch: `master`
   - Detection: **Webhooks** (triggers on every push)
5. **Build stage**:
   - Provider: **AWS CodeBuild**
   - Project name: `hive-backend-build`
6. Skip the Deploy stage (CodeBuild handles EB deployment directly via `buildspec.yml`)
7. Click **Create pipeline**

The pipeline runs immediately on creation. Subsequent pushes to `master` trigger it automatically.

---

## Step 8 — Update buildspec.yml with Your Values

Before pushing, replace all placeholder values in `buildspec.yml`:

| Variable | Where to get it |
|----------|----------------|
| `AWS_ACCOUNT_ID` | AWS Console → top-right account menu |
| `AWS_DEFAULT_REGION` | your chosen region, e.g. `us-east-1` |
| `FRONTEND_S3_BUCKET` | bucket name from Step 1 |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront console (if using CDN, else leave as-is) |
| `ECR_REPOSITORY` | repository name from Step 2 |
| `EB_APPLICATION_NAME` | from Step 3 |
| `EB_ENVIRONMENT_NAME` | from Step 3 |
| `EB_BUCKET` | artifacts bucket name from Step 1 |

---

## First Run Behaviour

Make sure the infra pipeline (see [INFRA_SETUP.md](INFRA_SETUP.md)) has already
been run at least once — this pipeline reads `/hive/db/host`,
`/hive/db/name`, `/hive/db/username`, and `/hive/db/password` from SSM
Parameter Store and fails fast if they don't exist yet.

On each pipeline run:
1. CodeBuild reads the database connection details from Parameter Store
2. Builds the React frontend and syncs it to S3 (+ CloudFront invalidation if configured)
3. Builds and pushes the Docker image to ECR
4. Deploys to Elastic Beanstalk, setting `DATABASE_URL` on the environment automatically

---

## Troubleshooting

**Build fails reading `/hive/db/host` (or similar) from Parameter Store**
→ The infra pipeline hasn't been run yet, or the CodeBuild role is missing the
`ssm:GetParameter` inline policy from Step 4. See
[INFRA_SETUP.md](INFRA_SETUP.md) troubleshooting section.

**`npm ci` fails with peer dependency errors**
→ Ensure `--legacy-peer-deps` is present (already in `buildspec.yml`).

**ECR push fails: "no basic auth credentials"**
→ The IAM role is missing `AmazonEC2ContainerRegistryPowerUser`. Also confirm `Privileged` mode is enabled in the CodeBuild environment (Step 6).

**EB deployment stuck on "Updating"**
→ Check the EB environment events tab and the container logs for startup errors (missing env vars, DB connection failure — confirm the EC2 MySQL host's security group allows inbound 3306 from the EB environment's security group).
