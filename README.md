# Rotifer Protocol — Papers & Articles

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Published writings on the Rotifer Protocol — an open-source evolution framework for AI agents.

## Articles

### [The Meta-Protocol for Distributed Intelligence Emergence: Hardware as the Physical Entry Point](./rotifer-meta-protocol-hardware-paper.md)

The strategic whitepaper. Why the trillion-device installed base of consumer hardware — phones, vehicles, edge devices — is the physical surface where a meta-protocol for distributed intelligence is most naturally instantiated, and what the architectural commitment requires of the protocol's design today.

**Audience:** Industry partners, OEM strategists, hardware ecosystem researchers, protocol architects

### [Philosophy Whitepaper: Digital Life on a Continuum](./rotifer-philosophy-whitepaper.md)

The philosophical foundations of the Rotifer Protocol — digital life as a spectrum, digital speciation, evolutionary endgames, governance philosophy, and ethical gradualism.

**Audience:** Researchers, philosophers of AI, ethics boards, protocol designers

### [From Skill to Gene: Why Your AI Agent Needs Evolution, Not Just Execution](./rotifer-gene-vs-skill.md)

A deep comparison between Rotifer Genes and conventional Agent Skills (MCP Tools). Explains the paradigm shift from a static tool model to a living, evolving biological model.

**Audience:** AI/Agent creators, MCP community, technical decision-makers

### [From AutoResearch to Collective Evolution](./from-autoresearch-to-collective-evolution.md)

A comparative essay positioning the Rotifer Protocol's collective-evolution model alongside individual-agent autoresearch architectures.

**Audience:** AI researchers, agent framework authors, complex-systems theorists

## Tiering

This repository follows a deliberately small two-tier model:

| Tier | Where it lives | What it means |
|---|---|---|
| **Public** | `*.md` at the root of this repo on `main` | Citable, indexable, discoverable. Subject to the publication gate below. |
| **Internal-Draft** | Not in this repo | Drafts that are not yet citable live in the project's internal workspace and are out of scope here. |

The frontmatter `status:` field in each article (e.g. `Draft`, `Published`, `Stable`) is an author-declared label for human readers. It does **not** bypass the mechanical publication gate.

> See `internal/adr/270-rotifer-papers-tiering-and-publication-gate.md` for the rationale (private to the project workspace).

## Publication Gate

A pre-push hook at `.githooks/pre-push` runs two checks against every pushed commit range:

1. **History audit** — refuses any commit that introduces internal-only file paths (`internal/`, `.env`, secrets, credentials).
2. **Spec §X.Y reference check** — refuses to push when a paper cites a numbered section of *Rotifer Protocol Specification* (lines mentioning `Specification` or `specification` together with a `§X.Y` reference) that is not present in the published executive summary at <https://github.com/rotifer-protocol/rotifer-spec>.

### Public spec sections currently published

```
§1 §1.1 §1.2 §1.3 §1.4   (Problem Statement)
§2                        (Design Principles)
§3                        (URAA — Five-Layer Architecture)
§4                        (Gene Standard, Summary)
§5                        (Fitness Model)
§6                        (Beyond the Executive Summary)
```

The whitelist lives in `scripts/verify-spec-refs.sh` and **must** be updated in the same commit that extends the public spec.

### Setup (one-time, for contributors)

```bash
git clone https://github.com/rotifer-protocol/rotifer-papers.git
cd rotifer-papers
git config core.hooksPath .githooks
```

After this, the hooks run automatically on every `git commit` and `git push`.

### Running the spec-refs check manually

```bash
./scripts/verify-spec-refs.sh                    # check every *.md at root
./scripts/verify-spec-refs.sh path/to/paper.md   # check a single file
```

### Per-line escape hatch

Edge cases (e.g. a sentence that explicitly contrasts a paper's own `§X.Y` against a spec `§Y`) can mark a single line as exempt:

```markdown
See *Rotifer Protocol Specification* §5 (Fitness) and §2.4 of this paper. <!-- spec-ref-allow: §2.4 is internal self-reference -->
```

Use sparingly. `git blame` will record both the reference and the reason.

## Withdrawn Papers

Two papers were withdrawn from this repository on 2026-04-27, approximately one hour after first publication, when a self-audit found their `§X.Y` references targeted sections of the protocol specification that exist only in the project's internal full version, not in the published executive summary.

| Paper | Withdrawn | Reason |
|---|---|---|
| `rotifer-evaluation-methodology.md` / `.zh.md` | 2026-04-27 | Cited spec sections (§14, §19, §24.5, §39, §40, §41) not present in the public specification. |
| `rotifer-fitness-evolution-chain.md` / `.zh.md` | 2026-04-27 | Cited spec sections (§14, §15, §38, §39) not present in the public specification. |

The drafts are preserved in the project's internal workspace and may be re-published once either (a) the public specification is extended to include the cited sections, or (b) the drafts are revised to no longer depend on internal section numbers.

The publication gate above was added in the same period to prevent a recurrence.

## Related Repositories

- [**rotifer-spec**](https://github.com/rotifer-protocol/rotifer-spec) — the protocol specification (executive summary)
- [**rotifer-playground**](https://github.com/rotifer-protocol/rotifer-playground) — CLI tool for gene development, Arena competition, and protocol simulation
- [Rotifer Protocol Website](https://rotifer.dev)

## Citation

If you reference these works in academic contexts:

```bibtex
@misc{rotifer2026philosophy,
  title  = {Digital Life on a Continuum: A Philosophical Framework for the Rotifer Protocol},
  author = {Rotifer Protocol Contributors},
  year   = {2026},
  url    = {https://github.com/rotifer-protocol/rotifer-papers}
}

@misc{rotifer2026metaprotocol,
  title  = {The Meta-Protocol for Distributed Intelligence Emergence: Hardware as the Physical Entry Point},
  author = {Rotifer Foundation},
  year   = {2026},
  url    = {https://github.com/rotifer-protocol/rotifer-papers}
}
```

## License

These articles are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt these works, provided you give appropriate credit.
