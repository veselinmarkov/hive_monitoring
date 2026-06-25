# Infrastructure Pipeline Setup Guide

This guide covers the **infrastructure pipeline**, which provisions the MySQL host
that the app relies on. It is kept separate from the application build/deploy
pipeline described in [CODEBUILD_SETUP.md](CODEBUILD_SETUP.md):

- `infra-buildspec.yml` + `infrastructure/provision_db.py` — creates the EC2 +
  EBS host running MySQL, security group, and IAM role. Runs rarely (only when
  the database host itself needs to be created or its definition changes).
- `buildspec.yml` — builds and deploys the app (frontend to S3, backend image to
  ECR, Elastic Beanstalk update). Runs on every push. It reads the database
  connection details from SSM Parameter Store; it no longer creates any
  database infrastructure itself.

Run the infrastructure pipeline **once, before the first app deployment** —
`buildspec.yml` expects `/hive/db/host` and friends to already exist in
Parameter Store.

---

## Why EC2 + EBS instead of RDS

The MySQL database now runs on a small, self-managed Ubuntu EC2 instance with a
dedicated EBS data volume (`/var/lib/mysql-data`), instead of RDS. This trades
RDS's managed patching/backups for lower cost and full control over the host.
There is currently no automated backup of the data volume — take manual EBS
snapshots periodically if you need point-in-time recovery.

---

## What `provision_db.py` does

Idempotent — if an EC2 instance tagged `Name=hive-mysql-host` already exists
(in any non-terminated state), the script does nothing except refresh the
`/hive/db/host` parameter. On a fresh run it:

1. Creates (or reuses) a security group `hive-mysql-sg` that allows inbound
   port 3306 **only** from the app's security group (`APP_SECURITY_GROUP_ID`).
   No SSH port is opened.
2. Creates an IAM role/instance profile (`hive-mysql-ec2-role`) with
   `AmazonSSMManagedInstanceCore` (for Session Manager access) plus a scoped
   inline policy for reading/writing `/hive/db/*` SSM parameters and reading
   the staged `sql_init` dumps from S3.
