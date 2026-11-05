# ---------------------------------------------------------------------------
# NETWORKING — intentionally misconfigured
# Findings:
#  N1. No VPC Flow Logs enabled (CIS 3.9 / loss of network visibility)
#  N2. Default Security Group of the VPC left with open ingress/egress
#  N3. Custom Security Group allows 0.0.0.0/0 on SSH(22), RDP(3389), and DB ports
#  N4. Network ACL allows ALL traffic in both directions
#  N5. Subnet auto-assigns public IPs to every instance launched into it
#  N6. Internet Gateway attached with no compensating controls (WAF/NACL) at all
# ---------------------------------------------------------------------------

resource "aws_vpc" "sandbox" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.name_prefix}-vpc"
  }
}

# N2: default SG is left in its wide-open state instead of being locked down
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.sandbox.id

  ingress {
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    protocol    = -1
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_internet_gateway" "sandbox" {
  vpc_id = aws_vpc.sandbox.id

  tags = {
    Name = "${var.name_prefix}-igw"
  }
}

# N5: public subnet auto-assigns public IPs
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.sandbox.id
  cidr_block              = var.public_subnet_cidr
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.name_prefix}-public-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.sandbox.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.sandbox.id
  }

  tags = {
    Name = "${var.name_prefix}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# N4: NACL allows everything, both directions — negates any SG tightening
resource "aws_network_acl" "wide_open" {
  vpc_id     = aws_vpc.sandbox.id
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
    Name = "${var.name_prefix}-nacl-allow-all"
  }
}

# N3: security group wide open to the internet on admin + database ports
resource "aws_security_group" "wide_open" {
  name        = "${var.name_prefix}-wide-open-sg"
  description = "Sandbox SG with deliberately permissive rules"
  vpc_id      = aws_vpc.sandbox.id

  ingress {
    description = "SSH open to the world"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "RDP open to the world"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "MySQL/Aurora open to the world"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Postgres open to the world"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "All ports open to the world, mislabeled as a management-only range"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name_prefix}-wide-open-sg"
  }
}

# N1: no aws_flow_log resource defined anywhere in this module (intentional omission)
