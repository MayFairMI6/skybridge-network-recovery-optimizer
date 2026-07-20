output "application_url" {
  value = "http://localhost:${var.host_port}"
}

output "deployed_image" {
  value = var.image_name
}
