# -*- mode: ruby -*-
# vi: set ft=ruby :

$pre_provision = <<SCRIPT
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
SCRIPT

Vagrant.configure("2") do |config|
    config.vm.box = "debian/contrib-stretch64"

    config.vm.network "forwarded_port", guest: 9000, host: 9000
    config.vm.network "forwarded_port", guest: 80, host: 8000

    config.vm.provision "shell", inline: $pre_provision
    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "provisioning/playbook.yml"
    end
end
