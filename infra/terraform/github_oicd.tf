
# Create the Microsoft Entra ID (Azure AD) Application
resource "azuread_application" "github_actions" {
  display_name = "${var.prefix}-app-github-actions"
}

# Create the associated Service Principal in your tenant
resource "azuread_service_principal" "github_actions" {
  client_id                    = azuread_application.github_actions.client_id
  app_role_assignment_required = false # Set to false to allow the Service Principal to be assigned roles without requiring app role assignments
}

# Federated Credential for commits pushed/merged to the main branch
resource "azuread_application_federated_identity_credential" "github_actions_main" {
  application_id = azuread_application.github_actions.id
  display_name   = "${var.prefix}-gh-actions-main"
  description    = "OIDC trust for GitHub Actions on main branch"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_organization}/${var.github_repository}:ref:refs/heads/main"
}

# (Optional) Federated Credential for Pull Requests
resource "azuread_application_federated_identity_credential" "github_actions_pr" {
  application_id = azuread_application.github_actions.id
  display_name   = "${var.prefix}-gh-actions-pr"
  description    = "OIDC trust for GitHub Actions pull requests"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_organization}/${var.github_repository}:pull_request"
}

# Assign Contributor role to the Service Principal scoped to your Resource Group
resource "azurerm_role_assignment" "github_actions_contributor" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.github_actions.object_id
}


data "azurerm_client_config" "current" {} # for getting tenant_id and subscription_id for GitHub secrets in outputs.tf