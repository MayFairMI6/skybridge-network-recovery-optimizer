variable "image_name" {
  description = "Locally built Docker image tag produced by Jenkins."
  type        = string
}

variable "container_name" {
  description = "Stable name for the deployed application container."
  type        = string
  default     = "local-pipeline-app"
}

variable "host_port" {
  description = "Host port exposed by the application."
  type        = number
  default     = 8081
}
