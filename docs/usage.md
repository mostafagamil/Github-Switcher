# Usage Guide

GitHub Switcher helps you manage multiple GitHub identities effortlessly. This guide covers the essential features you'll use daily.

## Quick Start

After installation, create your first profile:

```bash
# Interactive profile creation (recommended)
ghsw create

# Verify profile was created
ghsw list

# Switch to the profile
ghsw switch your-profile-name
```

## Interactive Commands

**All GitHub Switcher commands support interactive mode when no arguments are provided.**

When you run a command without specifying a profile name, GitHub Switcher will:
- Show a numbered list of available profiles
- Let you select by number or name  
- Handle case-insensitive matching
- Provide clear status indicators

**Examples:**
```bash
ghsw switch    # Shows numbered list of profiles to switch to
ghsw delete    # Shows list of profiles to delete with confirmation
ghsw copy-key  # Shows list of profiles to copy SSH key from
ghsw test      # Shows list of profiles to test SSH connection
```

This makes GitHub Switcher easy to use even when you can't remember exact profile names!

## Core Commands

### Create Profile

**Interactive (Recommended):**
```bash
ghsw create
```

The interactive wizard:
1. **Advanced SSH Detection**: Scans for existing keys with fingerprinting and deduplication
2. **Security Analysis**: Detects passphrase-protected keys and ssh-agent status
3. **Intelligent Guidance**: Recommends import vs new key generation based on your setup
4. **Enhanced SSH Security**: Prompts "🔐 Protect SSH key with passphrase?" for enhanced security
5. **Seamless Integration**: Copies public key to clipboard for GitHub setup

**SSH Key Security Options:**
- **Standard SSH keys** (🔓 Unprotected): Quick access, no passphrase required
- **Passphrase-protected SSH keys** (🔐 Protected): Enhanced security with passphrase encryption

**Non-Interactive:**
```bash
ghsw create --name work --fullname "Your Name" --email work@company.com
```

### Switch Profiles

**Interactive:**
```bash
ghsw switch
# Shows numbered list of profiles
# 🔧 Select a profile to switch to:
#   1. work - work@company.com 🟢 Active
#   2. personal - personal@gmail.com ⚪ Inactive
# 🎯 Enter profile number or name: 2
```

**Direct (Case-Insensitive):**
```bash
ghsw switch work      # Switch to work profile
ghsw switch PERSONAL  # Case doesn't matter
ghsw switch client-a  # Exact profile name
```

### List Profiles

```bash
ghsw list
# Shows table with profile names, emails, SSH security status, and activity
```

The list command displays:
- **Profile**: Profile name
- **Name**: Full name for git commits  
- **Email**: Email address for git commits
- **SSH Security**: 🔐 Protected (passphrase-protected) or 🔓 Unprotected
- **Status**: 🟢 Active or ⚪ Inactive
- **Last Used**: When the profile was last switched to

### Current Profile

```bash
ghsw current
# Shows currently active profile details
```

## 🔒 Advanced SSH Key Management

### Copy SSH Key

```bash
# Interactive - choose from list
ghsw copy-key

# Direct - specify profile
ghsw copy-key work
```

Copies SSH public key to clipboard for adding to GitHub settings. Shows key fingerprint for verification.

### Enhanced Connection Testing

```bash
# Interactive - choose from list
ghsw test

# Direct - test specific profile with comprehensive diagnostics
ghsw test work
```

**Advanced Connection Testing Features:**
- **Key Existence Check**: Verifies SSH key files are present
- **Encryption Detection**: Identifies passphrase-protected keys
- **SSH Agent Status**: Checks if encrypted keys are loaded in ssh-agent
- **Configuration Validation**: Ensures SSH config entries are correct
- **GitHub Connectivity**: Tests actual connection to GitHub servers
- **Error Guidance**: Provides specific solutions for connection issues

**Example Output:**
```bash
ghsw test work
🔍 Testing SSH connection for 'work' profile...
✅ SSH key file exists: ~/.ssh/id_ed25519_work
🔐 Key is passphrase-protected
✅ Key is loaded in ssh-agent
✅ SSH config entry is properly configured
✅ GitHub connection successful
🎯 Profile 'work' is ready to use
```

