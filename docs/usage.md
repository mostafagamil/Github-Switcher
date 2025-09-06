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
1. Detects existing SSH keys and GitHub setup
2. Guides you through profile creation
3. Handles SSH key generation or import automatically
4. Copies public key to clipboard for GitHub

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
# Shows table with profile names, emails, and status
```

### Current Profile

```bash
ghsw current
# Shows currently active profile details
```

## SSH Key Management

### Copy SSH Key

```bash
# Interactive - choose from list
ghsw copy-key

# Direct - specify profile
ghsw copy-key work
```

Copies SSH public key to clipboard for adding to GitHub settings.

### Test SSH Connection

```bash
# Interactive - choose from list
ghsw test

# Direct - test specific profile
ghsw test work
```

Verifies SSH connection to GitHub works properly.

### Regenerate SSH Key

```bash
# Interactive - choose from list  
ghsw regenerate-key

# Direct - regenerate for specific profile
ghsw regenerate-key work
```

Creates new SSH key and copies to clipboard for GitHub update.

### Detect Existing Setup

```bash
ghsw detect
```

Analyzes your current SSH configuration and shows:
- GitHub connectivity status
- Available SSH keys
- Profile associations
- Configuration recommendations

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