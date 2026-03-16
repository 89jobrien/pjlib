# Linux Kernel Features for Minibox

Detailed documentation of Linux kernel features required by minibox.

## Minimum Requirements

- **Linux Kernel:** 5.0 or higher
- **Architecture:** x86_64, aarch64
- **Cgroups:** v2 unified hierarchy
- **Namespaces:** PID, mount, network, IPC, UTS
- **Filesystem:** overlayfs support

## Cgroups v2 (Control Groups)

### Overview

Cgroups v2 provides resource management and accounting for minibox containers. The unified hierarchy simplifies cgroup management compared to v1.

### Required Configuration

**Kernel config options:**
```
CONFIG_CGROUPS=y
CONFIG_CGROUP_SCHED=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CGROUP_PIDS=y
CONFIG_CGROUP_DEVICE=y
CONFIG_CPUSETS=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_MEMCG=y
CONFIG_MEMCG_SWAP=y
```

**Enable unified hierarchy:**
```bash
# Check current mode
mount | grep cgroup

# If using hybrid or legacy mode, enable v2:
# Add to kernel boot parameters in /etc/default/grub:
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"

# Alternative:
GRUB_CMDLINE_LINUX="cgroup_no_v1=all"

# Update grub and reboot:
sudo update-grub
sudo reboot
```

**Verify cgroups v2:**
```bash
# Should show cgroup2fs
stat -fc %T /sys/fs/cgroup/

# Should show available controllers
cat /sys/fs/cgroup/cgroup.controllers
# Expected output: cpuset cpu io memory hugetlb pids rdma
```

### Controllers Used by Minibox

**Memory controller:**
- `memory.max` - Hard limit on memory+swap usage
- `memory.current` - Current memory usage
- `memory.events` - OOM events and statistics

**CPU controller:**
- `cpu.weight` - Relative CPU time (default: 100, range: 1-10000)
- `cpu.max` - CPU bandwidth limit (not currently used by minibox)

## Namespaces

### Overview

Namespaces provide process isolation. Each namespace type isolates a different aspect of the system.

### Required Kernel Config

```
CONFIG_NAMESPACES=y
CONFIG_UTS_NS=y
CONFIG_IPC_NS=y
CONFIG_USER_NS=y
CONFIG_PID_NS=y
CONFIG_NET_NS=y
CONFIG_CGROUP_NS=y
```

### Namespace Types Used

**PID namespace (CLONE_NEWPID):**
- Isolates process ID space
- Container sees own init process as PID 1
- Cannot see host processes

```c
// Clone flag used by minibox
CLONE_NEWPID
```

**Mount namespace (CLONE_NEWNS):**
- Isolates filesystem mount points
- Container has own root filesystem via pivot_root
- Changes don't affect host

```c
CLONE_NEWNS
```

**Network namespace (CLONE_NEWNET):**
- Isolates network stack
- Container has own interfaces, routing table, firewall rules
- Currently minibox doesn't configure networking (no internet)

```c
CLONE_NEWNET
```

**IPC namespace (CLONE_NEWIPC):**
- Isolates System V IPC, POSIX message queues
- Prevents inter-process communication with host

```c
CLONE_NEWIPC
```

**UTS namespace (CLONE_NEWUTS):**
- Isolates hostname and domain name
- Container can set own hostname

```c
CLONE_NEWUTS
```

**User namespace (CLONE_NEWUSER):**
- Not currently used by minibox
- Future: enable rootless containers

### Verification

```bash
# Check namespace support
ls -la /proc/self/ns/
# Should show: cgroup ipc mnt net pid pid_for_children user uts

# Check specific namespace for a process
sudo ls -la /proc/<pid>/ns/
```

## Overlay Filesystem

### Overview

Overlayfs provides copy-on-write filesystem for containers. Multiple read-only layers (image) + writable layer (container changes) = merged view.

### Required Kernel Config

```
CONFIG_OVERLAY_FS=y
```

### Verification

