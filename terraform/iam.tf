# ===================== IAM ROLES & LEAST-PRIVILEGE POLICIES =====================

# IAM Role assumed by EC2 DevOps Server
resource "aws_iam_role" "devops_ec2_role" {
  name_prefix = "${var.project_name}-ec2-role-"
  description = "IAM execution role for FakeGuard AI DevOps EC2 instance"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ec2-role"
  }
}

# Least-Privilege IAM Policy for S3 access (scoped strictly to FakeGuard artifacts bucket)
resource "aws_iam_policy" "devops_s3_policy" {
  name_prefix = "${var.project_name}-s3-policy-"
  description = "Least-privilege policy granting read/write operations only to FakeGuard artifacts S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBucketContents"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = aws_s3_bucket.fakeguard_artifacts.arn
      },
      {
        Sid    = "ReadWriteObjects"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.fakeguard_artifacts.arn}/*"
      }
    ]
  })
}

# Attach S3 Least-Privilege Policy to the EC2 Role
resource "aws_iam_role_policy_attachment" "s3_attach" {
  role       = aws_iam_role.devops_ec2_role.name
  policy_arn = aws_iam_policy.devops_s3_policy.arn
}

# Attach AWS SSM Managed Policy for secure Session Manager administration
resource "aws_iam_role_policy_attachment" "ssm_attach" {
  role       = aws_iam_role.devops_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# IAM Instance Profile to attach the Role to the EC2 Instance
resource "aws_iam_instance_profile" "devops_instance_profile" {
  name_prefix = "${var.project_name}-instance-profile-"
  role        = aws_iam_role.devops_ec2_role.name

  tags = {
    Name = "${var.project_name}-instance-profile"
  }
}
