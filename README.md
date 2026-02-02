# Bug Bounty Toolkit

Quick-start toolkit for bug bounty hunting.

## Directory Structure

```
bugbounty/
├── targets/          # Per-target recon data
├── wordlists/        # Fuzzing wordlists
├── scripts/          # Automation scripts
├── reports/          # Bug reports
├── notes/            # Research notes
└── tools/            # Additional tools
```

## Installed Tools

- **ffuf** - Fast web fuzzer for directory/parameter discovery

## Quick Start

### 1. Directory Fuzzing
```bash
cd scripts
./ffuf-quick.sh https://target.com
```

### 2. Manual Testing
Follow the checklist: `BURP_SUITE_CHECKLIST.md`

### 3. Basic Recon
```bash
cd scripts
./recon.sh target.com
```

## Recommended Workflow

1. **Choose a target** from HackerOne/Bugcrowd
2. **Read the scope** carefully
3. **Run basic recon** to enumerate attack surface
4. **Manual testing** with Burp Suite using the checklist
5. **Document findings** in reports/

## Bug Bounty Platforms

- [HackerOne](https://hackerone.com)
- [Bugcrowd](https://bugcrowd.com)
- [Intigriti](https://intigriti.com)

## Learning Resources

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTheBox](https://hackthebox.com)
- [PentesterLab](https://pentesterlab.com)

## Tips

- Always stay within scope
- Document everything
- Be patient - good bugs take time
- Focus on one vulnerability type to start
- Read previous disclosed reports for inspiration
