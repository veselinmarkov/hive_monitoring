#!/usr/bin/env python3
"""Re-initialises the Hive MySQL database from the sql_init dumps stored in S3.

Runs the same import sequence as the original EC2 user-data script, but via
SSM RunCommand so no direct network access to the MySQL host is required.

Usage:
    python infrastructure/init_db.py

Required SSM parameters (created by provision_db.py):
    /hive/db/password   - MySQL root / app password
    /hive/db/name       - database name
    /hive/infra/subnet-id  - used to locate the MySQL EC2 instance (indirect)

Required environment variable:
    AWS_DEFAULT_REGION  (default: eu-central-1)
"""
import os
import time

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")
INSTANCE_NAME = os.environ.get("DB_INSTANCE_NAME", "hive-mysql-host")
EB_BUCKET = os.environ.get("EB_BUCKET", "hive-eb-deployments-412265554969-eu-central-1-an")
SQL_INIT_S3_PREFIX = "db-init/"

ssm = boto3.client("ssm", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)


def get_ssm(name, decrypt=False):
    try:
        return ssm.get_parameter(Name=name, WithDecryption=decrypt)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            raise SystemExit(f"ERROR: SSM parameter '{name}' not found.")
        raise


def get_instance_id():
    resp = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
        {"Name": "instance-state-name", "Values": ["running"]},
    ])
    for r in resp["Reservations"]:
        for i in r["Instances"]:
            return i["InstanceId"]
    raise SystemExit(f"ERROR: No running instance named '{INSTANCE_NAME}' found.")


def run_command(instance_id, commands):
    resp = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
        TimeoutSeconds=600,
    )
    return resp["Command"]["CommandId"]


def wait_for_command(command_id, instance_id, timeout=600):
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(5)
        try:
            inv = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        except ClientError:
            continue
        status = inv["Status"]
        if status in ("Success", "Failed", "Cancelled", "TimedOut"):
            print(inv["StandardOutputContent"])
            if inv["StandardErrorContent"]:
                print("STDERR:", inv["StandardErrorContent"])
            return status
    raise TimeoutError("Timed out waiting for SSM command to complete.")


def main():
    print("Reading parameters from SSM...")
    db_password = get_ssm("/hive/db/password", decrypt=True)
    db_name = get_ssm("/hive/db/name")

    print(f"Locating instance '{INSTANCE_NAME}'...")
    instance_id = get_instance_id()
    print(f"Found: {instance_id}")

    script = f"""#!/bin/bash
set -euo pipefail

aws s3 sync s3://{EB_BUCKET}/{SQL_INIT_S3_PREFIX} /tmp/db-init --region {REGION}

mysql -u root -p"{db_password}" {db_name} < /tmp/db-init/definitions/samples_definition.sql
echo "samples_definition.sql OK"

zcat /tmp/db-init/hive_wo_samples.dmp.gz | mysql -u root -p"{db_password}" {db_name}
echo "hive_wo_samples.dmp.gz OK"

zcat /tmp/db-init/samples_monthly_dump_2024-05.bkp.gz | mysql -u root -p"{db_password}" {db_name}
echo "samples_monthly_dump_2024-05 OK"

zcat /tmp/db-init/samples_monthly_dump_2024-06.bkp.gz | mysql -u root -p"{db_password}" {db_name}
echo "samples_monthly_dump_2024-06 OK"

zcat /tmp/db-init/samples_monthly_dump_2024-07.bkp.gz | mysql -u root -p"{db_password}" {db_name}
echo "samples_monthly_dump_2024-07 OK"

echo "Database initialisation complete."
"""
    commands = [script]

    print("Sending init command to MySQL host via SSM...")
    command_id = run_command(instance_id, commands)
    print(f"Command ID: {command_id} — waiting for completion (this may take a few minutes)...")

    status = wait_for_command(command_id, instance_id)
    if status == "Success":
        print("Database initialisation completed successfully.")
    else:
        raise SystemExit(f"ERROR: Command finished with status '{status}'. Check output above.")


if __name__ == "__main__":
    main()
