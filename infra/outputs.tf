# ===============================
# Network Outputs
# ===============================

output "vcn_id" {
  value       = var.vcn_id
  description = "VCN ID of the existing Virtual Cloud Network"
}

output "subnet_api_id" {
  value       = local.api_subnet_id
  description = "Subnet ID for the Kubernetes API endpoint"
}

output "subnet_nodes_id" {
  value       = local.node_subnet_id
  description = "Subnet ID for OKE worker nodes"
}

output "subnet_lb_id" {
  value       = local.lb_subnet_id
  description = "Subnet ID for OKE service load balancers"
}

output "internet_gateway_id" {
  value       = var.internet_gateway_id
  description = "Internet Gateway OCID"
}

output "nat_gateway_id" {
  value       = var.nat_gateway_id
  description = "NAT Gateway OCID"
}

# ===============================
# Route Tables
# ===============================
output "route_table_api_id" {
  value       = try(oci_core_route_table.rt_api.id, null)
  description = "Route Table ID for API subnet"
}

output "route_table_nodes_id" {
  value       = try(oci_core_route_table.rt_nodes.id, null)
  description = "Route Table ID for worker node subnet"
}

output "route_table_nodes_nat_id" {
  value       = try(oci_core_route_table.rt_nodes_nat.id, null)
  description = "Route Table ID for NAT subnet"
}

output "route_table_public_id" {
  value       = try(oci_core_route_table.rt_public.id, null)
  description = "Route Table ID for public subnet"
}

# ===============================
# Security Lists
# ===============================
output "sl_api_id" {
  value       = try(oci_core_security_list.sl_api.id, null)
  description = "Security list for API subnet"
}

output "sl_nodes_id" {
  value       = try(oci_core_security_list.sl_nodes.id, null)
  description = "Security list for worker node subnet"
}

output "sl_lb_id" {
  value       = try(oci_core_security_list.sl_lb.id, null)
  description = "Security list for load balancer subnet"
}

# ===============================
# OKE Cluster + Node Pool
# ===============================
output "cluster_id" {
  value       = try(oci_containerengine_cluster.talentlink_cluster.id, var.cluster_id_existing)
  description = "OKE Cluster ID (existing or managed by Terraform)"
}

output "node_pool_id" {
  value       = try(oci_containerengine_node_pool.talentlink_node_pool.id, var.nodepool_id_existing)
  description = "OKE Node Pool ID (existing or managed by Terraform)"
}
