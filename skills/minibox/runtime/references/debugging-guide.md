# Minibox Container Debugging Guide

Comprehensive guide for debugging container runtime issues in minibox.

## Quick Diagnosis

### Container Won't Start

**Symptoms:** `minibox-cli run` fails or returns immediately

**Diagnosis steps:**

1. **Check daemon is running:**
   ```bash
   ps aux | grep miniboxd
   ```

2. **Check daemon logs:**
   ```bash
   sudo RUST_LOG=debug ./target/debug/miniboxd
   ```

3. **Verify image was pulled:**
   ```bash
   ls -la /var/lib/minibox/images/
   ```

4. **Check permissions:**
   ```bash
   # Must run as root
   whoami  # Should be 'root'
   ```

**Common causes:**
- Daemon not running
- Not running as root
- Image pull failed
- Kernel features missing

### Container Exits Immediately

**Symptoms:** Container starts but exits right away

**Diagnosis:**

1. **Check container process:**
   ```bash
   # Get container ID from minibox-cli ps
   sudo cat /var/lib/minibox/containers/<id>/pid
   ps -p <pid>  # Check if process exists
   ```

2. **Check daemon logs for errors:**
   ```bash
   # Look for execvp failures, namespace errors
   ```

3. **Verify command exists in image:**
   ```bash
   # Check overlay merged directory
   sudo ls -la /var/lib/minibox/containers/<id>/overlay/merged/bin/
   ```

**Common causes:**
- Command doesn't exist in image (e.g., `/bin/bash` not in alpine)
- Command exits immediately (e.g., `echo hello` completes instantly)
- Namespace setup failed
- Pivot root failed

### Resource Limit Issues

**Symptoms:** Container OOM killed or CPU throttled

**Diagnosis:**

1. **Check memory limit:**
   ```bash
   sudo cat /sys/fs/cgroup/minibox/<id>/memory.max
   sudo cat /sys/fs/cgroup/minibox/<id>/memory.current
   ```

2. **Check OOM events:**
   ```bash
   sudo cat /sys/fs/cgroup/minibox/<id>/memory.events | grep oom
   ```

3. **Check CPU weight:**
   ```bash
   sudo cat /sys/fs/cgroup/minibox/<id>/cpu.weight
   ```

**Solutions:**
- Increase memory limit: `--memory 1024`
- Increase CPU weight: `--cpu-weight 200`

## Namespace Debugging

### Verify Namespace Isolation

**Check PID namespace:**
```bash
# Inside container
ps aux  # Should only see container processes

# Outside container
sudo ls -la /proc/<container-pid>/ns/pid
```

**Check mount namespace:**
```bash
# Inside container
mount | grep overlay

# Outside container
sudo cat /proc/<container-pid>/mountinfo
```

**Check UTS namespace (hostname):**
```bash
# Inside container
hostname

# Outside container
hostname  # Should be different
```

**Check network namespace:**
```bash
# Inside container
ip addr  # Should show isolated network

# Outside container
sudo ip netns identify <container-pid>
```

### Namespace Creation Failures

**Error:** `clone() failed: EINVAL`

**Causes:**
- Kernel doesn't support requested namespace
- Missing CAP_SYS_ADMIN capability
- User namespaces not enabled

**Solutions:**
```bash
# Check namespace support
ls -la /proc/self/ns/

# Enable user namespaces (if disabled)
sudo sysctl -w kernel.unprivileged_userns_clone=1

# Verify running as root
sudo minibox-cli run ...
```

## Cgroup Debugging

### Cgroup v2 Not Available

**Check if cgroups v2 is enabled:**
```bash
mount | grep cgroup2
stat -fc %T /sys/fs/cgroup/
```

**If using cgroups v1:**
```bash
# Add to kernel boot parameters
sudo vim /etc/default/grub
# Add: systemd.unified_cgroup_hierarchy=1

sudo update-grub
sudo reboot
```

### Cgroup Creation Fails

**Error:** `mkdir: cannot create directory: Permission denied`

**Solutions:**
```bash
# Must run as root
sudo miniboxd

# Check cgroup filesystem is writable
touch /sys/fs/cgroup/test
rm /sys/fs/cgroup/test
```

### Cgroup Removal Fails

**Error:** `Device or resource busy`

**Cause:** Processes still in cgroup

**Solution:**
```bash
# Find processes
sudo cat /sys/fs/cgroup/minibox/<id>/cgroup.procs

# Kill processes
sudo kill -9 <pid>

# Then remove
sudo rmdir /sys/fs/cgroup/minibox/<id>
```

## Overlay Filesystem Debugging

### Mount Failures

**Error:** `mount: wrong fs type, bad option, bad superblock`

**Diagnosis:**
```bash
# Check kernel support
grep overlay /proc/filesystems

# Load module if missing
sudo modprobe overlay

# Verify mount options
mount | grep overlay
```

### Work Directory Errors

**Error:** `workdir and upperdir must be separate`

**Solution:** Ensure work, upper, and merged are separate directories:
```bash
sudo ls -la /var/lib/minibox/containers/<id>/overlay/
# Should show: lower/ upper/ work/ merged/
```

