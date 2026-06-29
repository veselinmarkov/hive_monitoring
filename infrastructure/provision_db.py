#!/usr/bin/env python3
"""Provisions the EC2 + EBS host that runs MySQL for the Hive app.

Replaces the RDS instance that used to be created inline by buildspec.yml.
Runs from its own CodeBuild project (see infra-buildspec.yml), separate from
the app build/deploy pipeline. Idempotent: if the named instance already
exists, no infrastructure is created or modified.

Configuration is read from environment variables (set in infra-buildspec.yml):
  AWS_DEFAULT_REGION    - region to provision in (default: eu-central-1)
  EB_BUCKET             - existing S3 bucket used to stage the sql_init dumps (required)
  DB_INSTANCE_NAME      - EC2 Name tag (default: hive-mysql-host)
  DB_INSTANCE_TYPE      - EC2 instance type (default: t3.small)
  DB_VOLUME_SIZE_GB     - size of the attached data volume (default: 20)
  DB_NAME               - MySQL database name (default: hive)
  DB_USERNAME           - MySQL application user (default: hiveadmin)

The following are read from SSM Parameter Store at runtime:
  /hive/infra/subnet-id              - subnet the instance launches into
  /hive/infra/app-security-group-id  - security group of the app servers that need DB access

On success, writes connection details to SSM Parameter Store under /hive/db/*,
which the app pipeline (buildspec.yml) reads to set the EB DATABASE_URL.
"""
import json
import os
import secrets
import time

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")
EB_BUCKET = os.environ["EB_BUCKET"]

INSTANCE_NAME = os.environ.get("DB_INSTANCE_NAME", "hive-mysql-host")
INSTANCE_TYPE = os.environ.get("DB_INSTANCE_TYPE", "t3.small")
VOLUME_SIZE_GB = int(os.environ.get("DB_VOLUME_SIZE_GB", "20"))
DB_NAME = os.environ.get("DB_NAME", "hive")
DB_USERNAME = os.environ.get("DB_USERNAME", "hiveadmin")

SG_NAME = "hive-mysql-sg"
ROLE_NAME = "hive-mysql-ec2-role"
INSTANCE_PROFILE_NAME = "hive-mysql-ec2-profile"
DATA_DEVICE = "/dev/sdf"
SQL_INIT_S3_PREFIX = "db-init/"
UBUNTU_AMI_PARAM = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"

SUBNET_ID_PARAM = "/hive/infra/subnet-id"
APP_SG_PARAM = "/hive/infra/app-security-group-id"

HOST_PARAM = "/hive/db/host"
PASSWORD_PARAM = "/hive/db/password"
NAME_PARAM = "/hive/db/name"
USERNAME_PARAM = "/hive/db/username"

ec2 = boto3.client("ec2", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)
iam = boto3.client("iam", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

def _require_ssm_param(name):
    try:
        return ssm.get_parameter(Name=name)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            raise SystemExit(
                f"ERROR: Required SSM parameter '{name}' not found. "
                f"Create it with: aws ssm put-parameter --name {name} --value <value> --type String --region {REGION}"
            )
        raise

SUBNET_ID = _require_ssm_param(SUBNET_ID_PARAM)
APP_SECURITY_GROUP_ID = _require_ssm_param(APP_SG_PARAM)


def find_existing_instance():
    resp = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
        {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
    ])
    for reservation in resp["Reservations"]:
        for instance in reservation["Instances"]:
            return instance
    return None


def ensure_security_group():
    vpc_id = ec2.describe_subnets(SubnetIds=[SUBNET_ID])["Subnets"][0]["VpcId"]
    resp = ec2.describe_security_groups(Filters=[
        {"Name": "group-name", "Values": [SG_NAME]},
        {"Name": "vpc-id", "Values": [vpc_id]},
    ])
    if resp["SecurityGroups"]:
        sg_id = resp["SecurityGroups"][0]["GroupId"]
    else:
        sg_id = ec2.create_security_group(
            GroupName=SG_NAME,
            Description="Allows the app servers to reach the Hive MySQL host on 3306",
            VpcId=vpc_id,
        )["GroupId"]

    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort": 3306,
                "ToPort": 3306,
                "UserIdGroupPairs": [{"GroupId": APP_SECURITY_GROUP_ID}],
            }],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
            raise
    return sg_id


