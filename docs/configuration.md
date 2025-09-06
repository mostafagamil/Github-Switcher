# Configuration Guide

GitHub Switcher stores its configuration in TOML format with automatic backups and safe defaults. This guide covers advanced configuration options and customization.

## Configuration Location

### Default Paths

- **Linux/macOS**: `~/.config/github-switcher/profiles.toml`
- **Windows**: `%APPDATA%\github-switcher\profiles.toml`

### Environment Override

You can override the configuration directory:

```bash
export GITHUB_SWITCHER_CONFIG_DIR="$HOME/my-configs/github-switcher"
ghsw list  # Uses the custom config directory
```

## Configuration File Structure

### Complete Example

```toml
[meta]
version = "1.0"
active_profile = "work"

[profiles.work]
name = "John Doe"
email = "john@company.com"
ssh_key_path = "~/.ssh/id_ed25519_work"
ssh_key_public = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... john@company.com"
created_at = "2024-01-15T10:30:00Z"
last_used = "2024-01-20T14:22:33Z"

[profiles.personal]
name = "John Doe"
email = "john.personal@gmail.com"
ssh_key_path = "~/.ssh/id_ed25519_personal"
ssh_key_public = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... john.personal@gmail.com"
created_at = "2024-01-10T09:15:00Z"
last_used = "2024-01-19T20:45:12Z"

[profiles.client-a]
name = "John Doe (Contractor)"
email = "contractor@client-a.com"
ssh_key_path = "~/.ssh/id_ed25519_client_a"
ssh_key_public = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... contractor@client-a.com"
created_at = "2024-01-12T16:00:00Z"
last_used = "2024-01-18T11:30:45Z"
```

## Configuration Sections

### Meta Section

Controls global GitHub Switcher behavior:

```toml
[meta]
version = "1.0"              # Configuration format version
active_profile = "work"      # Currently active profile name
```

**Fields:**
- `version`: Configuration format version (currently "1.0")
- `active_profile`: Name of the currently active profile (null if none)

### Profile Sections

Each profile is defined as `[profiles.<name>]`:

```toml
[profiles.my-profile]
name = "Full Name"                    # Git commit name
email = "email@example.com"           # Git commit email
ssh_key_path = "~/.ssh/id_ed25519_*"  # Private key path
ssh_key_public = "ssh-ed25519 ..."    # Public key content
created_at = "2024-01-15T10:30:00Z"   # ISO format creation timestamp
last_used = "2024-01-20T14:22:33Z"    # ISO format last usage (null if never used)
```

**Required Fields:**
- `name`: Full name for git commits
- `email`: Email address for git commits
- `ssh_key_path`: Path to private SSH key
- `ssh_key_public`: Public SSH key content

**Auto-Generated Fields:**
- `created_at`: Profile creation timestamp
- `last_used`: Last profile usage timestamp (updated on switch)

## Advanced Configuration

### Custom SSH Key Paths

You can manually edit SSH key paths for special setups:

```toml
[profiles.special]
name = "Special User"
email = "special@example.com"
ssh_key_path = "/custom/path/to/key"  # Custom path
ssh_key_public = "ssh-rsa ..."        # Different key type
```

### Multiple Email Domains

Organize profiles by email domains:

```toml
[profiles.work-main]
name = "John Doe"
email = "john.doe@company.com"

[profiles.work-staging]
name = "John Doe"
email = "john.doe+staging@company.com"

[profiles.work-testing]
name = "John Doe"
email = "john.doe+testing@company.com"
```

### Consultant/Contractor Setup

```toml
[profiles.client-a-main]
name = "John Doe (Client A)"
email = "jdoe@client-a.com"

[profiles.client-a-staging]
name = "John Doe (Client A)"
email = "jdoe+staging@client-a.com"

[profiles.client-b]
name = "J. Doe"
email = "john@client-b.org"
```

## Configuration Management

### Manual Editing

You can safely edit the configuration file manually:

```bash
# Edit configuration
vim ~/.config/github-switcher/profiles.toml

# Validate configuration
ghsw list  # Will show errors if configuration is invalid
```

### Backup and Restore

GitHub Switcher automatically creates backups:

```bash
# Automatic backup created before modifications
ls ~/.config/github-switcher/
# profiles.toml
# profiles.toml.backup

# Manual backup
cp ~/.config/github-switcher/profiles.toml ~/my-backup.toml

# Restore from backup
cp ~/my-backup.toml ~/.config/github-switcher/profiles.toml
```

### Configuration Validation

GitHub Switcher validates configuration on startup:

- TOML syntax validation
- Required field presence
- Email format validation
- SSH key path validation
- Timestamp format validation

Invalid configurations show helpful error messages:

```bash
ghsw list
Error: Invalid configuration
- Profile 'work': missing required field 'email'
- Profile 'personal': invalid email format 'not-an-email'
- Profile 'old': SSH key file not found at path '~/.ssh/missing_key'
```

## Migration and Portability

### Export for Backup

```bash
# Export current configuration
ghsw export --output backup-$(date +%Y%m%d).toml

# Export without private key paths (portable)
ghsw export --format json --output portable.json
```

### Import on New System

```bash
# Import full configuration
ghsw import backup-20240120.toml

# Import with SSH key path updates
ghsw import portable.json --format json
# Then manually update SSH key paths if needed
```

### Cross-Platform Considerations

When moving between platforms:

1. **Path Separators**: SSH key paths automatically converted
2. **Home Directory**: `~` expansion works on all platforms
3. **Permissions**: SSH keys get proper permissions (600/644)
4. **Configuration Directory**: Uses platform-appropriate locations

## Troubleshooting

### Configuration Not Found

```bash
# Check configuration location
echo $GITHUB_SWITCHER_CONFIG_DIR
# or default: ~/.config/github-switcher/

# Create configuration directory
mkdir -p ~/.config/github-switcher

# Initialize with first profile
ghsw create
```

### Corrupted Configuration

```bash
# Restore from automatic backup
cp ~/.config/github-switcher/profiles.toml.backup ~/.config/github-switcher/profiles.toml

# Or start fresh
rm ~/.config/github-switcher/profiles.toml
ghsw create  # Creates new configuration
```

### Profile Conflicts

If you manually edit and create conflicts:

```bash
# Check for issues
ghsw list

# Common fixes:
# 1. Ensure profile names are unique
# 2. Check active_profile refers to existing profile
# 3. Validate email formats
# 4. Ensure SSH key paths exist
```

### Permission Issues

```bash
# Fix configuration directory permissions
chmod 755 ~/.config/github-switcher/
chmod 644 ~/.config/github-switcher/profiles.toml

# Fix SSH key permissions
chmod 600 ~/.ssh/id_ed25519_*
chmod 644 ~/.ssh/id_ed25519_*.pub
```

## Security Considerations

### Sensitive Information

The configuration file contains:
- ✅ **Email addresses** (not sensitive)
- ✅ **SSH public keys** (safe to share)
- ✅ **Profile metadata** (safe)
- ❌ **No private keys** (stored separately)
- ❌ **No passwords** (not used)

### File Permissions

- Configuration file: `644` (readable by owner and group)
- Configuration directory: `755` (accessible by owner and group)
- SSH private keys: `600` (owner read/write only)
- SSH public keys: `644` (readable by all)

### Backup Safety

Configuration backups are safe to store and share as they contain no private keys.

## Best Practices

1. **Regular Backups**: Export configuration monthly
2. **Descriptive Names**: Use clear profile names like "work-main", "client-a"
3. **Email Organization**: Use consistent email patterns
4. **Manual Edits**: Always test with `ghsw list` after manual changes
5. **Version Control**: Consider versioning your exported configurations
6. **Documentation**: Comment complex setups in separate documentation

## Integration with CI/CD

For automated environments:

```bash
# Set custom config location
export GITHUB_SWITCHER_CONFIG_DIR="/app/config"

# Pre-populate configuration
cat > $GITHUB_SWITCHER_CONFIG_DIR/profiles.toml << EOF
[meta]
version = "1.0"
active_profile = "ci"

[profiles.ci]
name = "CI Bot"
email = "ci@company.com"
ssh_key_path = "/app/keys/ci_key"
ssh_key_public = "${CI_SSH_PUBLIC_KEY}"
created_at = "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF

# Use in CI pipeline
ghsw switch ci
git clone git@github-ci:company/repo.git
```

This configuration guide covers all aspects of GitHub Switcher configuration management, from basic usage to advanced enterprise scenarios.