3. Generates a random MySQL root/app password and stores it as a
   `SecureString` at `/hive/db/password` (only if one doesn't already exist).
4. Looks up the latest Ubuntu 22.04 LTS AMI via the public Canonical SSM
   parameter.
5. Uploads the contents of `sql_init/` to `s3://$EB_BUCKET/db-init/`.
6. Launches the EC2 instance with an 8GB root volume and a second EBS volume
   (`DB_VOLUME_SIZE_GB`, default 20GB, gp3) attached at `/dev/sdf`. No public
   IP, no key pair.
7. Instance user data (runs once on first boot):
   - Formats the data volume (ext4) if it isn't already formatted.
   - Mounts it at `/var/lib/mysql-data` and relocates MySQL's `datadir` there
     (with the matching AppArmor alias), so all data lives on the dedicated
     volume.
   - Installs `mysql-server`, sets the root password from
     `/hive/db/password`, creates the `hive` database and `hiveadmin` user,
     and opens MySQL to the private network (`bind-address = 0.0.0.0` — it's
     still only reachable from inside the VPC, gated by the security group).
   - Downloads the staged dumps from S3 and imports them in the same order
     the old RDS bootstrap used to (`samples_definition.sql`,
     `hive_wo_samples.dmp.gz`, then the three monthly dumps).
   - Writes a completion marker file.
8. The script polls the instance via SSM `send_command` until the completion
   marker appears (timeout 15 minutes), then writes `/hive/db/host`,
   `/hive/db/name`, and `/hive/db/username` to Parameter Store.

---

## Prerequisites

- The target subnet must have outbound internet access (NAT gateway) or VPC
  interface endpoints for `ssm`, `ssmmessages`, `ec2messages`, plus an S3
  gateway endpoint — required for SSM Session Manager and for the instance to
  reach `apt` repositories and S3.
- The app's Elastic Beanstalk environment must already exist so you know its
  security group ID (`APP_SECURITY_GROUP_ID`). Find it via:
  ```bash
  aws elasticbeanstalk describe-environment-resources --environment-name hive-backend-env \
    --query 'EnvironmentResources.Instances[0].Id' --output text
  # then look up that instance's security group, or check EC2 console → the EB env's instances
  ```
- The same `EB_BUCKET` artifacts bucket used by the app pipeline (it just needs
  `s3:PutObject`/`s3:GetObject` for the `db-init/` prefix).

---

## Step 1 — Create the IAM Role for the Infra CodeBuild Project

1. **IAM → Roles → Create role** → Trusted entity: **CodeBuild**
2. Attach these managed policies (broad, matching the pragmatic style used for
   the app pipeline's role):
   - `AmazonEC2FullAccess`
   - `IAMFullAccess` (needed to create the `hive-mysql-ec2-role` role/instance
     profile and to `iam:PassRole` it to EC2)
   - `AmazonSSMFullAccess`
   - `AmazonS3FullAccess`
3. Name it `CodeBuildHiveInfraRole`.

## Step 2 — Create the Infra CodeBuild Project

1. **CodeBuild → Create build project**
2. Project name: `hive-infra-build`
3. Source: same GitHub repo/branch as the app project (via the CodeStar
   connection already created for the app pipeline)
4. Environment: Managed image **Ubuntu**, Standard runtime,
   `aws/codebuild/standard:7.0`, service role `CodeBuildHiveInfraRole`
   - Privileged mode is **not** required (no Docker build here)
5. VPC: not required for the CodeBuild project itself — `provision_db.py` only
   calls the EC2/IAM/SSM/S3 APIs, it doesn't need to be inside the VPC.
6. Buildspec: select **Use a buildspec file** → `infra-buildspec.yml`
7. Update the environment variables in `infra-buildspec.yml` (or override them
   in the CodeBuild project console) with your real values:

   | Variable | Where to get it |
   |----------|----------------|
   | `VPC_SUBNET_ID` | the subnet (private, with NAT/VPC endpoints) where the DB host should live — same VPC as the EB environment |
   | `APP_SECURITY_GROUP_ID` | security group of the EB environment's instances |
   | `EB_BUCKET` | the existing deployment artifacts bucket from the app pipeline setup |
   | `DB_INSTANCE_NAME` / `DB_INSTANCE_TYPE` / `DB_VOLUME_SIZE_GB` / `DB_NAME` / `DB_USERNAME` | adjust if needed, sane defaults already set |

## Step 3 — Run the Infra Pipeline

Since infra changes are rare, this project doesn't need a CodePipeline trigger.
Run it on demand:

```bash
aws codebuild start-build --project-name hive-infra-build
```

If you'd rather have it auto-trigger on pushes to `infrastructure/**` or
`infra-buildspec.yml`, wire it into a CodePipeline (V2 pipeline type) using a
Git push trigger filtered to those file paths — but a manual trigger is
simpler and matches how infrequently this should run.

Watch the build logs; the final lines confirm the instance's private IP and
that `/hive/db/*` parameters were written.

## Step 4 — Grant the App Pipeline Read Access

The existing `CodeBuildHiveRole` (used by the app's `hive-backend-build`
project, see [CODEBUILD_SETUP.md](CODEBUILD_SETUP.md) Step 6) needs to read
the parameters this pipeline writes. Add an inline policy:

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

(`AmazonRDSFullAccess` and the RDS-specific VPC/security-group steps from the
old CODEBUILD_SETUP.md are no longer needed by the app pipeline — see the
update there.)

---

## Ad-hoc Admin Access

No SSH key exists for this instance. To get a shell:

```bash
aws ssm start-session --target <instance-id>
```

Find `<instance-id>` via **EC2 console** → filter by tag `Name=hive-mysql-host`,
or:

```bash
aws ec2 describe-instances --filters "Name=tag:Name,Values=hive-mysql-host" \
  "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text
```

---

## Troubleshooting

**`provision_db.py` hangs in `wait_for_mysql_ready`**
→ Check `/var/log/hive-mysql-init.log` on the instance via SSM Session Manager.
Common causes: subnet lacks internet/VPC-endpoint access for `apt-get` or S3,
or the `sql_init` dumps failed to import (foreign key/order issue).

**App pipeline fails reading `/hive/db/host`**
→ The infra pipeline hasn't been run yet, or failed before reaching the final
`put_parameter` calls. Check Parameter Store directly:
`aws ssm get-parameter --name /hive/db/host`.

**EB environment doesn't pick up the new `DATABASE_URL`**
→ `buildspec.yml`'s `update-environment` call sets it via `--option-settings`
on every app deploy. If you rotate the DB password by re-running the infra
script against an *existing* instance, the password in Parameter Store won't
change (the script only generates one if absent) — to rotate it you'd need to
update `/hive/db/password` and the MySQL user's password together.
