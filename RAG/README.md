# Enterprise Knowledge Base Q&A — Amazon Bedrock RAG
### TechNova Corporation · Internal Deployment Guide

---

## Architecture

```
Employee Browser
      │
      ▼
 EC2 (Streamlit app)  ←──IAM Role──→  Amazon Bedrock
      │                                    │
      │                           ┌────────┴────────┐
      │                    Knowledge Base     Foundation Model
      │                    (Retrieval)    (Claude 3.5 Sonnet)
      │                           │
      │                    Amazon OpenSearch
      │                    Serverless (Vector)
      │                           │
      └──────────────────→ Amazon S3 (Documents)
```

---

## Prerequisites

| Item | Value |
|------|-------|
| AWS Region | `us-east-1` |
| EC2 AMI | Amazon Linux 2023 |
| Instance Type | `t3.medium` or larger |
| Python | 3.11+ |
| IAM Role | See permissions below |

---

## Step 1 — Prepare Your S3 Document Bucket

```bash
# Create the bucket
aws s3 mb s3://technova-kb-documents --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket technova-kb-documents \
  --versioning-configuration Status=Enabled

# Upload the policy handbook PDF
aws s3 cp TechNova_Enterprise_Policy_Handbook.pdf \
  s3://technova-kb-documents/policies/
```

---

## Step 2 — Create Amazon Bedrock Knowledge Base (Console)

1. Go to **Amazon Bedrock → Knowledge Bases → Create**
2. **Name:** `technova-enterprise-kb`
3. **IAM Role:** Let Bedrock create a service role
4. **Data Source:** S3 → `s3://technova-kb-documents/`
5. **Embeddings Model:** Amazon Titan Embeddings V2 (1536 dim)
6. **Vector Store:** Amazon OpenSearch Serverless (auto-create)
7. **Chunking:** Hierarchical · Parent 1500 tokens · Child 300 tokens · Overlap 50
8. Click **Create**, then **Sync data source**
9. Copy the **Knowledge Base ID** (format: `XXXXXXXXXX`)

---

## Step 3 — IAM Role for EC2

Attach this inline policy to your EC2 instance role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockRAG",
      "Effect": "Allow",
      "Action": [
        "bedrock:RetrieveAndGenerate",
        "bedrock:Retrieve",
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3ReadDocuments",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::technova-kb-documents",
        "arn:aws:s3:::technova-kb-documents/*"
      ]
    }
  ]
}
```

> **No AWS credentials in code** — the app uses `boto3` which automatically
> picks up the EC2 instance role via the instance metadata service.

---

## Step 4 — Launch EC2 & Deploy App

### User Data script (paste at EC2 launch)

```bash
#!/bin/bash
yum update -y
yum install -y python3.11 python3.11-pip git

# App directory
mkdir -p /opt/technova-kb && cd /opt/technova-kb

# Copy files (or clone from internal Git)
# git clone https://git.technova.internal/ai/kb-app .

pip3.11 install streamlit==1.35.0 boto3==1.34.84

# Streamlit config
mkdir -p /root/.streamlit
cat > /root/.streamlit/config.toml <<EOF
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true
EOF

# Systemd service
cat > /etc/systemd/system/technova-kb.service <<EOF
[Unit]
Description=TechNova Knowledge Base Q&A
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/technova-kb
ExecStart=/usr/bin/python3.11 -m streamlit run app.py
Restart=always
RestartSec=10
Environment=AWS_DEFAULT_REGION=us-east-1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable technova-kb
systemctl start technova-kb
```

---

## Step 5 — Configure app.py

Edit the constants at the top of `app.py`:

```python
AWS_REGION        = "us-east-1"
KNOWLEDGE_BASE_ID = "XXXXXXXXXX"   # ← your KB ID from Step 2
MODEL_ARN         = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
```

---

## Step 6 — Security (Production Hardening)

```
EC2 Security Group:
  Inbound:  8501 from internal CIDR only (e.g. 10.0.0.0/8)
  Outbound: 443 to AWS endpoints (Bedrock, S3, OpenSearch)

Recommended additions:
  - Application Load Balancer + ACM certificate (HTTPS)
  - AWS WAF on ALB
  - Cognito / SAML SSO for employee authentication
  - CloudWatch Logs for Streamlit output
  - VPC Endpoints for Bedrock & S3 (no internet traffic)
```

---

## Running Locally (Dev)

```bash
pip install -r requirements.txt

# Use a named profile with Bedrock permissions
export AWS_PROFILE=technova-dev
export AWS_DEFAULT_REGION=us-east-1

streamlit run app.py
# → http://localhost:8501
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ResourceNotFoundException` | Wrong KB ID | Check `KNOWLEDGE_BASE_ID` in app.py |
| `AccessDeniedException` | Missing IAM perms | Add `bedrock:RetrieveAndGenerate` to role |
| `ValidationException` | Wrong model ARN | Verify Claude 3.5 Sonnet ARN for your region |
| `NoCredentialsError` | No IAM role on EC2 | Attach instance profile with Bedrock policy |
| Empty citations | KB not synced | Re-sync data source in Bedrock console |

---

## File Structure

```
/opt/technova-kb/
├── app.py                              # Streamlit RAG application
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
└── docs/
    └── TechNova_Enterprise_Policy_Handbook.pdf   # Sample KB document
```

---

*TechNova Corporation — AI Platform Engineering · Confidential*
