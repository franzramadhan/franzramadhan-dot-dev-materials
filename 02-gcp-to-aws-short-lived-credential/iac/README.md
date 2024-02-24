# IaC

- Check each directories. Either create  `terraform.tfvars` file or you can specify the variable input later.
- Initialize the infrastructure following the folder sequence
  - `cd 01_gcp_serviceaccount && terraform init && terraform apply`
  - `cd 02_aws_iam_role && terraform init && terraform apply`
  - `cd 03_gcp_workloadidentity && terraform init && terraform apply`