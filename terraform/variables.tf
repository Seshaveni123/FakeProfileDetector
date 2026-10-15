variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix for resource naming and tagging"
  type        = string
  default     = "fakeguard"
}

variable "environment" {
  description = "Environment identifier (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the custom VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet (DevOps server, public ingress)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet (internal workloads, database)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "allowed_ssh_cidr" {
  description = "Restricted CIDR block allowed to connect via SSH (port 22). Defaults to VPC CIDR; override in terraform.tfvars with trusted admin IP e.g. 203.0.113.50/32"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.allowed_ssh_cidr))
    error_message = "allowed_ssh_cidr must be a valid IPv4 CIDR block (e.g., 203.0.113.50/32 or 10.0.0.0/16)."
  }
}

variable "instance_type" {
  description = "EC2 instance type for the DevOps server"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Custom AMI ID for EC2 instance. If left empty, the latest official Ubuntu 24.04 LTS AMI in ap-south-1 will be used automatically."
  type        = string
  default     = ""
}

variable "root_volume_size" {
  description = "Size of the root EBS volume in GB"
  type        = number
  default     = 20
}

variable "enable_s3_versioning" {
  description = "Enable object versioning on the S3 artifacts bucket"
  type        = bool
  default     = true
}