### Unmount Issues

**Error:** `target is busy`

**Cause:** Processes have files open

**Solution:**
```bash
# Find processes using mount
sudo lsof +D /var/lib/minibox/containers/<id>/overlay/merged/

# Kill processes
sudo fuser -k /var/lib/minibox/containers/<id>/overlay/merged/

# Force unmount
sudo umount -l /var/lib/minibox/containers/<id>/overlay/merged/
```

## Process Debugging

### execvp() Failures

**Error in logs:** `execvp failed: ENOENT`

**Causes:**
- Command doesn't exist in container
- Incorrect PATH
- Missing shared libraries

**Diagnosis:**
```bash
# Check if command exists
sudo chroot /var/lib/minibox/containers/<id>/overlay/merged/ which bash

# Check shared libraries
sudo chroot /var/lib/minibox/containers/<id>/overlay/merged/ ldd /bin/bash
```

### File Descriptor Leaks

**Symptom:** Container inherits daemon's file descriptors

**Check:**
```bash
# Inside container
ls -la /proc/self/fd/
# Should only show 0, 1, 2 (stdin, stdout, stderr)
```

**Solution:** The `close_leaked_fds()` function should handle this. If not working:
```rust
// In container/process.rs, verify fd closing logic
for fd in 3..max_fd {
    unsafe { libc::close(fd) };
}
```

## Image Debugging

### Pull Failures

**Error:** `failed to pull image`

**Diagnosis:**
```bash
# Check network connectivity
curl https://registry-1.docker.io/v2/

# Check image name format
# Must be: <image>:<tag> or <image> (defaults to :latest)

# Enable debug logging
RUST_LOG=minibox::image=trace sudo miniboxd
```

### Layer Extraction Failures

**Error:** `failed to extract layer`

**Diagnosis:**
```bash
# Check downloaded layers
ls -la /var/lib/minibox/images/<image-name>/

# Verify tar.gz format
file /var/lib/minibox/images/<image-name>/*.tar.gz

# Test extraction manually
tar -tzf /var/lib/minibox/images/<image-name>/layer.tar.gz | head
```

## Daemon Debugging

### Socket Errors

**Error:** `No such file or directory: /var/run/minibox.sock`

**Cause:** Daemon not running

**Solution:**
```bash
# Start daemon
sudo ./target/debug/miniboxd

# Verify socket created
ls -la /var/run/minibox.sock
```

### Request Timeout

**Symptom:** CLI hangs waiting for response

**Diagnosis:**
```bash
# Check daemon logs
RUST_LOG=debug sudo ./target/debug/miniboxd

# Check if daemon is stuck
sudo strace -p <miniboxd-pid>

# Check socket permissions
ls -la /var/run/minibox.sock
```

### State Corruption

**Symptom:** Daemon has inconsistent container state

**Solutions:**
```bash
# Clean up stale containers
sudo rm -rf /var/lib/minibox/containers/*

# Clean up stale cgroups
sudo find /sys/fs/cgroup/minibox/ -type d -delete 2>/dev/null

# Restart daemon
sudo pkill miniboxd
sudo ./target/debug/miniboxd
```

## Advanced Debugging

### Syscall Tracing

**Trace namespace creation:**
```bash
sudo strace -f -e clone,unshare ./target/debug/miniboxd
```

**Trace filesystem operations:**
```bash
sudo strace -f -e mount,pivot_root,chroot ./target/debug/miniboxd
```

**Trace cgroup operations:**
```bash
sudo strace -f -e open,write ./target/debug/miniboxd | grep cgroup
```

### Kernel Logs

**Check kernel messages:**
```bash
sudo dmesg | grep -i 'minibox\|overlay\|cgroup'

# Watch in real-time
sudo dmesg -w
```

### Performance Profiling

**CPU profiling:**
```bash
cargo install flamegraph
sudo cargo flamegraph --bin miniboxd
```

**Memory profiling:**
```bash
valgrind --leak-check=full ./target/debug/miniboxd
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `EINVAL: Invalid argument` | Invalid namespace flags or cgroup parameter | Check kernel support |
| `EPERM: Operation not permitted` | Not running as root | Use `sudo` |
| `EBUSY: Device or resource busy` | Cgroup has processes or mount is busy | Kill processes, force unmount |
| `ENOENT: No such file or directory` | Missing command, file, or directory | Verify paths and image contents |
| `EEXIST: File exists` | Trying to create existing cgroup or mount | Check for leftover state |

## Debugging Checklist

Before reporting issues:

- [ ] Running on Linux (not macOS/Windows)
- [ ] Running as root (`sudo`)
- [ ] Daemon is running (`ps aux | grep miniboxd`)
- [ ] Cgroups v2 enabled (`mount | grep cgroup2`)
- [ ] Overlay supported (`grep overlay /proc/filesystems`)
- [ ] Checked daemon logs (`RUST_LOG=debug`)
- [ ] Verified image exists (`ls /var/lib/minibox/images/`)
- [ ] Checked container state (`ls /var/lib/minibox/containers/`)
- [ ] Reviewed kernel logs (`dmesg`)
