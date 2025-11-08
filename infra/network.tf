# ===============================
# Route Table: API
# ===============================
resource "oci_core_route_table" "rt_api" {
  display_name   = var.rt_api_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.internet_gateway_id
    description       = "Public internet access for API endpoint"
  }

  lifecycle {
    ignore_changes = [
      route_rules,
      freeform_tags,
      defined_tags
    ]
  }
}

# ===============================
# Route Table: Nodes
# ===============================
resource "oci_core_route_table" "rt_nodes" {
  display_name   = var.rt_nodes_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.nat_gateway_id
    description       = "Node outbound via NAT"
  }

  lifecycle {
    ignore_changes = [
      route_rules,
      freeform_tags,
      defined_tags
    ]
  }
}

# ===============================
# Route Table: Nodes NAT
# ===============================
resource "oci_core_route_table" "rt_nodes_nat" {
  display_name   = var.rt_nodes_nat_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.nat_gateway_id
    description       = "Outbound NAT route"
  }

  lifecycle {
    ignore_changes = [
      route_rules,
      freeform_tags,
      defined_tags
    ]
  }
}

# ===============================
# Route Table: Public
# ===============================
resource "oci_core_route_table" "rt_public" {
  display_name   = var.rt_public_name
  compartment_id = var.compartment_ocid
  vcn_id         = var.vcn_id

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = var.internet_gateway_id
    description       = "Public traffic to/from internet"
  }

  lifecycle {
    ignore_changes = [
      route_rules,
      freeform_tags,
      defined_tags
    ]
  }
}
