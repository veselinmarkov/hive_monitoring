#!/usr/bin/env python3
"""Destroys all Hive project infrastructure.

Preserves:
  - SSM Parameter Store parameters (/hive/*)
  - IAM roles and instance profiles

Destroys (in safe order):
  1. CloudFront distribution (hive EB distribution)
  2. Elastic Beanstalk environment and application
  3. ECR repository
  4. EC2 instance (hive-mysql-host) and its data EBS volume
  5. Security group (hive-mysql-sg)
  6. S3 buckets (frontend and EB deployments)
  7. CodeBuild project

Usage:
    python infrastructure/destroy.py
"""
import os
import sys
import time
import argparse

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")

INSTANCE_NAME      = "hive-mysql-host"
SG_NAME            = "hive-mysql-sg"
EB_APP_NAME        = "hive-backend-app"
EB_ENV_NAME        = "hive-backend-env"
ECR_REPO_NAME      = "hive-backend"
CODEBUILD_PROJECT  = "hive-backend-build"
FRONTEND_BUCKET    = "hive-frontend-412265554969-eu-central-1-an"
EB_BUCKET          = "hive-eb-deployments-412265554969-eu-central-1-an"
CF_DIST_SSM_PARAM  = "/hive/infra/cloudfront-eb-distribution-id"

ec2 = boto3.client("ec2", region_name=REGION)
eb  = boto3.client("elasticbeanstalk", region_name=REGION)
ecr = boto3.client("ecr", region_name=REGION)
s3  = boto3.client("s3", region_name=REGION)
s3r = boto3.resource("s3", region_name=REGION)
cb  = boto3.client("codebuild", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)
cf  = boto3.client("cloudfront", region_name="us-east-1")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def confirm(prompt):
    answer = input(f"\n{prompt} [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        sys.exit(0)


def ignore_not_found(fn, *args, codes=("NoSuchEntity", "ResourceNotFoundException",
                                       "NoSuchBucket", "RepositoryNotFoundException",
                                       "ProjectNotFoundException"), **kwargs):
    try:
        return fn(*args, **kwargs)
    except ClientError as e:
        if e.response["Error"]["Code"] in codes:
            return None
        raise


# ---------------------------------------------------------------------------
# Step 1 — CloudFront
# ---------------------------------------------------------------------------

def destroy_cloudfront():
    try:
        dist_id = ssm.get_parameter(Name=CF_DIST_SSM_PARAM)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            print("  CloudFront: no distribution ID in SSM — skipping.")
            return
        raise

    print(f"  Disabling CloudFront distribution {dist_id}...")
    resp = cf.get_distribution_config(Id=dist_id)
    etag   = resp["ETag"]
    config = resp["DistributionConfig"]

    if config["Enabled"]:
        config["Enabled"] = False
        resp = cf.update_distribution(Id=dist_id, DistributionConfig=config, IfMatch=etag)
        etag = resp["ETag"]
        print("  Waiting for distribution to finish disabling (this takes ~10 min)...")
        while True:
            status = cf.get_distribution(Id=dist_id)["Distribution"]["Status"]
            print(f"    status: {status}")
            if status == "Deployed":
                break
            time.sleep(30)

    print(f"  Deleting CloudFront distribution {dist_id}...")
    cf.delete_distribution(Id=dist_id, IfMatch=etag)
    print("  CloudFront distribution deleted.")


# ---------------------------------------------------------------------------
# Step 2 — Elastic Beanstalk
# ---------------------------------------------------------------------------

def destroy_elasticbeanstalk():
    envs = eb.describe_environments(ApplicationName=EB_APP_NAME,
                                    EnvironmentNames=[EB_ENV_NAME])["Environments"]
    if envs and envs[0]["Status"] not in ("Terminated", "Terminating"):
        print(f"  Terminating EB environment '{EB_ENV_NAME}' (this takes a few minutes)...")
        eb.terminate_environment(EnvironmentName=EB_ENV_NAME)
        while True:
            status = eb.describe_environments(
                EnvironmentNames=[EB_ENV_NAME])["Environments"][0]["Status"]
            print(f"    status: {status}")
            if status == "Terminated":
                break
            time.sleep(15)
        print("  EB environment terminated.")
    else:
        print("  EB environment: not found or already terminated — skipping.")

    try:
        eb.delete_application(ApplicationName=EB_APP_NAME, TerminateEnvByForce=True)
        print(f"  EB application '{EB_APP_NAME}' deleted.")
    except ClientError as e:
        if "No Application" in str(e):
            print("  EB application: not found — skipping.")
        else:
            raise


# ---------------------------------------------------------------------------
# Step 3 — ECR repository
# ---------------------------------------------------------------------------

def destroy_ecr():
    try:
        ecr.delete_repository(repositoryName=ECR_REPO_NAME, force=True)
        print(f"  ECR repository '{ECR_REPO_NAME}' deleted.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "RepositoryNotFoundException":
            print("  ECR repository: not found — skipping.")
        else:
            raise


# ---------------------------------------------------------------------------
# Step 4 — EC2 instance + data EBS volume
# ---------------------------------------------------------------------------

def destroy_ec2():
    resp = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
        {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
    ])
    instances = [i for r in resp["Reservations"] for i in r["Instances"]]
    if not instances:
        print("  EC2 instance: not found — skipping.")
        return None

    instance = instances[0]
    instance_id = instance["InstanceId"]

    # Collect non-root EBS volumes to delete after termination
    root_device = instance.get("RootDeviceName", "/dev/sda1")
    data_volume_ids = [
        bdm["Ebs"]["VolumeId"]
        for bdm in instance.get("BlockDeviceMappings", [])
        if bdm["DeviceName"] != root_device
    ]

    print(f"  Terminating EC2 instance {instance_id}...")
    ec2.terminate_instances(InstanceIds=[instance_id])
    ec2.get_waiter("instance_terminated").wait(InstanceIds=[instance_id])
    print("  EC2 instance terminated.")

    for vol_id in data_volume_ids:
        print(f"  Deleting data EBS volume {vol_id}...")
        try:
            ec2.delete_volume(VolumeId=vol_id)
            print(f"  Volume {vol_id} deleted.")
        except ClientError as e:
            print(f"  Volume {vol_id}: {e.response['Error']['Code']} — skipping.")


# ---------------------------------------------------------------------------
# Step 5 — Security group
# ---------------------------------------------------------------------------

def destroy_security_group():
    resp = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [SG_NAME]}])
    sgs = resp["SecurityGroups"]
    if not sgs:
        print(f"  Security group '{SG_NAME}': not found — skipping.")
        return
    sg_id = sgs[0]["GroupId"]
    ec2.delete_security_group(GroupId=sg_id)
    print(f"  Security group '{SG_NAME}' ({sg_id}) deleted.")


