terraform {
  backend "http" {
    address = "http://127.0.0.1:8080/storage/test"
    lock_address = "http://127.0.0.1:8080/storage/test/lock"
    unlock_address = "http://127.0.0.1:8080/storage/test/lock"
  }
}

provider "random" {
  
}

resource "random_password" "password" {
  length           = 16
  special = false
}