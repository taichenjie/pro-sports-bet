variable "region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-southeast-1"
}

variable "github_owner" {
  description = "GitHub username or organisation that owns the repo"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "pro-sports-bet"
}

variable "alert_email" {
  description = "Email for AWS budget alerts"
  type        = string
}

variable "monthly_budget_usd" {
  description = "Monthly AWS spend that triggers alerts"
  type        = string
  default     = "20"
}
