# Advanced SSH Key Management

GitHub Switcher provides enterprise-grade SSH key management with automatic detection, deduplication, passphrase protection, ssh-agent integration, and intelligent connection testing.

## Comprehensive SSH Detection

When you run `ghsw create`, the wizard performs a comprehensive analysis:

```bash
ghsw create
# Output:
🔍 Detecting existing GitHub setup...
✅ GitHub SSH connection is working
🔑 Found 3 SSH key(s):
  ✅ id_ed25519_work (john@company.com) → used by 'work' profile
  ✅ id_ed25519_personal (john@gmail.com) → used by 'personal' profile  
  ✅ id_ed25519 (old@email.com)
⚙️ SSH config has 4 GitHub entries
```

**What Gets Detected:**
- **SSH Connectivity**: Tests actual connection to GitHub with intelligent error analysis
- **All SSH Keys**: Scans `~/.ssh/` for Ed25519, RSA, ECDSA keys with format validation
- **Key Fingerprinting**: SHA256 fingerprints for deduplication and identification
- **Passphrase Protection**: Automatically detects encrypted vs unencrypted keys
- **SSH Agent Integration**: Checks if keys are loaded in ssh-agent
- **Profile Associations**: Shows which keys are already used by profiles
- **GitHub Compatibility**: Identifies recommended key types and security levels
- **SSH Configuration**: Analyzes existing GitHub entries with conflict detection

## Smart SSH Strategy Selection

Based on detection results, the wizard intelligently offers appropriate options:

### Scenario 1: No Available Keys (All Used)
```
💡 All SSH keys are already used by profiles. Will generate a new Ed25519 key.
```
**Result**: Automatically generates new key - no confusing choices

### Scenario 2: Available Keys for Import
```
Options:
• import: Use one of your existing SSH keys
• new: Generate a fresh SSH key for this profile
```

## Option 1: Generate New Key (Recommended)

This is the default and recommended approach:

- Creates a dedicated SSH key for this profile
- Maintains separation between different GitHub identities
- Follows security best practices
- No risk of conflicts with existing setup

**When to choose this:**
- You want complete isolation between profiles
- Security is a priority
- You're setting up work/personal separation
- You have sufficient SSH key slots on GitHub (max 5 keys per account)

## Option 2: Import Existing Key

Reuses one of your existing SSH keys:

- Shows a list of available SSH keys
- Creates a profile-specific copy of the selected key
- Preserves your existing setup
- Allows sharing keys between profiles if needed

**When to choose this:**
- You're approaching GitHub's SSH key limit
- You want to reuse a key you've already added to GitHub
- You're migrating from manual SSH management
- You have a specific key you prefer to use

### Import Process

1. Select "import" when prompted
2. Choose from available SSH keys:
   ```
   📋 Available SSH Keys:
   1. id_rsa
   2. id_ed25519  
   3. id_ecdsa
   4. Generate new key
   ```
3. The selected key is copied and configured for your profile

## Option 3: Skip SSH Setup

For advanced users who want manual control:

- Creates profile without SSH key generation
- You can set up SSH keys manually later
- Useful for complex networking environments
- Good for testing or special configurations

**When to choose this:**
- You have custom SSH configurations
- You're using SSH certificates or other advanced setups
- You want to set up keys manually later
- You're testing or troubleshooting

## 🔒 Enhanced Security Features

### Passphrase-Protected SSH Keys

GitHub Switcher now supports passphrase-protected SSH keys for enhanced security:

```bash
# Generate a passphrase-protected key
ghsw regenerate-key work
# Output:
🔐 SSH Key Options
🔐 Protect new SSH key with passphrase? [y/N]: y
🔑 Enter passphrase for SSH key: [secure input]
✅ Generated passphrase-protected SSH key for work
🔐 Key encrypted and saved securely
```

**Benefits:**
- **Enhanced Security**: Even if your key file is compromised, it's encrypted
- **Industry Standard**: Follows enterprise security best practices
- **SSH Agent Integration**: Works seamlessly with ssh-agent for convenience

### Automatic Passphrase Detection

The system automatically detects passphrase-protected keys:

```bash
ghsw test work
# For encrypted keys not in ssh-agent:
❌ SSH key is passphrase-protected and not in ssh-agent
💡 Try: ssh-add ~/.ssh/id_ed25519_work
```

### SSH Agent Integration

GitHub Switcher intelligently manages ssh-agent integration:

**Automatic Detection:**
- Checks if keys are loaded in ssh-agent
- Provides helpful guidance for encrypted keys
- Suggests proper ssh-add commands

**Connection Testing:**
```bash
ghsw test work
# Intelligent connection testing:
# 1. Checks if key exists
# 2. Detects if key is encrypted
# 3. Verifies ssh-agent status
# 4. Tests actual GitHub connection
# 5. Provides specific error guidance
```

### Key Fingerprinting & Deduplication

Advanced key management prevents duplicates:

```bash
ghsw detect
# Output shows fingerprints:
🔑 Found SSH keys:
  ✅ id_ed25519_work (SHA256:abc123...) → work profile
  ✅ id_ed25519 (SHA256:def456...) 
  ⚠️ id_rsa (SHA256:ghi789...) - RSA key detected
```

**Features:**
- **SHA256 Fingerprints**: Unique identification for each key
- **Duplicate Prevention**: Never import the same key twice
- **Profile Tracking**: See which profile uses which key

## SSH Configuration Management

GitHub Switcher preserves your existing SSH configuration while adding its own entries:

### Backup Creation

On first use, GitHub Switcher creates a backup:
```
~/.ssh/config.github-switcher-backup
```

