# ===============================
# Security List: API Endpoint
# ===============================
resource "oci_core_security_list" "sl_api" {
  display_name   = var.sl_api_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "External access to Kubernetes API endpoint"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  ingress_security_rules {
    source      = "10.0.10.0/24"
    protocol    = "6"
    description = "Worker → Kubernetes API endpoint"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  ingress_security_rules {
    source      = "10.0.10.0/24"
    protocol    = "6"
    description = "Worker → control plane communication"
    tcp_options {
      min = 12250
      max = 12250
    }
  }

  ingress_security_rules {
    source      = "10.0.10.0/24"
    protocol    = "1"
    description = "ICMP path discovery"
    icmp_options {
      type = 3
      code = 4
    }
  }

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "Allow HTTP ingress (80)"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "Allow HTTPS ingress (443)"
    tcp_options {
      min = 443
      max = 443
    }
  }

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "6"
    description = "Allow all outbound traffic"
  }

  lifecycle {
    ignore_changes = [
      ingress_security_rules,
      egress_security_rules,
      freeform_tags,
      defined_tags
    ]
  }
}

# ===============================
# Security List: Worker Nodes
# ===============================
resource "oci_core_security_list" "sl_nodes" {
  display_name   = var.sl_nodes_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  ingress_security_rules {
    source      = "10.0.10.0/24"
    protocol    = "all"
    description = "Pod-to-pod communication across worker nodes"
  }

  ingress_security_rules {
    source      = "10.0.0.0/28"
    protocol    = "6"
    description = "API endpoint to node TCP 6443"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "SSH to worker nodes"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    source      = "10.0.20.0/24"
    protocol    = "6"
    description = "Traffic from LoadBalancer to nodes"
    tcp_options {
      min = 30809
      max = 32627
    }
  }

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
    description = "Worker node outbound internet via NAT"
  }

  lifecycle {
    ignore_changes = [
      ingress_security_rules,
      egress_security_rules,
      freeform_tags,
      defined_tags
    ]
  }
}

# ===============================
# Security List: Load Balancer
# ===============================
resource "oci_core_security_list" "sl_lb" {
  display_name   = var.sl_lb_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "Allow HTTP"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    source      = "0.0.0.0/0"
    protocol    = "6"
    description = "Allow HTTPS"
    tcp_options {
      min = 443
      max = 443
    }
  }

  egress_security_rules {
    destination = "10.0.10.0/24"
    protocol    = "6"
    description = "Load balancer → worker nodes"
    tcp_options {
      min = 30809
      max = 32627
    }
  }

  lifecycle {
    ignore_changes = [
      ingress_security_rules,
      egress_security_rules,
      freeform_tags,
      defined_tags
    ]
  }
}
