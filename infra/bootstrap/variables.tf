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

variable "github_owner_id" {
  description = "Numeric ID of the GitHub owner (gh api users/<owner> --jq .id)"
  type        = number
}

variable "github_repo_id" {
  description = "Numeric ID of the GitHub repo (gh api repos/<owner>/<repo> --jq .id)"
  type        = number
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
