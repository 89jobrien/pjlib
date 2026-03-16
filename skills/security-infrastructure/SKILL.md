---
name: security-infrastructure
description: Comprehensive security infrastructure patterns including zero-trust architecture, compliance automation (SOC2/PCI-DSS), infrastructure as code security baselines, threat monitoring, and incident response automation. Use when implementing security controls, automating compliance, setting up security monitoring, or responding to security incidents.
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# Security Infrastructure

You are an expert in security infrastructure, specializing in zero-trust architecture, compliance automation, infrastructure as code security, and incident response.

## When to Use This Skill

Use this skill whenever:
- Implementing security infrastructure as code (Terraform, CloudFormation)
- Setting up security monitoring and threat detection
- Automating compliance frameworks (SOC2, PCI-DSS, HIPAA, GDPR)
- Building incident response automation
- Configuring cloud security posture management (CSPM)
- The user mentions security architecture, compliance, or incident response

## Core Security Framework

### Security Domains

**Infrastructure Security**
- Network security (VPC, security groups, NACLs)
- Identity and access management (IAM, RBAC)
- Encryption (KMS, TLS/SSL, at-rest, in-transit)
- Secrets management (Vault, AWS Secrets Manager)

**Application Security**
- Static application security testing (SAST)
- Dynamic application security testing (DAST)
- Dependency scanning and vulnerability management
- Secure development lifecycle (SDL)

**Compliance Automation**
- SOC2 Type II compliance controls
- PCI-DSS payment security standards
- HIPAA healthcare data protection
- GDPR data privacy requirements

**Incident Response**
- Security monitoring (SIEM, log aggregation)
- Threat detection (GuardDuty, Security Hub)
- Automated incident response playbooks
- Post-incident analysis and reporting

**Cloud Security**
- Cloud security posture management
- Multi-cloud security controls
- Serverless security patterns
- Container and Kubernetes security

### Security Architecture Principles

**Zero Trust**
- Never trust, always verify every request
- Least privilege access controls
- Continuous authentication and authorization
- Micro-segmentation of network resources

**Defense in Depth**
- Multiple security layers and controls
- Redundant security mechanisms
- Fail-secure defaults
- Security at every tier (network, application, data)

**Security by Design**
- Security requirements from architecture phase
- Threat modeling during design
- Security controls built into infrastructure
- Secure defaults and configuration

**Continuous Monitoring**
- Real-time security event monitoring
- Automated alerting and escalation
- Centralized logging and analysis
- Behavioral anomaly detection

**Automation First**
- Infrastructure as code for security controls
- Automated compliance validation
- Automated incident response
- Security testing in CI/CD pipelines

## Technical Implementation

### 1. Infrastructure Security as Code

**Terraform Security Baseline**

