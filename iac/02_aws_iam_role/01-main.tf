data "terraform_remote_state" "gcp_service_account" {
  backend = "local"

  config = {
    path = "../01_gcp_serviceaccount/terraform.tfstate"
  }
}

resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
            Effect =  "Allow"
            Principal = {
                Federated = "accounts.google.com"
            }
            Action = "sts:AssumeRoleWithWebIdentity"
            Condition = {
                StringEquals = {
                    "accounts.google.com:aud" = data.terraform_remote_state.gcp_service_account.outputs.service_account_unique_id
                }
            }
        }
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AdministratorAccess"
  ]
}