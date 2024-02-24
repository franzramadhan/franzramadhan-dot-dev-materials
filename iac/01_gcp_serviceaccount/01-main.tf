resource "google_service_account" "this" {
  account_id   = var.sa_account_id
  display_name = var.sa_account_id
  description  = "Service Account for OIDC Federation between AWS and GCP"
}

resource "google_service_account_iam_member" "this_sa_token_creator" {
  for_each           = toset(var.sa_token_creators)
  service_account_id = google_service_account.this.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = each.value
}

resource "google_project_iam_member" "viewer" {
  project = var.project_id
  role    = "roles/viewer"
  member  = google_service_account.this.member
}
