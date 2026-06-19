provider "aws" {
  region = "us-east-1"

  # default_tags: tags de governanca aplicadas a todos os recursos do provider.
  default_tags {
    tags = {
      Project   = "vortex-mobility"
      ManagedBy = "terraform"
      Lab       = "01-terraform"
    }
  }
}

module "servidor" {
  source  = "./modules/file"
  project = "vortex"
}
