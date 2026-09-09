variable "name" {
  description = "Name of the firewall"
  type        = string
}

variable "rules" {
  description = "List of firewall rules"
  type = list(object({
    direction  = string
    protocol   = string
    port       = string
    source_ips = list(string)
  }))
}

variable "firewall_attachment_label" {
  description = "Label to identify the firewall attachment"
  type        = string
}
