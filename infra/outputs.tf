output "instance_ip" {
  value = aws_spot_instance_request.k3s.public_ip
}

output "ssh_command" {
  value = "ssh -i ../vibe-search-key.pem ubuntu@${aws_spot_instance_request.k3s.public_ip}"
}

output "argocd_url" {
  value = "https://${aws_spot_instance_request.k3s.public_ip}:30443"
}

output "app_url" {
  value = "http://${aws_spot_instance_request.k3s.public_ip}:30080"
}