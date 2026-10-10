# Contributing

Thank you for contributing to Video-to-Audio.

## Commit messages: Conventional Commits

Every new commit **must** follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

Format:

```text
<type>[optional scope][!]: <short description>

[optional body]

[optional footer(s)]
```

Use an imperative, concise description. Do not end the subject with a period.
Recommended scopes: `converter`, `gui`, `windows`, `tests`, `deps`, `ci`, `docs`.

Common types:

- `feat`: a new feature
- `fix`: a bug fix
- `docs`: documentation only
- `test`: tests added or corrected
- `refactor`: internal code changes without feature or bug fix
- `perf`: a performance improvement
- `build`: dependencies, packaging and build tooling
- `ci`: continuous integration
- `chore`: maintenance not covered by another type
- `style`: formatting only

Examples:

```text
fix(converter): close FFmpeg pipes after conversion
feat(gui): add cancel conversion button
test(converter): cover concurrent output collisions
docs(windows): describe Start menu shortcut
```

For breaking changes, use `!` in the header (e.g. `feat(api)!: rename conversion options`) and explain them in a `BREAKING CHANGE:` footer.

**Pull request titles must use the same convention**, particularly when squash merges are used. Avoid rewriting commits already shared or fetched by collaborators just to change their messages: if a shared commit is already compliant, preserve its SHA.

## Validation before merge

- Run `python -m unittest discover -s tests -v` in the project's virtual environment.
- Test a real MKV-to-MP3 conversion through the Windows Start menu shortcut after modifying the GUI or converter.
- Never modify or depend on another project's Python environment (including WhisperX).
- Preserve upstream attribution, icons and the Apache-2.0 license.
