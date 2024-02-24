output "gcp_project_id" {
    value = data.google_project.this.id
}

output "gcp_project_number" {
    value = data.google_project.this.number
}

output "service_account_email" {
    value = google_service_account.this.email
}

output "service_account_id" {
    value = google_service_account.this.id
}

output "service_account_unique_id" {
    value = google_service_account.this.unique_id
}