### SSH Key Regeneration with Security Options

```bash
# Interactive - choose from list with security options
ghsw regenerate-key

# Direct - regenerate for specific profile
ghsw regenerate-key work
```

**Enhanced Regeneration Features:**
- **Passphrase Protection**: Option to encrypt new SSH keys
- **Secure Key Generation**: Uses Ed25519 algorithm for optimal security
- **Fingerprint Tracking**: Updates profile metadata with new key fingerprint
- **Automatic Clipboard**: Copies new public key for GitHub update
- **Non-Destructive**: Safely removes old keys after successful generation

**Example Workflow:**
```bash
ghsw regenerate-key work
🔐 SSH Key Options
🔐 Protect new SSH key with passphrase? [y/N]: y
🔑 Enter passphrase for SSH key: [secure input]
✅ Generated passphrase-protected SSH key for work
📋 New SSH public key copied to clipboard
```

### Comprehensive SSH Environment Analysis

```bash
ghsw detect
```

**Enhanced Detection Provides:**

📊 **SSH Key Analysis:**
- Total keys found with type breakdown (Ed25519, RSA, etc.)
- Passphrase protection status
- Key fingerprints for identification
- Security recommendations

🏷️ **Profile Associations:**
- Which profiles use which SSH keys
- Available keys for import
- Duplicate detection

🔌 **SSH Agent Status:**
- ssh-agent running status
- Keys currently loaded in agent
- Encrypted keys requiring passphrase entry

⚙️ **SSH Configuration:**
- GitHub Switcher managed entries
- Legacy configuration detection
- Backup file status

🌐 **Connectivity Testing:**
- GitHub connection validation
- Profile-specific connection testing
- Performance metrics

**Example Output:**
```bash
ghsw detect
🔍 Analyzing SSH environment...

📊 SSH Key Analysis:
  🔑 Total keys found: 4
  ✅ Ed25519 keys: 2 (recommended)
  ⚠️  RSA keys: 2 (legacy)
  🔐 Passphrase-protected: 1
  🔓 Unencrypted: 3

🏷️ Profile Associations:
  ✅ work → id_ed25519_work (SHA256:abc123...)
  ✅ personal → id_ed25519_personal (SHA256:def456...)
  🔄 Available for import: id_rsa_old (SHA256:ghi789...)

🔌 SSH Agent Status:
  ✅ ssh-agent running
  🔑 2 keys loaded in agent
  🔐 1 encrypted key needs loading

🌐 GitHub Connectivity: ✅ All connections optimal
```

## Profile Management

### Delete Profile

```bash
# Interactive - choose from list with confirmation
ghsw delete

# Direct - delete specific profile
ghsw delete old-profile

# Skip confirmation
ghsw delete old-profile --yes
```

Removes profile configuration and cleans up SSH keys.

## Common Workflows

### Personal & Work Setup

```bash
# Create work profile
ghsw create --name work --fullname "Your Name" --email work@company.com

# Create personal profile  
ghsw create --name personal --fullname "Your Name" --email personal@gmail.com

# Switch between them
ghsw switch work      # For work projects
ghsw switch personal  # For personal projects
```

### Multiple Client Management

```bash
# Create client profiles
ghsw create --name client-a --email you@client-a.com
ghsw create --name client-b --email you@client-b.com

# Switch as needed
ghsw switch client-a  # Work on Client A projects
ghsw switch client-b  # Switch to Client B
```

### SSH Key Strategies

**Import Existing Keys (Reuse):**
- Choose "import" during profile creation
- Reuses your existing SSH keys
- Good when approaching GitHub's 5-key limit

**Generate New Keys (Recommended):**
- Choose "new" during profile creation
- Creates dedicated SSH key per profile
- Better security isolation

## What Happens When You Switch

When you run `ghsw switch profile-name`, GitHub Switcher:

1. **Updates Git Configuration:**
   - Sets `user.name` to profile's full name
   - Sets `user.email` to profile's email

2. **Configures SSH:**
   - Updates SSH config for GitHub connections
   - Sets default GitHub host to use profile's SSH key