```hcl
# security/infrastructure/security-baseline.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Security baseline module
module "security_baseline" {
  source = "./modules/security-baseline"

  organization_name     = var.organization_name
  environment          = var.environment
  compliance_frameworks = ["SOC2", "PCI-DSS"]

  # Security services
  enable_cloudtrail    = true
  enable_config       = true
  enable_guardduty    = true
  enable_security_hub = true
  enable_inspector    = true

  # Network security
  enable_vpc_flow_logs     = true
  enable_network_firewall  = var.environment == "production"

  # Encryption
  kms_key_rotation_enabled = true
  s3_encryption_enabled    = true
  ebs_encryption_enabled   = true

  tags = local.security_tags
}

# KMS encryption key
resource "aws_kms_key" "security_key" {
  description              = "Security encryption key"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM root permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow service access"
        Effect = "Allow"
        Principal = {
          Service = ["s3.amazonaws.com", "rds.amazonaws.com", "logs.amazonaws.com"]
        }
        Action = ["kms:Decrypt", "kms:GenerateDataKey", "kms:CreateGrant"]
        Resource = "*"
      }
    ]
  })

  tags = merge(local.security_tags, { Purpose = "Security encryption" })
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "security_audit" {
  name           = "${var.organization_name}-security-audit"
  s3_bucket_name = aws_s3_bucket.cloudtrail_logs.bucket

  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  kms_key_id                   = aws_kms_key.security_key.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::${aws_s3_bucket.sensitive_data.bucket}/*"]
    }
  }

  insight_selector {
    insight_type = "ApiCallRateInsight"
  }

  tags = local.security_tags
}

# Security Hub for centralized findings
resource "aws_securityhub_account" "main" {
  enable_default_standards = true
}

# Config for compliance monitoring
resource "aws_config_configuration_recorder" "security_recorder" {
  name     = "security-compliance-recorder"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# WAF for application protection
resource "aws_wafv2_web_acl" "application_firewall" {
  name  = "${var.organization_name}-application-firewall"
  scope = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # Rate limiting
  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 10000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled    = true
    }
  }

  # OWASP Top 10 protection
  rule {
    name     = "OWASPTop10Protection"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesOWASPTop10RuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "OWASPTop10Protection"
      sampled_requests_enabled    = true
    }
  }

  tags = local.security_tags
}

# Secrets Manager
resource "aws_secretsmanager_secret" "application_secrets" {
  name                    = "${var.organization_name}-application-secrets"
  description            = "Application secrets and credentials"
  kms_key_id            = aws_kms_key.security_key.arn
  recovery_window_in_days = 7

  replica {
    region = var.backup_region
  }

  tags = local.security_tags
}

# IAM security policies
data "aws_iam_policy_document" "security_policy" {
  statement {
    sid    = "DenyInsecureConnections"
    effect = "Deny"
    actions = ["*"]
    resources = ["*"]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  statement {
    sid    = "RequireMFAForSensitiveActions"
    effect = "Deny"
    actions = [
      "iam:DeleteRole",
      "iam:DeleteUser",
      "s3:DeleteBucket",
      "rds:DeleteDBInstance"
    ]
    resources = ["*"]

    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["false"]
    }
  }
}

# GuardDuty threat detection
resource "aws_guardduty_detector" "security_monitoring" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = local.security_tags
}

locals {
  security_tags = {
    Environment   = var.environment
    SecurityLevel = "High"
    Compliance    = join(",", var.compliance_frameworks)
    ManagedBy     = "terraform"
    Owner         = "security-team"
  }
}
```

### 2. Security Monitoring Automation

**Python Security Monitor**

```python
# security/automation/security_monitor.py
import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SecurityMonitor:
    def __init__(self, region_name='us-east-1'):
        self.region = region_name
        self.session = boto3.Session(region_name=region_name)

        # AWS clients
        self.cloudtrail = self.session.client('cloudtrail')
        self.guardduty = self.session.client('guardduty')
        self.security_hub = self.session.client('securityhub')
        self.config = self.session.client('config')
        self.sns = self.session.client('sns')

        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def monitor_security_events(self):
        """Main monitoring function"""

        security_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'guardduty_findings': self.check_guardduty_findings(),
            'security_hub_findings': self.check_security_hub_findings(),
            'config_compliance': self.check_config_compliance(),
            'cloudtrail_anomalies': self.check_cloudtrail_anomalies(),
            'iam_analysis': self.analyze_iam_permissions(),
            'recommendations': []
        }

        security_report['recommendations'] = self.generate_recommendations(security_report)
        self.process_security_alerts(security_report)

        return security_report

    def check_guardduty_findings(self) -> List[Dict[str, Any]]:
        """Check GuardDuty for threats"""

        try:
            detectors = self.guardduty.list_detectors()
            if not detectors['DetectorIds']:
                return []

            detector_id = detectors['DetectorIds'][0]

            response = self.guardduty.list_findings(
                DetectorId=detector_id,
                FindingCriteria={
                    'Criterion': {
                        'updatedAt': {
                            'Gte': int((datetime.utcnow() - timedelta(hours=24)).timestamp() * 1000)
                        }
                    }
                }
            )

            findings = []
            if response['FindingIds']:
                finding_details = self.guardduty.get_findings(
                    DetectorId=detector_id,
                    FindingIds=response['FindingIds']
                )

                for finding in finding_details['Findings']:
                    findings.append({
                        'id': finding['Id'],
                        'type': finding['Type'],
                        'severity': finding['Severity'],
                        'title': finding['Title'],
                        'description': finding['Description']
                    })

            self.logger.info(f"Found {len(findings)} GuardDuty findings")
            return findings

        except Exception as e:
            self.logger.error(f"Error checking GuardDuty: {str(e)}")
            return []

    def analyze_iam_permissions(self) -> Dict[str, Any]:
        """Analyze IAM for security risks"""

        try:
            iam = self.session.client('iam')
            users = iam.list_users()

            analysis = {
                'overprivileged_users': [],
                'users_without_mfa': [],
                'unused_access_keys': []
            }

            for user in users['Users']:
                username = user['UserName']

                # Check MFA
                mfa_devices = iam.list_mfa_devices(UserName=username)
                if not mfa_devices['MFADevices']:
                    analysis['users_without_mfa'].append(username)

                # Check access keys
                access_keys = iam.list_access_keys(UserName=username)
                for key in access_keys['AccessKeyMetadata']:
                    last_used = iam.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
                    if 'LastUsedDate' in last_used['AccessKeyLastUsed']:
                        days_since_use = (datetime.utcnow().replace(tzinfo=None) -
                                        last_used['AccessKeyLastUsed']['LastUsedDate'].replace(tzinfo=None)).days
                        if days_since_use > 90:
                            analysis['unused_access_keys'].append({
                                'username': username,
                                'access_key_id': key['AccessKeyId'],
                                'days_unused': days_since_use
                            })

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing IAM: {str(e)}")
            return {}
```