def ensure_iam_instance_profile():
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    }
    try:
        iam.create_role(RoleName=ROLE_NAME, AssumeRolePolicyDocument=json.dumps(trust_policy))
    except ClientError as e:
        if e.response["Error"]["Code"] != "EntityAlreadyExists":
            raise

    # SSM Session Manager access instead of SSH keys / open port 22.
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
    )
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="hive-mysql-ec2-inline",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["ssm:GetParameter", "ssm:PutParameter"],
                    "Resource": f"arn:aws:ssm:{REGION}:*:parameter/hive/db/*",
                },
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{EB_BUCKET}/{SQL_INIT_S3_PREFIX}*",
                },
            ],
        }),
    )

    try:
        iam.create_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME)
        iam.add_role_to_instance_profile(InstanceProfileName=INSTANCE_PROFILE_NAME, RoleName=ROLE_NAME)
        time.sleep(15)  # IAM eventual consistency before EC2 can use the profile
    except ClientError as e:
        if e.response["Error"]["Code"] != "EntityAlreadyExists":
            raise

    return INSTANCE_PROFILE_NAME


def get_or_create_db_password():
    try:
        return ssm.get_parameter(Name=PASSWORD_PARAM, WithDecryption=True)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "ParameterNotFound":
            raise
    password = secrets.token_urlsafe(24)
    ssm.put_parameter(Name=PASSWORD_PARAM, Value=password, Type="SecureString", Overwrite=True)
    return password


def latest_ubuntu_ami():
    return ssm.get_parameter(Name=UBUNTU_AMI_PARAM)["Parameter"]["Value"]


def upload_sql_init():
    base = os.path.join(os.path.dirname(__file__), "..", "sql_init")
    for root, _, files in os.walk(base):
        for filename in files:
            local_path = os.path.join(root, filename)
            rel_path = os.path.relpath(local_path, base)
            s3.upload_file(local_path, EB_BUCKET, f"{SQL_INIT_S3_PREFIX}{rel_path}")


def build_user_data():
    return rf"""#!/bin/bash
set -euxo pipefail
exec > /var/log/hive-mysql-init.log 2>&1

apt-get update
apt-get install -y mysql-server awscli

DATA_DEV=""
for candidate in /dev/nvme1n1 /dev/xvdf /dev/sdf; do
  for i in $(seq 1 30); do
    if [ -e "$candidate" ]; then DATA_DEV="$candidate"; break 2; fi
    sleep 2
  done
done
if [ -z "$DATA_DEV" ]; then echo "data volume never appeared" >&2; exit 1; fi

if ! blkid "$DATA_DEV" > /dev/null 2>&1; then
  mkfs.ext4 "$DATA_DEV"
fi

mkdir -p /var/lib/mysql-data
UUID=$(blkid -s UUID -o value "$DATA_DEV")
grep -q "$UUID" /etc/fstab || echo "UUID=$UUID /var/lib/mysql-data ext4 defaults,nofail 0 2" >> /etc/fstab
mount /var/lib/mysql-data

systemctl stop mysql
if [ -z "$(ls -A /var/lib/mysql-data)" ]; then
  rsync -a /var/lib/mysql/ /var/lib/mysql-data/
fi
sed -i 's#datadir\s*=.*#datadir = /var/lib/mysql-data#' /etc/mysql/mysql.conf.d/mysqld.cnf
echo "alias /var/lib/mysql/ -> /var/lib/mysql-data/," >> /etc/apparmor.d/tunables/alias
systemctl reload apparmor || true
sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
systemctl start mysql

DB_PASSWORD=$(aws ssm get-parameter --name "{PASSWORD_PARAM}" --with-decryption --region {REGION} --query 'Parameter.Value' --output text)

mysql -u root <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_PASSWORD';
CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '{DB_USERNAME}'@'%' IDENTIFIED WITH mysql_native_password BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USERNAME}'@'%';
FLUSH PRIVILEGES;
SQL

aws s3 sync "s3://{EB_BUCKET}/{SQL_INIT_S3_PREFIX}" /tmp/db-init --region {REGION}
mysql -u root -p"$DB_PASSWORD" {DB_NAME} < /tmp/db-init/definitions/samples_definition.sql
zcat /tmp/db-init/hive_wo_samples.dmp.gz | mysql -u root -p"$DB_PASSWORD" {DB_NAME}
for dump in /tmp/db-init/samples_monthly_dump_2024-05.bkp.gz /tmp/db-init/samples_monthly_dump_2024-06.bkp.gz /tmp/db-init/samples_monthly_dump_2024-07.bkp.gz; do
  zcat "$dump" | mysql -u root -p"$DB_PASSWORD" {DB_NAME}
done

touch /var/lib/hive-mysql-init-complete
"""


