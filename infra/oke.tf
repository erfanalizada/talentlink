locals {
  api_subnet_id  = "ocid1.subnet.oc1.eu-amsterdam-1.aaaaaaaalar2izgxfvxzwp5avpysm7gs6jlh6hd76mtsuvrldrupxihkzuya"
  node_subnet_id = "ocid1.subnet.oc1.eu-amsterdam-1.aaaaaaaa3eclfjq2ignmfqkmiailfrz4inuuzpgnjrroqaa5zuutsahdeujq"
  lb_subnet_id   = "ocid1.subnet.oc1.eu-amsterdam-1.aaaaaaaanlhpdk74ziz5cxbeblofhcmtrgjlzhcgwwlt3xh7j2eclg7omela"
}

# -------------------------------------------------------------------
# EXISTING OKE CLUSTER (imported / managed safely)
# -------------------------------------------------------------------
resource "oci_containerengine_cluster" "talentlink_cluster" {
  compartment_id     = var.compartment_ocid
  name               = "talentlink-cluster"
  kubernetes_version = "v1.33.1"
  vcn_id             = var.vcn_id

  endpoint_config {
    is_public_ip_enabled = true
    subnet_id            = local.api_subnet_id
  }

  options {
    service_lb_subnet_ids = [local.lb_subnet_id]

    kubernetes_network_config {
      pods_cidr     = "10.244.0.0/16"
      services_cidr = "10.96.0.0/16"
    }
  }

  freeform_tags = {
    Environment = "dev"
    ManagedBy   = "Terraform"
  }

  # Prevent Terraform from touching OCI-managed properties
  lifecycle {
    ignore_changes = [
      freeform_tags,
      defined_tags,
      options,
      endpoint_config,
      kubernetes_version
    ]
  }
}

# -------------------------------------------------------------------
# EXISTING NODE POOL (imported / managed safely)
# -------------------------------------------------------------------
resource "oci_containerengine_node_pool" "talentlink_node_pool" {
  compartment_id     = var.compartment_ocid
  cluster_id         = oci_containerengine_cluster.talentlink_cluster.id
  name               = "talentlink-node-pool"
  kubernetes_version = "v1.33.1"
  node_shape         = "VM.Standard.A1.Flex"

  node_shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  node_config_details {
    size = 1

    placement_configs {
      availability_domain = "xjKl:eu-amsterdam-1-AD-1"
      subnet_id           = local.node_subnet_id
    }
  }

  freeform_tags = {
    Environment = "dev"
    ManagedBy   = "Terraform"
  }

  # Prevent Terraform from modifying OCI-managed attributes
  lifecycle {
    ignore_changes = [
      freeform_tags,
      defined_tags,
      kubernetes_version,
      node_config_details,
      node_shape_config
    ]
  }
}
