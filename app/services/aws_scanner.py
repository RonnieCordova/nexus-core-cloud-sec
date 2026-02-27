from __future__ import annotations

from typing import Any


def verify_aws_access(account: dict[str, Any]) -> dict[str, str]:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required to verify AWS access") from exc

    sts = boto3.client("sts")
    assumed = sts.assume_role(
        RoleArn=account["role_arn"],
        RoleSessionName="nexus-account-verify",
        ExternalId=account["external_id"],
        DurationSeconds=900,
    )

    return {
        "assumed_role_arn": assumed["AssumedRoleUser"]["Arn"],
        "account": account["account_id"],
        "status": "verified",
    }


def _public_sg_finding(group_id: str, port: int) -> dict[str, str]:
    return {
        "severity": "critical",
        "service": "ec2",
        "resource_id": group_id,
        "title": "Security Group exposed to internet",
        "description": f"Ingress rule allows 0.0.0.0/0 on sensitive port {port}.",
    }


def run_security_scan(account: dict[str, Any]) -> tuple[dict[str, int], list[dict[str, str]]]:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required to execute AWS scans") from exc

    findings: list[dict[str, str]] = []

    sts = boto3.client("sts")
    assumed = sts.assume_role(
        RoleArn=account["role_arn"],
        RoleSessionName="nexus-security-scan",
        ExternalId=account["external_id"],
        DurationSeconds=900,
    )

    creds = assumed["Credentials"]
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )

    s3 = session.client("s3")
    for bucket in s3.list_buckets().get("Buckets", []):
        name = bucket["Name"]
        acl = s3.get_bucket_acl(Bucket=name)
        for grant in acl.get("Grants", []):
            grantee = grant.get("Grantee", {})
            uri = grantee.get("URI", "")
            if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                findings.append(
                    {
                        "severity": "critical",
                        "service": "s3",
                        "resource_id": name,
                        "title": "Public S3 bucket ACL",
                        "description": "Bucket ACL grants public or broad authenticated access.",
                    }
                )
                break

    regions = [r.strip() for r in account["regions"].split(",") if r.strip()]
    sensitive_ports = {22, 3389}
    for region in regions:
        ec2 = session.client("ec2", region_name=region)
        response = ec2.describe_security_groups()
        for sg in response.get("SecurityGroups", []):
            sg_id = sg.get("GroupId", "unknown")
            for permission in sg.get("IpPermissions", []):
                from_port = permission.get("FromPort")
                to_port = permission.get("ToPort")
                port = from_port if from_port == to_port else -1
                for ip_range in permission.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        if port in sensitive_ports or port == -1:
                            findings.append(_public_sg_finding(sg_id, port if port != -1 else 0))

    summary = {
        "total_findings": len(findings),
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }
    return summary, findings
