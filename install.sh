#!/bin/bash
echo "enter hostname:"
read hostname

echo "Enter admin username:"
read user

echo "Enter admin password"
read -sp password

echo "Enter admin password again"
read -sp password2

[[ "$password" == "$password2" ]] || ( echo "Passwords did not match"; exit 1; )

timedatectl set-ntp true

parted --script "/dev/sda" -- mklabel gpt \
  mkpart ESP fat32 1Mib 512MiB \
  set 1 boot on \
  mkpart primary btrfs 512 100%

part_boot="$(ls ${device}* | grep -E "^${device}p?1$")"
part_root="$(ls ${device}* | grep -E "^${device}p?3$")"

mkfs.vfat -F32 "${part_boot}"
mkfs.btrfs -L system "${part_root}"
mount "${part_root}" /mnt
mkdir /mnt/boot
mount "${part_boot}" /mnt/boot

pacstrap /mnt base linux linux-firmware vim xf86-video-intel xorg-server plasma plasma-wayland-session firefox vlc git base-devel grub bootmgr
genfstab -U /mnt >> /mnt/etc/fstab
echo "${hostname}" > /mnt/etc/hostname


arch-chroot /mnt timedatectl set-timezone Asia/Jerusalem
arch-chroot /mnt hwclock --systohc
echo "en_IL UTF-8" >> /mnt/etc/locale.gen

arch-chroot /mnt locale-gen
echo Lang=en_IL.UTF-8 >> /mnt/etc/locale.conf

arch-chroot /mnt mkinitcpio -P
arch-chroot /mnt useradd -m "$user"
echo "$user:$password" | chpasswd --root /mnt
echo "root:$password" | chpasswd --root /mnt
echo "lotem ALL=(ALL) ALL" >> /mnt/etc/sudoers.d/lotem
