locals {
  vsts_configuration = {
      account_name = "josemartinez0973"
      branch_name = "tfg/master"
      project_name = "tfg-traffic-analysis"
      repository_name = "tfg-traffic-analysis"
      root_folder = "adf"
  }
}

output "adf_vsts" {
  value = local.vsts_configuration
}