def launch_instance(ami_id, sg_id, instance_profile_name, user_data):
    last_error = None
    for attempt in range(5):
        try:
            resp = ec2.run_instances(
                ImageId=ami_id,
                InstanceType=INSTANCE_TYPE,
                MinCount=1,
                MaxCount=1,
                SubnetId=SUBNET_ID,
                SecurityGroupIds=[sg_id],
                IamInstanceProfile={"Name": instance_profile_name},
                UserData=user_data,
                BlockDeviceMappings=[
                    {
                        "DeviceName": "/dev/sda1",
                        "Ebs": {"VolumeSize": 8, "VolumeType": "gp3", "DeleteOnTermination": True},
                    },
                    {
                        "DeviceName": DATA_DEVICE,
                        "Ebs": {"VolumeSize": VOLUME_SIZE_GB, "VolumeType": "gp3", "DeleteOnTermination": False},
                    },
                ],
                TagSpecifications=[{
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": INSTANCE_NAME}],
                }],
            )
            return resp["Instances"][0]["InstanceId"]
        except ClientError as e:
            last_error = e
            if e.response["Error"]["Code"] == "InvalidParameterValue" and "Invalid IAM Instance Profile" in str(e):
                time.sleep(10)
                continue
            raise
    raise last_error


def wait_for_running(instance_id):
    ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    return resp["Reservations"][0]["Instances"][0]["PrivateIpAddress"]


def wait_for_mysql_ready(instance_id, timeout_seconds=900):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            command_id = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": ["test -f /var/lib/hive-mysql-init-complete && echo READY || echo NOT_READY"]},
            )["Command"]["CommandId"]
        except ClientError:
            time.sleep(15)
            continue
        time.sleep(5)
        try:
            invocation = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        except ClientError:
            time.sleep(15)
            continue
        if invocation["Status"] == "Success" and "READY" in invocation["StandardOutputContent"]:
            return
        time.sleep(20)
    raise TimeoutError("Timed out waiting for MySQL initialization to complete on the instance")


def main():
    existing = find_existing_instance()
    sg_id = ensure_security_group()

    if existing:
        print(f"Instance {INSTANCE_NAME} already exists ({existing['InstanceId']}, "
              f"{existing['State']['Name']}) - skipping creation.")
        if existing.get("PrivateIpAddress"):
            ssm.put_parameter(Name=HOST_PARAM, Value=existing["PrivateIpAddress"], Type="String", Overwrite=True)
        return

    instance_profile_name = ensure_iam_instance_profile()
    get_or_create_db_password()
    ami_id = latest_ubuntu_ami()
    upload_sql_init()
    user_data = build_user_data()

    print(f"Launching {INSTANCE_TYPE} Ubuntu instance with a {VOLUME_SIZE_GB}GB data volume...")
    instance_id = launch_instance(ami_id, sg_id, instance_profile_name, user_data)
    private_ip = wait_for_running(instance_id)
    print(f"Instance {instance_id} running at {private_ip}. Waiting for MySQL setup to finish...")
    wait_for_mysql_ready(instance_id)

    ssm.put_parameter(Name=HOST_PARAM, Value=private_ip, Type="String", Overwrite=True)
    ssm.put_parameter(Name=NAME_PARAM, Value=DB_NAME, Type="String", Overwrite=True)
    ssm.put_parameter(Name=USERNAME_PARAM, Value=DB_USERNAME, Type="String", Overwrite=True)
    print(f"MySQL ready on {private_ip}. Connection details stored under /hive/db/* in Parameter Store.")


if __name__ == "__main__":
    main()
