provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# The image is created by Jenkins immediately before this apply. Referencing it
# directly lets Terraform manage only the running deployment container.
resource "docker_container" "app" {
  name  = var.container_name
  image = var.image_name

  ports {
    internal = 3000
    external = var.host_port
  }

  restart = "unless-stopped"
}