3. **Tracks Active Profile:**
   - Records which profile is currently active
   - Updates last-used timestamps

## Working with Git

After switching profiles, your Git operations use the correct identity:

```bash
# Switch to work profile
ghsw switch work

# Clone work repository
git clone git@github.com:company/project.git

# Make commits - they'll use your work identity
git commit -m "Add new feature"
git push origin main
```

## Troubleshooting

### Profile Not Switching
```bash
# Check current profile
ghsw current

# Verify Git config was updated
git config --global user.name
git config --global user.email
```

### SSH Connection Issues
```bash
# Test SSH connection
ghsw test profile-name

# Copy key to clipboard and add to GitHub
ghsw copy-key profile-name
# Then go to https://github.com/settings/keys

# Check SSH agent
ssh-add -l
```

### Profile Creation Problems
```bash
# Check system requirements
ghsw detect

# Verify Git is installed
git --version

# Check SSH directory permissions
ls -la ~/.ssh/
```

## Best Practices

### Profile Management
1. **Descriptive Profile Names:** Use clear names like `work`, `personal`, `client-abc`
2. **Regular Testing:** Periodically run `ghsw test <profile>` to verify connections
3. **Verify After Switching:** Always check `ghsw current` after switching profiles
4. **Clean Up Unused Profiles:** Remove old profiles with `ghsw delete`

### SSH Key Management
5. **SSH Key Strategy for Multiple GitHub Accounts:**
   - **Generate new keys** for each profile when using different GitHub accounts
   - **Import existing keys** when using one GitHub account with multiple profiles
   - Each GitHub account supports up to 5 SSH keys maximum

6. **Security Best Practices:**
   - Keep SSH keys secure and never share private keys
   - Use Ed25519 keys (default) for better security
   - Regularly regenerate keys for enhanced security
   - Back up SSH keys securely (private keys only locally)

### Workflow Organization
7. **Development Teams:**
   ```bash
   # Set up work and personal separation
   ghsw create --name work --fullname "Your Name" --email work@company.com
   ghsw create --name personal --fullname "Your Name" --email personal@gmail.com
   ```

8. **Freelancer Setup:**
   ```bash
   # Separate client identities
   ghsw create --name client-a --email you@client-a.com
   ghsw create --name client-b --email you@client-b.com
   ghsw create --name personal --email your@personal.com
   ```

9. **Repository Configuration:**
   - Use profile-specific remote URLs: `git@github-work:company/repo.git`
   - Test SSH connection before cloning: `ghsw test work`
   - Verify correct identity after switching: `git config user.email`

### Troubleshooting Prevention
10. **Profile Verification:**
    ```bash
    # Always verify after switching
    ghsw current
    git config --global user.name
    git config --global user.email
    ```

11. **SSH Connection Health:**
    ```bash
    # Regular SSH testing
    ghsw test profile-name
    
    # Check SSH agent status
    ssh-add -l
    ```

12. **Backup and Recovery:**
    - Keep SSH keys backed up securely
    - Document your profile configurations
    - Regular testing prevents issues during critical work

## Command Reference

| Command | Description |
|---------|-------------|
| `ghsw create` | Create new profile (interactive wizard) |
| `ghsw list` | Show all profiles with status |
| `ghsw switch [profile]` | Switch to profile (interactive if no name) |
| `ghsw current` | Show active profile |
| `ghsw delete [profile]` | Remove profile (interactive if no name) |
| `ghsw copy-key [profile]` | Copy SSH public key to clipboard |
| `ghsw test [profile]` | Test SSH connection to GitHub |
| `ghsw regenerate-key [profile]` | Create new SSH key for profile |
| `ghsw detect` | Analyze existing SSH setup |

## Getting Help

- **Command Help:** Add `--help` to any command
- **GitHub Issues:** [Report bugs](https://github.com/mostafagamil/Github-Switcher/issues)
- **Discussions:** [Ask questions](https://github.com/mostafagamil/Github-Switcher/discussions)
- **Documentation:** [Full guides](../README.md#documentation)

## Next Steps

- [SSH Key Management Details](existing-ssh-keys.md)
- [Contributing Guide](contributing.md)  
- [API Reference](api-reference.md)