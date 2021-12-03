// output "instance_ip_addr" {
//   value = aws_instance.app_server.public_ip
// }
output "static_files" {
  value = module.template_files.files
}