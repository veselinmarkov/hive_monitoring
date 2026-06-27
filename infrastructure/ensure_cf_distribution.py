#!/usr/bin/env python3
"""Creates a CloudFront distribution in front of the Elastic Beanstalk environment.

Idempotent: on subsequent runs it reads the existing distribution ID from SSM
and skips creation. Prints the CloudFront HTTPS URL on every run.

Cache behaviours (evaluated in order):
  /api/*      — caching disabled, all methods forwarded (dynamic Django responses)
  /static/*   — caching enabled with long TTL (hashed filenames, safe to cache)
  /*          — caching disabled (index.html must always be fresh)

SSM parameter written:
  /hive/infra/cloudfront-eb-distribution-id

Usage:
    python infrastructure/ensure_cf_distribution.py
"""
import os
import time

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")
EB_ENV_NAME = os.environ.get("EB_ENVIRONMENT_NAME", "hive-backend-env")
SSM_PARAM = "/hive/infra/cloudfront-eb-distribution-id"

# AWS managed policy IDs (global, not region-specific)
CACHE_POLICY_DISABLED   = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
CACHE_POLICY_OPTIMIZED  = "658327ea-f89d-4fab-a63d-7e88639e58f6"
ORIGIN_REQUEST_ALL_EXCEPT_HOST = "b689b0a8-53d0-40ab-baf2-68738e2966ac"

ssm = boto3.client("ssm", region_name=REGION)
eb = boto3.client("elasticbeanstalk", region_name=REGION)
cf = boto3.client("cloudfront", region_name="us-east-1")  # CloudFront is always us-east-1


def get_eb_url():
    resp = eb.describe_environments(EnvironmentNames=[EB_ENV_NAME])
    envs = resp["Environments"]
    if not envs:
        raise SystemExit(f"ERROR: EB environment '{EB_ENV_NAME}' not found.")
    cname = envs[0].get("CNAME")
    if not cname:
        raise SystemExit(f"ERROR: EB environment '{EB_ENV_NAME}' has no CNAME yet.")
    return cname


def get_existing_distribution_id():
    try:
        return ssm.get_parameter(Name=SSM_PARAM)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            return None
        raise


def create_distribution(eb_url):
    caller_ref = f"hive-backend-{int(time.time())}"
    resp = cf.create_distribution(DistributionConfig={
        "CallerReference": caller_ref,
        "Comment": "Hive backend — CloudFront HTTPS in front of Elastic Beanstalk",
        "Enabled": True,
        "HttpVersion": "http2and3",
        "Origins": {
            "Quantity": 1,
            "Items": [{
                "Id": "hive-eb-origin",
                "DomainName": eb_url,
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only",
                },
            }],
        },
        "DefaultCacheBehavior": {
            # /* — index.html must always be fresh
            "TargetOriginId": "hive-eb-origin",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"],
                "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
            },
            "CachePolicyId": CACHE_POLICY_DISABLED,
            "OriginRequestPolicyId": ORIGIN_REQUEST_ALL_EXCEPT_HOST,
            "Compress": True,
        },
        "CacheBehaviors": {
            "Quantity": 2,
            "Items": [
                {
                    # /api/* — dynamic Django responses, never cache, all methods
                    "PathPattern": "/api/*",
                    "TargetOriginId": "hive-eb-origin",
                    "ViewerProtocolPolicy": "redirect-to-https",
                    "AllowedMethods": {
                        "Quantity": 7,
                        "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    },
                    "CachePolicyId": CACHE_POLICY_DISABLED,
                    "OriginRequestPolicyId": ORIGIN_REQUEST_ALL_EXCEPT_HOST,
                    "Compress": True,
                },
                {
                    # /static/* — hashed filenames, safe to cache aggressively
                    "PathPattern": "/static/*",
                    "TargetOriginId": "hive-eb-origin",
                    "ViewerProtocolPolicy": "redirect-to-https",
                    "AllowedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"],
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    },
                    "CachePolicyId": CACHE_POLICY_OPTIMIZED,
                    "OriginRequestPolicyId": ORIGIN_REQUEST_ALL_EXCEPT_HOST,
                    "Compress": True,
                },
            ],
        },
        "CustomErrorResponses": {"Quantity": 0},
        "PriceClass": "PriceClass_100",  # US, Canada, Europe only — cheapest
    })
    dist = resp["Distribution"]
    return dist["Id"], dist["DomainName"]


def main():
    print(f"Fetching EB environment URL for '{EB_ENV_NAME}'...")
    eb_url = get_eb_url()
    print(f"EB origin: {eb_url}")

    dist_id = get_existing_distribution_id()
    if dist_id:
        print(f"CloudFront distribution already exists: {dist_id}")
        dist = cf.get_distribution(Id=dist_id)["Distribution"]
        cf_url = dist["DomainName"]
    else:
        print("Creating CloudFront distribution (this takes 10-15 min to deploy globally)...")
        dist_id, cf_url = create_distribution(eb_url)
        ssm.put_parameter(Name=SSM_PARAM, Value=dist_id, Type="String", Overwrite=True)
        print(f"Distribution created: {dist_id}")
        print(f"Distribution ID saved to SSM: {SSM_PARAM}")

    print(f"\nCloudFront HTTPS URL: https://{cf_url}")


if __name__ == "__main__":
    main()
