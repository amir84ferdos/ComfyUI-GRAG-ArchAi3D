# Contributing to GRAG v3.0

Thank you for considering contributing to GRAG! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

## 🤝 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inspiring community for all.

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Enforcement
Unacceptable behavior may be reported to Amir84ferdos@gmail.com

## 💡 How Can I Contribute?

### Reporting Bugs
**Before submitting a bug report:**
1. Check existing [GitHub Issues](https://github.com/amir84ferdos/ComfyUI-GRAG/issues)
2. Verify you're using the latest version
3. Test with default settings

**Bug Report Template:**
```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Environment
- GRAG Version: v3.0.0
- ComfyUI Version: X.X.X
- Python Version: 3.X.X
- OS: Windows/Linux/Mac
- PyYAML Installed: Yes/No

## Console Output
```
Paste relevant console output here
```

## Screenshots (if applicable)
Attach screenshots
```

### Suggesting Enhancements
**Enhancement Proposal Template:**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How would this feature work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Any other relevant information
```

### Contributing Code
Areas where contributions are especially welcome:
- 🐛 Bug fixes
- 📚 Documentation improvements
- 🎨 New presets (with testing/validation)
- ⚡ Performance optimizations
- 🧪 Test coverage improvements
- 🌐 Internationalization/Localization
- 🎯 New features (discuss first via GitHub Issues)

### Contributing Presets
We welcome new preset contributions! Please:
1. Test thoroughly with multiple images
2. Document use case and parameters
3. Follow preset naming convention
4. Submit via Pull Request with examples

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- ComfyUI installed
- Git
- Text editor or IDE

### Setup Steps

1. **Fork the Repository**
   ```bash
   # On GitHub, click "Fork"
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ComfyUI-GRAG.git
   cd ComfyUI-GRAG
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/amir84ferdos/ComfyUI-GRAG.git
   ```

4. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # Optional: Install dev dependencies
   pip install pytest black flake8
   ```

6. **Install in ComfyUI**
   ```bash
   # Create symlink or copy to ComfyUI custom_nodes
   ln -s /path/to/ComfyUI-GRAG /path/to/ComfyUI/custom_nodes/GRAG
   ```

## 📝 Pull Request Process

### Before Submitting
1. ✅ Test your changes thoroughly
2. ✅ Update documentation if needed
3. ✅ Add/update tests if applicable
4. ✅ Ensure code follows style guidelines
5. ✅ Update CHANGELOG.md (under "Unreleased")
6. ✅ Verify no merge conflicts with main branch

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe testing performed:
- [ ] Tested with Simple Controller
- [ ] Tested with Unified Controller
- [ ] Tested with different presets
- [ ] Verified console output
- [ ] No regressions observed

## Screenshots (if applicable)
Attach before/after screenshots

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed code
- [ ] Commented code (especially complex areas)
- [ ] Updated documentation
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] No new warnings
- [ ] Updated CHANGELOG.md
```

### Review Process
1. Maintainer will review within 7 days
2. Address any requested changes
3. Once approved, maintainer will merge
4. Your contribution will be credited in CHANGELOG.md

## 💅 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation (no tabs)
- Max line length: 100 characters
- Use type hints where appropriate

### Example:
```python
def apply_grag_v3(
    joint_key: torch.Tensor,
    seq_txt: int,
    config: GRAGConfig
) -> torch.Tensor:
    """Apply GRAG v3.0 reweighting to attention keys.

    Args:
        joint_key: Concatenated text+image keys [B, S, H, D]
        seq_txt: Length of text sequence
        config: GRAGConfig object with parameters

    Returns:
        Reweighted keys tensor [B, S, H, D]
    """
    # Implementation here
    pass
```

### Naming Conventions
- Classes: `PascalCase` (e.g., `GRAGSimpleController`)
- Functions/Methods: `snake_case` (e.g., `apply_grag_simple`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `PRESET_STRATEGIES`)
- Private: `_leading_underscore` (e.g., `_patch_qwen_attention`)

### Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Include type hints
- Explain complex algorithms with comments

### Console Output
- Use descriptive prefixes: `[GRAG Simple]`, `[GRAG v3.0]`
- Include relevant parameter values
- Use emojis sparingly (only in user-facing UI)

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] Test with Simple Controller
- [ ] Test with Unified Controller (all 3 modes)
- [ ] Test with different presets
- [ ] Test with PyYAML installed
- [ ] Test without PyYAML (fallback presets)
- [ ] Test error handling (invalid inputs)
- [ ] Check console output for errors/warnings
- [ ] Verify no contamination (test standard KSampler after)

### Automated Testing (Future)
We plan to add automated tests. Contributions welcome!

## 📚 Documentation Guidelines

### README.md
- Keep updated with new features
- Include examples
- Update badges if needed

### Inline Documentation
```python
# Good:
# Calculate deviation from neutral (1.0) to enable proportional scaling
lambda_deviation = lambda_base - 1.0

# Bad:
# Calculate deviation
lambda_deviation = lambda_base - 1.0
```

### User Documentation
- Use simple language
- Include examples
- Add screenshots where helpful
- Explain WHY, not just HOW

## 🎨 Preset Contribution Guidelines

### Preset Naming
```
Category: Name (description)
```
Examples:
- `Paper: Balanced` (paper-recommended)
- `Clean Room: Gentle` (interior design)
- `Portrait: Soft` (portrait photography)

### Preset Metadata
```yaml
preset_key:
  name: "Display Name"
  lambda: 1.05
  delta: 1.10
  strength: 1.0
  description: "Detailed description of effect"
  category: "category_name"
  use_case: "interior_design / portrait / general / etc"
```

### Preset Testing
Before submitting, test with:
- At least 5 different images
- Different content types (interior/exterior/portrait/etc)
- Various resolutions
- Document observable effects

## 🔄 Git Workflow

### Branch Naming
- Features: `feature/short-description`
- Bug fixes: `fix/bug-description`
- Documentation: `docs/what-changed`
- Performance: `perf/optimization-description`

### Commit Messages
```
Short (50 chars or less) summary

More detailed explanatory text, if necessary. Wrap at 72 characters.
Explain the problem this commit solves and why you chose this solution.

- Bullet points are okay
- Use imperative mood ("Add feature" not "Added feature")
```

### Keeping Fork Updated
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 📬 Contact

### Questions?
- GitHub Issues: For bugs and feature requests
- Email: Amir84ferdos@gmail.com
- LinkedIn: [ArchAi3d](https://www.linkedin.com/in/archai3d/)

### Discussion
- GitHub Discussions (if enabled)
- ComfyUI Discord (search for GRAG threads)

## 🏆 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Credited in GitHub contributors page
- Mentioned in release notes (for significant contributions)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to GRAG!** 🎉

Your contributions help make GRAG better for everyone.