### 3. Compliance Automation

**SOC2 and PCI-DSS Frameworks**

```python
# security/compliance/compliance_framework.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class ComplianceFramework(ABC):
    """Base class for compliance frameworks"""

    @abstractmethod
    def get_controls(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def assess_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class SOC2Compliance(ComplianceFramework):
    """SOC 2 Type II compliance"""

    def get_controls(self) -> List[Dict[str, Any]]:
        return [
            {
                'control_id': 'CC6.1',
                'title': 'Logical and Physical Access Controls',
                'description': 'Implement access controls to protect against threats',
                'aws_services': ['IAM', 'VPC', 'Security Groups'],
                'checks': ['mfa_enabled', 'least_privilege', 'network_segmentation']
            },
            {
                'control_id': 'CC6.2',
                'title': 'Transmission and Disposal of Data',
                'description': 'Secure data transmission and disposal',
                'aws_services': ['KMS', 'S3', 'EBS', 'RDS'],
                'checks': ['encryption_in_transit', 'encryption_at_rest', 'secure_disposal']
            },
            {
                'control_id': 'CC7.2',
                'title': 'System Monitoring',
                'description': 'Monitor system components continuously',
                'aws_services': ['CloudWatch', 'CloudTrail', 'Config', 'GuardDuty'],
                'checks': ['logging_enabled', 'monitoring_active', 'alert_configuration']
            }
        ]

    def assess_compliance(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess SOC 2 compliance"""

        compliance_results = {
            'framework': 'SOC2',
            'assessment_date': datetime.utcnow().isoformat(),
            'overall_score': 0,
            'control_results': [],
            'recommendations': []
        }

        total_controls = 0
        passed_controls = 0

        for control in self.get_controls():
            control_result = self._assess_control(control, resource_data)
            compliance_results['control_results'].append(control_result)

            total_controls += 1
            if control_result['status'] == 'PASS':
                passed_controls += 1

        compliance_results['overall_score'] = (passed_controls / total_controls) * 100
        return compliance_results

class PCIDSSCompliance(ComplianceFramework):
    """PCI DSS compliance"""

    def get_controls(self) -> List[Dict[str, Any]]:
        return [
            {
                'requirement': '1',
                'title': 'Install and maintain firewall configuration',
                'checks': ['firewall_configured', 'default_deny', 'documented_rules']
            },
            {
                'requirement': '2',
                'title': 'Do not use vendor-supplied defaults',
                'checks': ['default_passwords_changed', 'strong_authentication']
            },
            {
                'requirement': '3',
                'title': 'Protect stored cardholder data',
                'checks': ['data_encryption', 'secure_storage', 'access_controls']
            }
        ]
```

### 4. Incident Response Automation

**Automated Incident Response Script**

Save this as `scripts/incident_response.sh`:

```bash
#!/bin/bash
# Automated incident response

set -euo pipefail

INCIDENT_ID="${1:-$(date +%Y%m%d-%H%M%S)}"
SEVERITY="${2:-medium}"
INCIDENT_TYPE="${3:-security}"

echo "Incident Response Activated"
echo "Incident ID: $INCIDENT_ID"
echo "Severity: $SEVERITY"
echo "Type: $INCIDENT_TYPE"

# Create incident directory
INCIDENT_DIR="./incidents/$INCIDENT_ID"
mkdir -p "$INCIDENT_DIR"

# Collect system state
echo "Collecting system state..."
kubectl get pods --all-namespaces > "$INCIDENT_DIR/kubernetes_pods.txt"
kubectl get events --all-namespaces > "$INCIDENT_DIR/kubernetes_events.txt"
aws ec2 describe-instances > "$INCIDENT_DIR/ec2_instances.json"

# Collect security logs
echo "Collecting security logs..."
aws logs filter-log-events \
    --log-group-name "/aws/lambda/security-function" \
    --start-time "$(date -d '1 hour ago' +%s)000" \
    > "$INCIDENT_DIR/security_logs.json"

# Generate incident report
cat > "$INCIDENT_DIR/incident_report.md" << EOF
# Security Incident Report

**Incident ID:** $INCIDENT_ID
**Date:** $(date)
**Severity:** $SEVERITY
**Type:** $INCIDENT_TYPE

## Timeline
- $(date): Incident detected and response initiated

## Initial Assessment
- System state collected
- Security logs analyzed
- Network traffic reviewed

## Actions Taken
1. Incident response activated
2. System state preserved
3. Logs collected for analysis

## Next Steps
- [ ] Detailed log analysis
- [ ] Root cause identification
- [ ] Containment measures
- [ ] Recovery planning
- [ ] Post-incident review
EOF

echo "Incident response data collected in $INCIDENT_DIR"
```

## Security Workflow

### Step 1: Infrastructure Security Setup

1. **Deploy security baseline**
   - Apply Terraform security baseline
   - Enable all security services
   - Configure encryption and KMS

2. **Configure monitoring**
   - Set up CloudTrail logging
   - Enable GuardDuty threat detection
   - Configure Security Hub

3. **Implement access controls**
   - Configure IAM policies
   - Enforce MFA requirements
   - Set up least privilege access

### Step 2: Compliance Automation

1. **Select compliance frameworks**
   - Identify applicable frameworks (SOC2, PCI-DSS, etc.)
   - Map controls to infrastructure
   - Implement automated validation

2. **Continuous compliance monitoring**
   - AWS Config rules for compliance
   - Automated compliance assessments
   - Regular compliance reporting

### Step 3: Security Monitoring

1. **Deploy monitoring automation**
   - Security monitor Python scripts
   - Automated threat detection
   - Real-time alerting

2. **Configure incident response**
   - Incident response automation scripts
   - Runbook automation
   - Post-incident analysis

### Step 4: Continuous Improvement

1. **Regular security assessments**
   - Automated vulnerability scanning
   - Penetration testing
   - Security posture reviews

2. **Security metrics and reporting**
   - Security dashboard
   - Compliance scorecard
   - Trend analysis

## Best Practices

**Infrastructure Security**
- Use infrastructure as code for all security controls
- Enable encryption by default (at-rest and in-transit)
- Implement network segmentation
- Use managed security services

**Access Control**
- Enforce MFA for all users
- Implement least privilege access
- Rotate credentials regularly
- Use temporary credentials (IAM roles)

**Monitoring and Detection**
- Enable comprehensive logging
- Centralize log aggregation
- Set up real-time alerting
- Monitor for anomalies

**Compliance**
- Automate compliance validation
- Maintain audit trails
- Regular compliance assessments
- Document security controls

**Incident Response**
- Maintain incident response playbooks
- Automate incident detection
- Practice incident response drills
- Conduct post-incident reviews

## Common Patterns

**Multi-Account Security**
- AWS Organizations with SCPs
- Centralized logging and monitoring
- Cross-account IAM roles
- Centralized security tooling

**Serverless Security**
- Lambda execution role least privilege
- API Gateway authentication
- Secrets in environment variables (encrypted)
- VPC integration for sensitive operations

**Container Security**
- Image scanning in CI/CD
- Runtime security monitoring
- Network policies
- Pod security policies

**Data Protection**
- Encryption at rest and in transit
- Data classification and tagging
- DLP (Data Loss Prevention)
- Secure data disposal

## Remember

Security is a continuous process, not a one-time implementation. Always:
- Stay updated on security threats and best practices
- Automate security controls where possible
- Test security controls regularly
- Maintain comprehensive documentation
- Practice incident response procedures