```bash
# Check support
grep overlay /proc/filesystems
# Should show: nodev overlay

# Load module if needed
sudo modprobe overlay

# Auto-load on boot
echo overlay | sudo tee /etc/modules-load.d/overlay.conf
```

### Directory Structure

Minibox uses overlayfs with:
- **lowerdir** - Read-only image layers (colon-separated)
- **upperdir** - Container modifications (writable)
- **workdir** - Overlay working directory (must be empty)
- **merged** - Combined view (container sees this as /)

**Example mount:**
```bash
mount -t overlay overlay \
  -o lowerdir=/lower1:/lower2,upperdir=/upper,workdir=/work \
  /merged
```

### Limitations

- upperdir and workdir must be on same filesystem
- Cannot nest overlay filesystems (no overlay-over-overlay)
- workdir must be empty directory on same fs as upperdir

## Capabilities

### Required Capabilities

Minibox daemon requires these Linux capabilities:

- **CAP_SYS_ADMIN** - Create namespaces, mount filesystems, pivot_root
- **CAP_SYS_CHROOT** - chroot system call
- **CAP_SYS_RESOURCE** - Set resource limits
- **CAP_SETUID/CAP_SETGID** - Change user/group ID
- **CAP_NET_ADMIN** - Configure network namespaces

**Current approach:** Run entire daemon as root

**Future improvement:** Drop privileges after initial setup

### Verification

```bash
# Check current capabilities
sudo capsh --print

# Run daemon with specific capabilities (future)
# sudo setcap cap_sys_admin,cap_sys_chroot+eip ./miniboxd
```

## Security Features

### Seccomp (Secure Computing Mode)

**Not currently implemented**

Future enhancement to restrict syscalls available to containers.

**Kernel config:**
```
CONFIG_SECCOMP=y
CONFIG_SECCOMP_FILTER=y
```

### AppArmor / SELinux

**Not currently implemented**

Future enhancement for mandatory access control.

**Kernel config:**
```
# AppArmor
CONFIG_SECURITY_APPARMOR=y

# SELinux
CONFIG_SECURITY_SELINUX=y
```

## Kernel Parameters

### Recommended Settings

**Enable cgroups v2:**
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"
```

**Enable user namespaces (for rootless in future):**
```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1

# Persist across reboots
echo "kernel.unprivileged_userns_clone=1" | sudo tee /etc/sysctl.d/99-userns.conf
```

**Increase PID limit (for many containers):**
```bash
sudo sysctl -w kernel.pid_max=4194304

# Persist
echo "kernel.pid_max=4194304" | sudo tee /etc/sysctl.d/99-pid.conf
```

## Distribution-Specific Notes

### Ubuntu 20.04+

- Cgroups v2 enabled by default on 21.10+
- Enable on 20.04: add boot parameter
- overlay module included in kernel

### Debian 11+

- Cgroups v2 enabled by default
- overlay module included

### Fedora 31+

- Cgroups v2 enabled by default
- Full namespace support

### Arch Linux

- Latest kernel with all features
- Cgroups v2 enabled
- May need to load overlay module manually

## Troubleshooting

### Cgroups v2 Not Available

**Symptoms:**
- `/sys/fs/cgroup` is not cgroup2fs
- `mount | grep cgroup` shows v1 hierarchy

**Solutions:**
1. Add `systemd.unified_cgroup_hierarchy=1` to boot parameters
2. Or add `cgroup_no_v1=all`
3. Update grub: `sudo update-grub`
4. Reboot

### Namespace Creation Fails

**Symptoms:**
- `clone()` returns EINVAL or EPERM

**Solutions:**
1. Verify running as root
2. Check `ls -la /proc/self/ns/`
3. Enable user namespaces: `sysctl kernel.unprivileged_userns_clone=1`

### Overlay Mount Fails

**Symptoms:**
- Mount fails with "wrong fs type"

**Solutions:**
1. Load module: `sudo modprobe overlay`
2. Verify: `grep overlay /proc/filesystems`
3. Auto-load: `echo overlay > /etc/modules-load.d/overlay.conf`

## References

- [Cgroups v2 Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Overlayfs Documentation](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