This ensures you can always restore your original configuration.

### Configuration Structure  

Your SSH config will look like:
```
# Your existing entries (unchanged)
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa

# GitHub Switcher entries (added)
Host github-work
    HostName github.com  
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
```

## Best Practices

### For Multiple GitHub Accounts

If you use different GitHub accounts (work/personal):

1. **Generate new keys** for each profile
2. Add each key to the respective GitHub account
3. Use profile-specific git remotes:
   ```bash
   # Work repository
   git remote add origin git@github-work:company/repo.git
   
   # Personal repository  
   git remote add origin git@github-personal:username/repo.git
   ```

### For Single Account, Multiple Profiles

If you use one GitHub account but want different commit identities:

1. **Import existing key** for all profiles
2. All profiles can share the same SSH key
3. Only git config (name/email) changes between profiles

### Migration from Manual Setup

If you currently manage SSH manually:

1. **Import your existing key** for your primary profile
2. **Generate new keys** for additional profiles  
3. Let GitHub Switcher manage SSH config going forward
4. Remove manual SSH config entries after testing

## Troubleshooting

### SSH Key Not Working After Import

```bash
# Test the imported key
ghsw test your-profile

# Check SSH agent
ssh-add -l

# Add key to SSH agent if needed
ssh-add ~/.ssh/id_ed25519_your-profile
```

### Existing Config Conflicts

If you see SSH errors after setup:

1. Check your SSH config: `cat ~/.ssh/config`
2. Look for conflicting Host entries
3. Restore from backup if needed: 
   ```bash
   cp ~/.ssh/config.github-switcher-backup ~/.ssh/config
   ```
4. Re-run GitHub Switcher setup

### GitHub Key Limit Reached

GitHub allows max 5 SSH keys per account:

1. **Remove unused keys** from GitHub settings
2. **Reuse keys** by importing instead of generating new ones
3. **Use GitHub fine-grained tokens** as an alternative
4. **Use multiple GitHub accounts** if you need more separation

## 🚀 Enhanced CLI Commands

### Intelligent SSH Key Regeneration

The `regenerate-key` command now offers advanced options:

```bash
ghsw regenerate-key work
# Interactive options:
🔐 SSH Key Options
🔐 Protect new SSH key with passphrase? [y/N]: 
🔧 Keep existing fingerprint for profile tracking? [Y/n]:
✅ Regenerated SSH key with enhanced security options
📋 New SSH public key copied to clipboard
```

### Advanced Connection Testing

The `test` command provides comprehensive diagnostics:

```bash
ghsw test work
# Comprehensive output:
🔍 Testing SSH connection for 'work' profile...
✅ SSH key file exists: ~/.ssh/id_ed25519_work
🔐 Key is passphrase-protected
✅ Key is loaded in ssh-agent
✅ SSH config entry is properly configured  
✅ GitHub connection successful
🎯 Profile 'work' is ready to use
```

**Error scenarios with guidance:**
```bash
# Encrypted key not in agent:
❌ Key is passphrase-protected and not in ssh-agent
💡 Try: ssh-add ~/.ssh/id_ed25519_work

# SSH config issues:
❌ SSH config entry missing or invalid
💡 Try: ghsw switch work  # Rebuilds SSH config

# GitHub connection problems:
❌ GitHub rejected SSH connection
💡 Ensure key is added to GitHub account settings
```

### Enhanced Detection Command

The `detect` command now provides rich SSH environment analysis:

```bash
ghsw detect
# Comprehensive SSH environment report:
🔍 Analyzing SSH environment...

📊 SSH Key Analysis:
  🔑 Total keys found: 4
  ✅ Ed25519 keys: 2 (recommended)
  ⚠️  RSA keys: 2 (legacy)
  🔐 Passphrase-protected: 1
  🔓 Unencrypted: 3

🏷️  Profile Associations:
  ✅ work → id_ed25519_work (SHA256:abc123...)
  ✅ personal → id_ed25519_personal (SHA256:def456...)
  🔄 Available for import: id_rsa_old (SHA256:ghi789...)

🔌 SSH Agent Status:
  ✅ ssh-agent running
  🔑 2 keys loaded in agent
  🔐 1 encrypted key needs loading

⚙️  SSH Configuration:
  ✅ GitHub Switcher entries: 2
  ⚠️  Legacy entries detected: 1
  🔧 Backup available: ~/.ssh/config.github-switcher-backup

🌐 GitHub Connectivity:
  ✅ Primary connection working
  ✅ Profile-specific connections tested
  📈 All connections optimal
```

## Advanced Configurations

### Custom SSH Key Types

GitHub Switcher generates Ed25519 keys by default (most secure), but you can import any key type:

- RSA (legacy, still supported)
- ECDSA (good compatibility)  
- Ed25519 (recommended, fastest)

### SSH Certificates

If you use SSH certificates, choose "skip" and manage SSH manually:

```bash
ghsw create --name work --fullname "Your Name" --email work@company.com
# Choose "skip" for SSH setup
# Then configure SSH certificates manually
```

### Complex Networking

For VPN, proxy, or corporate environments:

1. Set up basic profile with "skip" option
2. Manually configure SSH with your network settings
3. Update profile SSH path: `ghsw edit work`

## Security Considerations

- **Key Isolation**: New keys provide better security isolation
- **Key Reuse**: Importing keys is convenient but reduces isolation  
- **Backup Safety**: SSH config backups contain no private keys
- **Permission Management**: All keys maintain proper file permissions (600/644)

The choice between new keys and importing existing ones depends on your security requirements and GitHub account limitations.