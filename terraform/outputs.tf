# ===================== NETWORKING OUTPUTS =====================

output "vpc_id" {
  description = "ID of the custom FakeGuard VPC"
  value       = aws_vpc.fakeguard_vpc.id
}

output "vpc_cidr" {
  description = "CIDR block of the FakeGuard VPC"
  value       = aws_vpc.fakeguard_vpc.cidr_block
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway attached to the VPC"
  value       = aws_internet_gateway.fakeguard_igw.id
}

output "public_subnet_id" {
  description = "ID of the public subnet where the DevOps server is deployed"
  value       = aws_subnet.public_subnet.id
}

output "private_subnet_id" {
  description = "ID of the isolated private subnet"
  value       = aws_subnet.private_subnet.id
}

# ===================== SECURITY GROUP OUTPUTS =====================

output "security_group_id" {
  description = "ID of the DevOps security group"
  value       = aws_security_group.devops_sg.id
}

output "security_group_name" {
  description = "Name of the DevOps security group"
  value       = aws_security_group.devops_sg.name
}

# ===================== COMPUTE (EC2) OUTPUTS =====================

output "ec2_instance_id" {
  description = "ID of the DevOps Server EC2 instance"
  value       = aws_instance.devops_server.id
}

output "ec2_instance_ami" {
  description = "AMI ID used by the DevOps Server"
  value       = aws_instance.devops_server.ami
}

output "ec2_instance_type" {
  description = "Instance type of the DevOps Server"
  value       = aws_instance.devops_server.instance_type
}

output "ec2_public_ip" {
  description = "Public IP address of the DevOps Server"
  value       = aws_instance.devops_server.public_ip
}

output "ec2_private_ip" {
  description = "Private IP address of the DevOps Server inside the VPC"
  value       = aws_instance.devops_server.private_ip
}

# ===================== STORAGE (S3) OUTPUTS =====================

output "s3_bucket_name" {
  description = "Name of the private S3 artifacts bucket"
  value       = aws_s3_bucket.fakeguard_artifacts.id
}

output "s3_bucket_arn" {
  description = "ARN of the private S3 artifacts bucket"
  value       = aws_s3_bucket.fakeguard_artifacts.arn
}

output "s3_bucket_domain_name" {
  description = "Regional domain name of the S3 artifacts bucket"
  value       = aws_s3_bucket.fakeguard_artifacts.bucket_regional_domain_name
}

# ===================== IAM OUTPUTS =====================

output "iam_role_name" {
  description = "Name of the IAM role attached to the DevOps EC2 instance"
  value       = aws_iam_role.devops_ec2_role.name
}

output "iam_role_arn" {
  description = "ARN of the IAM role attached to the DevOps EC2 instance"
  value       = aws_iam_role.devops_ec2_role.arn
}

output "iam_instance_profile_name" {
  description = "Name of the IAM instance profile"
  value       = aws_iam_instance_profile.devops_instance_profile.name
}