# ---------------------------------------------------------------------------
# Step 6 — S3 buckets
# ---------------------------------------------------------------------------

def empty_and_delete_bucket(bucket_name):
    try:
        bucket = s3r.Bucket(bucket_name)
        bucket.object_versions.delete()
        bucket.objects.delete()
        bucket.delete()
        print(f"  S3 bucket '{bucket_name}' emptied and deleted.")
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchBucket", "404"):
            print(f"  S3 bucket '{bucket_name}': not found — skipping.")
        else:
            raise


# ---------------------------------------------------------------------------
# Step 7 — CodeBuild project
# ---------------------------------------------------------------------------

def destroy_codebuild():
    try:
        cb.delete_project(name=CODEBUILD_PROJECT)
        print(f"  CodeBuild project '{CODEBUILD_PROJECT}' deleted.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"  CodeBuild project '{CODEBUILD_PROJECT}': not found — skipping.")
        else:
            raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    print("=" * 60)
    print("Hive infrastructure teardown")
    print("=" * 60)
    print("\nThis will permanently destroy:")
    print(f"  • CloudFront distribution (from SSM {CF_DIST_SSM_PARAM})")
    print(f"  • Elastic Beanstalk: {EB_ENV_NAME} / {EB_APP_NAME}")
    print(f"  • ECR repository: {ECR_REPO_NAME}")
    print(f"  • EC2 instance: {INSTANCE_NAME} + its data EBS volume")
    print(f"  • Security group: {SG_NAME}")
    print(f"  • S3 buckets: {FRONTEND_BUCKET}")
    print(f"  •             {EB_BUCKET}")
    print(f"  • CodeBuild project: {CODEBUILD_PROJECT}")
    print("\nPreserved: SSM parameters, IAM roles and instance profiles.")

    if not args.yes:
        confirm("Are you sure you want to destroy all of the above?")
    else:
        print("\nProceeding without confirmation (--yes flag set).")

    print("\n[1/7] CloudFront distribution")
    destroy_cloudfront()

    print("\n[2/7] Elastic Beanstalk")
    destroy_elasticbeanstalk()

    print("\n[3/7] ECR repository")
    destroy_ecr()

    print("\n[4/7] EC2 instance + EBS volume")
    destroy_ec2()

    print("\n[5/7] Security group")
    destroy_security_group()

    print("\n[6/7] S3 buckets")
    empty_and_delete_bucket(FRONTEND_BUCKET)
    empty_and_delete_bucket(EB_BUCKET)

    print("\n[7/7] CodeBuild project")
    destroy_codebuild()

    print("\n" + "=" * 60)
    print("Teardown complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
