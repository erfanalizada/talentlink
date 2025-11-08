# ===============================================================
# Global OCI Configuration
# ===============================================================

variable "region" {
  type        = string
  description = "OCI region where resources are deployed"
  default     = "eu-amsterdam-1"
}

variable "tenancy_ocid" {
  type        = string
  description = "OCI tenancy OCID (root identifier for all resources)"
  default     = "ocid1.tenancy.oc1..aaaaaaaa3wrwlxbbluhqe7sywhjkx24jnpf5z22xh62q4bxjk3uaojihjula"
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID where OKE and related resources reside"
  default     = "ocid1.tenancy.oc1..aaaaaaaa3wrwlxbbluhqe7sywhjkx24jnpf5z22xh62q4bxjk3uaojihjula"
}

# ===============================================================
# Networking
# ===============================================================

variable "vcn_id" {
  type        = string
  description = "VCN ID for the existing network"
  default     = "ocid1.vcn.oc1.eu-amsterdam-1.amaaaaaaknk3zmiah4wit5lzm2q254bntzrgzdpijkqrj6mdqak5ov6jo5jq"
}

variable "internet_gateway_id" {
  type        = string
  description = "Existing Internet Gateway OCID"
  default     = "ocid1.internetgateway.oc1.eu-amsterdam-1.aaaaaaaadhx4r2zmtz4ed3f6bxgsuj3pnb5jrlixlgzhfvfwynulvtwdnncq"
}

variable "nat_gateway_id" {
  type        = string
  description = "Existing NAT Gateway OCID"
  default     = "ocid1.natgateway.oc1.eu-amsterdam-1.aaaaaaaaowp7zxqiddsom6xakyakwr54lud2x766qy3qpsbmk5l4hg7m5tsa"
}

# ===============================================================
# Route Table Names
# ===============================================================

variable "rt_api_name" {
  type        = string
  description = "Display name for the route table associated with API subnet"
  default     = "oke-api-rt"
}

variable "rt_nodes_name" {
  type        = string
  description = "Display name for the route table associated with worker nodes"
  default     = "oke-nodes-rt"
}

variable "rt_nodes_nat_name" {
  type        = string
  description = "Display name for the route table used by NAT subnet"
  default     = "oke-node-nat-routetable"
}

variable "rt_public_name" {
  type        = string
  description = "Display name for the route table used by public subnet"
  default     = "oke-public-routetable-talentlink-cluster-85f68c16d"
}

# ===============================================================
# Security List Names
# ===============================================================

variable "sl_api_name" {
  type        = string
  description = "Display name for security list associated with the Kubernetes API endpoint"
  default     = "oke-k8sApiEndpoint-quick-talentlink-cluster-85f68c16d"
}

variable "sl_nodes_name" {
  type        = string
  description = "Display name for security list associated with OKE worker nodes"
  default     = "oke-nodeseclist-quick-talentlink-cluster-85f68c16d"
}

variable "sl_lb_name" {
  type        = string
  description = "Display name for security list associated with load balancer subnet"
  default     = "oke-svclbseclist-quick-talentlink-cluster-85f68c16d"
}

# ===============================================================
# Existing OKE Resources
# ===============================================================

variable "cluster_id_existing" {
  type        = string
  description = "OCID of the existing OKE cluster (used for reference or import)"
  default     = "ocid1.cluster.oc1.eu-amsterdam-1.aaaaaaaay62d2h4r5scmwfg5cae3ts4xesddow3tfqkzvuqwfc5vboap7ima"
}

variable "nodepool_id_existing" {
  type        = string
  description = "OCID of the existing OKE node pool (used for reference or import)"
  default     = "ocid1.nodepool.oc1.eu-amsterdam-1.aaaaaaaap5meizwzxkwx5pqpzzeksdlpykp73zpuu3flfkrwdnk5qpnnehrq"
}
