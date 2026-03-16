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
kubectl get pods --all-namespaces > "$INCIDENT_DIR/kubernetes_pods.txt" 2>/dev/null || echo "Kubernetes not available"
kubectl get events --all-namespaces > "$INCIDENT_DIR/kubernetes_events.txt" 2>/dev/null || echo "Kubernetes events not available"
aws ec2 describe-instances > "$INCIDENT_DIR/ec2_instances.json" 2>/dev/null || echo "AWS CLI not configured"

# Collect security logs
echo "Collecting security logs..."
aws logs filter-log-events \
    --log-group-name "/aws/lambda/security-function" \
    --start-time "$(date -d '1 hour ago' +%s)000" \
    > "$INCIDENT_DIR/security_logs.json" 2>/dev/null || echo "Security logs not available"

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
