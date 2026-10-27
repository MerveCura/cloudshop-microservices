terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      Project     = "CloudShop"
      Environment = "terraform-lab"
      ManagedBy   = "Terraform"
    }
  }
}

# VPC
resource "aws_vpc" "cloudshop" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "cloudshop-vpc"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.cloudshop.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "cloudshop-public-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.cloudshop.id

  tags = {
    Name = "cloudshop-igw"
  }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.cloudshop.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "cloudshop-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# PRIVATE SUBNET 1 - Frankfurt AZ-a
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.cloudshop.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-central-1a"

  tags = {
    Name = "cloudshop-private-a"
  }
}

# PRIVATE SUBNET 2 - Frankfurt AZ-b
resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.cloudshop.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "eu-central-1b"

  tags = {
    Name = "cloudshop-private-b"
  }
}

# EC2 SECURITY GROUP
resource "aws_security_group" "ec2" {
  name        = "cloudshop-ec2-sg"
  description = "CloudShop EC2 security group"
  vpc_id      = aws_vpc.cloudshop.id

  tags = {
    Name = "cloudshop-ec2-sg"
  }
}

# EC2 - HTTP INBOUND
resource "aws_vpc_security_group_ingress_rule" "ec2_http" {
  security_group_id = aws_security_group.ec2.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

# EC2 - ALL OUTBOUND
resource "aws_vpc_security_group_egress_rule" "ec2_outbound" {
  security_group_id = aws_security_group.ec2.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# RDS SECURITY GROUP
resource "aws_security_group" "rds" {
  name        = "cloudshop-rds-sg"
  description = "CloudShop PostgreSQL security group"
  vpc_id      = aws_vpc.cloudshop.id

  tags = {
    Name = "cloudshop-rds-sg"
  }
}

# RDS - ONLY EC2 CAN CONNECT
resource "aws_vpc_security_group_ingress_rule" "rds_postgres" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.ec2.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
}

# PUBLIC SUBNET NACL
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.cloudshop.id
  subnet_ids = [aws_subnet.public.id]

  ingress {
    rule_no    = 100
    protocol   = "-1"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    rule_no    = 100
    protocol   = "-1"
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "cloudshop-public-nacl"
  }
}

# Güncel Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# EC2 Instance
resource "aws_instance" "cloudshop" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2.id]

  tags = {
    Name = "cloudshop-terraform-ec2"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "cloudshop" {
  bucket_prefix = "cloudshop-terraform-lab-"

  tags = {
    Name = "cloudshop-storage"
  }
}

# Public erişimi engelle
resource "aws_s3_bucket_public_access_block" "cloudshop" {
  bucket = aws_s3_bucket.cloudshop.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# RDS için iki farklı AZ'daki private subnet'ler
resource "aws_db_subnet_group" "cloudshop" {
  name = "cloudshop-terraform-lab-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  tags = {
    Name = "cloudshop-db-subnet-group"
  }
}

# PostgreSQL veritabanı
resource "aws_db_instance" "cloudshop" {
  identifier = "cloudshop-terraform-db"

  engine         = "postgres"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  username                    = "cloudshopadmin"
  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.cloudshop.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "cloudshop-terraform-rds"
  }
}