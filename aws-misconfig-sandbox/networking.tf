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

# N2 [REMEDIATED Day 8, B13]: default SG emptied (no ingress or egress rules), per CIS 5.5
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.sandbox.id

  # Explicit empty lists: omitting the blocks would leave the existing rules in place.
  ingress = []
  egress  = []
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

# N3 [REMEDIATED Day 8, B09]: the internet-open ingress rules (22, 3389, 3306, 5432, 0-65535)
# were removed. The group is unattached, so it keeps no ingress rules at all.
resource "aws_security_group" "wide_open" {
  name        = "${var.name_prefix}-wide-open-sg"
  description = "Sandbox SG with deliberately permissive rules"
  vpc_id      = aws_vpc.sandbox.id

  # Explicit empty list: omitting the blocks would leave the existing rules in place.
  ingress = []

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
