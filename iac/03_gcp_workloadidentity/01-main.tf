data "terraform_remote_state" "gcp_service_account" {
  backend = "local"

  config = {
    path = "../01_gcp_serviceaccount/terraform.tfstate"
  }
}

data "terraform_remote_state" "aws_iam_role" {
  backend = "local"

  config = {
    path = "../02_aws_iam_role/terraform.tfstate"
  }
}

resource "google_iam_workload_identity_pool" "this" {
  workload_identity_pool_id = var.workload_identity_pool_id
  display_name              = var.workload_identity_pool_id
  description               = "Workload Identity Pool for OIDC authentication from AWS IAM Role."
}

resource "google_iam_workload_identity_pool_provider" "this" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.this.workload_identity_pool_id
  workload_identity_pool_provider_id = var.workload_identity_pool_provider_id
  display_name                       = var.workload_identity_pool_provider_id
  attribute_condition                = "attribute.aws_role==\"${split("/",split(":", data.terraform_remote_state.aws_iam_role.outputs.aws_iam_role_arn)[5])[1]}\""
  attribute_mapping = {
    "google.subject"             = "assertion.arn"
    "attribute.account"          = "assertion.account"
    "attribute.aws_role"         = "assertion.arn.extract('assumed-role/{role}/')"
    "attribute.aws_ec2_instance" = "assertion.arn.extract('assumed-role/{role_and_session}').extract('/{session}')"
  }
  aws {
    account_id = split(":", data.terraform_remote_state.aws_iam_role.outputs.aws_iam_role_arn)[4]
  }
}

resource "google_service_account_iam_member" "this" {
  service_account_id = data.terraform_remote_state.gcp_service_account.outputs.service_account_id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${data.terraform_remote_state.gcp_service_account.outputs.gcp_project_number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.this.workload_identity_pool_id}/attribute.aws_role/${split("/",split(":", data.terraform_remote_state.aws_iam_role.outputs.aws_iam_role_arn)[5])[1]}"
}
