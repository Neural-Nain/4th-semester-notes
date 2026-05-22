#!/usr/bin/env python3
"""Generate Topic 5 HTML from prompt5.txt — preserves all source text."""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = (ROOT / "prompt5.txt").read_text(encoding="utf-8")

SECTION_RE = re.compile(r"(5\.(?:1[0-3]|[1-9]))\s+")
parts = SECTION_RE.split(RAW)
preamble = parts[0].strip()
sections = {}
for i in range(1, len(parts), 2):
    sections[parts[i]] = (parts[i + 1] if i + 1 < len(parts) else "").strip()

IMAGE_FOR_55 = """
<figure class="diagram figure-photo">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/1f/Block_cipher_operation_%28EN%29.svg" alt="Block cipher operation diagram" width="640" height="360" loading="lazy" decoding="async" />
  <figcaption>Block cipher operation (Wikimedia Commons). Compare with stream ciphers that XOR plaintext with a keystream bit-by-bit or byte-by-byte.</figcaption>
</figure>
"""

EXTRA_FIGURES = {
    "5.1": """
<figure class="diagram figure-photo">
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2b/Public-key-crypto-1.svg" alt="Public-key cryptography diagram" width="520" height="380" loading="lazy" decoding="async" />
  <figcaption>Public-key cryptography complements symmetric secret-key encryption (Wikimedia Commons).</figcaption>
</figure>
""",
    "5.5": IMAGE_FOR_55
    + """
<figure class="diagram figure-photo">
  <img src="https://upload.wikimedia.org/wikipedia/commons/4/4c/CBC_mode_encryption.svg" alt="Cipher Block Chaining diagram" width="640" height="280" loading="lazy" decoding="async" />
  <figcaption>Cipher Block Chaining (CBC) mode (Wikimedia Commons).</figcaption>
</figure>
""",
    "5.7": """
<figure class="diagram figure-photo">
  <img src="https://upload.wikimedia.org/wikipedia/commons/6/6a/End_to_end_encryption_diagram.svg" alt="End-to-end encryption diagram" width="640" height="320" loading="lazy" decoding="async" />
  <figcaption>End-to-end encryption vs hop-by-hop link encryption (Wikimedia Commons).</figcaption>
</figure>
""",
    "5.13": """
<figure class="diagram figure-photo">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/SSL_TLS_full_handshake.png" alt="TLS handshake diagram" width="720" height="400" loading="lazy" decoding="async" />
  <figcaption>TLS/SSL full handshake used by HTTPS (Wikimedia Commons).</figcaption>
</figure>
""",
}

SYM_TABLE = """
<div class="table-wrap">
  <table>
    <caption>Symmetric vs asymmetric cryptographic paradigms (Section 5.6)</caption>
    <thead>
      <tr><th scope="col">Architectural feature</th><th scope="col">Symmetric cryptography (secret-key)</th><th scope="col">Asymmetric cryptography (public-key)</th></tr>
    </thead>
    <tbody>
      <tr><th scope="row">Key architecture</th><td>Uses a single, shared secret key for both encryption and decryption operations.</td><td>Uses a mathematically linked Key Pair: a public key for encryption and a private key for decryption.</td></tr>
      <tr><th scope="row">Computational speed</th><td>Fast. Designed for high-throughput data processing with minimal CPU overhead.</td><td>Slow. Relies on complex, resource-intensive prime number factorization or discrete logarithms.</td></tr>
      <tr><th scope="row">Primary use cases</th><td>Encrypting bulk data at rest (hard drives, databases) and bulk data in transit (TLS data phase).</td><td>Secure key exchange protocols, digital signatures, and identity verification.</td></tr>
      <tr><th scope="row">Key distribution problem</th><td>High. The sender and receiver must find a secure way to share the secret key before communicating.</td><td>Low. The public key can be openly distributed over insecure channels without compromising security.</td></tr>
      <tr><th scope="row">Scalability (N users)</th><td>Scales poorly. Requires N(N-1)/2 unique keys for secure, isolated communication across a group.</td><td>Scales well. Each user only needs to maintain and protect their own single key pair (2N keys total).</td></tr>
    </tbody>
  </table>
</div>
"""

SECTION_TITLES = {
    "5.1": "Introduction to Cryptology (The Historical and Mathematical Context)",
    "5.2": "Core Mathematical and Technical Goals of Cryptography",
    "5.3": "Technical Lexicon: Foundations of Secret Writing",
    "5.4": "Kerckhoffs's Principle: The Gold Standard of Security Architecture",
    "5.5": "Classification of Ciphers by Data Processing Modes",
    "5.6": "Symmetric vs. Asymmetric Cryptographic Paradigms",
    "5.7": "Network-Level Encryption Deployment: Link vs. End-to-End",
    "5.8": "Key Space and Cryptographic Strength",
    "5.9": "Steganography vs. Cryptography",
    "5.10": "Cryptographic Hashing",
    "5.11": "Symmetric Encryption Algorithms: High-Level Summary",
    "5.12": "Asymmetric Encryption Algorithms: High-Level Summary",
    "5.13": "Network Security Architectures: HTTPS and E2EE",
}


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def formulas_to_html(text: str) -> str:
    out = []
    pos = 0
    for m in re.finditer(r"\$\$([^$]+)\$\$", text):
        if m.start() > pos:
            out.append(esc(text[pos : m.start()]))
        out.append(f'<div class="formula">{esc(m.group(1).strip())}</div>')
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def is_diagram_line(line: str) -> bool:
    return bool(re.search(r"[┌┐└┘│─┬┴┼▼▲═]", line)) or (
        "==(" in line and ")==>" in line
    )


def render_body(key: str, body: str) -> str:
    body = body.replace("\r\n", "\n")

    # Image placeholder from source
    body = re.sub(
        r"\[Image comparing Stream Cipher processing bit-by-bit vs Block Cipher processing fixed blocks of data\]",
        "__FIG55__",
        body,
    )

    # Extract diagram blocks
    lines = body.split("\n")
    chunks = []
    i = 0
    while i < len(lines):
        if is_diagram_line(lines[i]):
            block = []
            while i < len(lines) and (is_diagram_line(lines[i]) or not lines[i].strip()):
                if lines[i].strip():
                    block.append(lines[i])
                i += 1
            chunks.append(("diagram", "\n".join(block)))
        else:
            buf = []
            while i < len(lines) and not is_diagram_line(lines[i]):
                buf.append(lines[i])
                i += 1
            chunks.append(("text", "\n".join(buf)))

    html_out = []
    for kind, content in chunks:
        if kind == "diagram":
            html_out.append(f'<pre class="diagram-flow">{esc(content)}</pre>')
        else:
            html_out.append(render_text_chunk(key, content))

    result = "".join(html_out)
    result = result.replace("__FIG55__", IMAGE_FOR_55)
    return result


def render_text_chunk(key: str, text: str) -> str:
    text = text.strip()
    if not text:
        return ""

    if key == "5.6" and "Architectural Feature" in text:
        before, _, after = text.partition("5.7")
        # keep only 5.6 part
        text = text.split("5.7")[0] if "5.7" in text else text
        return SYM_TABLE + render_prose(text.replace(
            "Architectural FeatureSymmetric Cryptography (Secret-Key)Asymmetric Cryptography (Public-Key)Key ArchitectureUses a single, shared secret key for both encryption and decryption operations.Uses a mathematically linked Key Pair: a public key for encryption and a private key for decryption.Computational SpeedFast. Designed for high-throughput data processing with minimal CPU overhead.Slow. Relies on complex, resource-intensive prime number factorization or discrete logarithms.Primary Use CasesEncrypting bulk data at rest (hard drives, databases) and bulk data in transit (TLS data phase).Secure key exchange protocols, digital signatures, and identity verification.Key Distribution ProblemHigh. The sender and receiver must find a secure way to share the secret key before communicating.Low. The public key can be openly distributed over insecure channels without compromising security.Scalability ($N$ Users)Scales poorly. Requires $N(N-1)/2$ unique keys for secure, isolated communication across a group.Scales well. Each user only needs to maintain and protect their own single key pair ($2N$ keys total).",
            "",
        ))

    # Split numbered items: "1. Title" or lettered "a. Title:"
    pieces = re.split(
        r"(?=(?:(?:^|\n)\d+\.\s+[A-Z])|(?:(?:^|\n)[a-z]\.\s+[A-Z])|(?:(?:^|\n)The Symbiotic Relationship)|(?:(?:^|\n)Kerckhoffs's Principle:)|(?:(?:^|\n)Why \"Security through Obscurity\")|(?:(?:^|\n)Core Properties of a Secure Hash))",
        text,
    )

    out = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        m = re.match(r"^(\d+)\.\s+([^\n]+)", piece)
        if m:
            heading = piece[: piece.find(".", 2) + 1 + len(m.group(2))]
            rest = piece[len(heading) :].lstrip()
            title = m.group(2).strip()
            out.append(f"<h3>{esc(m.group(1))}. {esc(title)}</h3>")
            out.append(render_prose(rest))
            continue
        m = re.match(r"^([a-z])\.\s+([^:\n]+):?", piece)
        if m and len(piece) < 200:
            out.append(f"<h4>{esc(piece.split(':')[0])}</h4>")
            if ":" in piece:
                out.append(render_prose(piece.split(":", 1)[1].strip()))
            continue
        if piece.startswith("The Symbiotic Relationship"):
            out.append("<h3>The Symbiotic Relationship</h3>")
            out.append(render_prose(piece[len("The Symbiotic Relationship") :].strip()))
            continue
        out.append(render_prose(piece))
    return "".join(out)


def render_prose(text: str) -> str:
    if not text.strip():
        return ""
    # Split on sentence boundaries before known labels
    labels = [
        "Confidentiality:", "Integrity:", "Authentication:", "Non-Repudiation:",
        "How it works:", "Key Characteristics:", "Examples:", "Status:", "Architecture:",
        "Core Principle:", "Definition:", "Bypassing via Brute-Force Attacks",
        "Small Key Space (Vulnerable):", "Large Key Space (Secure):",
        "Mathematical Notation:", "Reverse Engineering:", "The Flaw of Inflexible Systems:",
        "The Strength of Public Algorithms:", "Padding Requirement:", "Cipher Modes of Operation:",
        "Vulnerabilities (The Two-Time Pad Trap):", "Exceptional Speed:", "Zero Latency:",
        "No Data Expansion:", "Deterministic:", "Pre-Image Resistance (One-Way):",
        "Second Pre-Image Resistance:", "Collision Resistance:", "Avalanche Effect:",
        "The Public Key:", "The Private Key:", "Step 1:", "Step 2:", "Step 3:",
        "Protects Routing Metadata:", "Vulnerable Intermediate Nodes:", "Layer 1/2 Scope:",
        "High Security Over Untrusted Networks:", "Metadata Exposure:", "Layer 7 Scope:",
        "The Security Flaw:", "The Identity Rule:",
    ]
    pattern = "|".join(re.escape(l) for l in labels)
    parts = re.split(rf"(?={pattern})", text)
    html_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        for lab in labels:
            if part.startswith(lab):
                if lab.endswith(":"):
                    html_parts.append(
                        f"<p><strong>{esc(lab)}</strong> {formulas_to_html(part[len(lab):].strip())}</p>"
                    )
                else:
                    html_parts.append(f"<p><strong>{esc(lab)}</strong> {formulas_to_html(part[len(lab):].strip())}</p>")
                break
        else:
            if part.endswith(":") and len(part) < 100:
                html_parts.append(f"<p><strong>{formulas_to_html(part)}</strong></p>")
            else:
                html_parts.append(f"<p>{formulas_to_html(part)}</p>")
    return "".join(html_parts)


def section_id(key: str) -> str:
    return "sec-" + key.replace(".", "-")


def build_sections() -> str:
    blocks = []
    if preamble:
        blocks.append(f'<p class="callout-intro">{formulas_to_html(preamble)}</p>')
    for key in sorted(sections, key=lambda k: float(k[2:])):
        body = sections[key]
        title = SECTION_TITLES.get(key, key)
        blocks.append(f'<section id="{section_id(key)}">')
        blocks.append(f"<h2>{esc(key)} {esc(title)}</h2>")
        blocks.append(render_body(key, body))
        if key in EXTRA_FIGURES:
            blocks.append(EXTRA_FIGURES[key])
        blocks.append("</section>")
    return "\n".join(blocks)


TOC = """
<ul>
  <li><a href="#sec-5-1">5.1 Cryptology</a></li>
  <li><a href="#sec-5-2">5.2 Goals</a></li>
  <li><a href="#sec-5-3">5.3 Lexicon</a></li>
  <li><a href="#sec-5-4">5.4 Kerckhoffs</a></li>
  <li><a href="#sec-5-5">5.5 Stream vs block</a></li>
  <li><a href="#sec-5-6">5.6 Symmetric vs asymmetric</a></li>
  <li><a href="#sec-5-7">5.7 Link vs E2EE</a></li>
  <li><a href="#sec-5-8">5.8 Key space</a></li>
  <li><a href="#sec-5-9">5.9 Steganography</a></li>
  <li><a href="#sec-5-10">5.10 Hashing</a></li>
  <li><a href="#sec-5-11">5.11 Symmetric algorithms</a></li>
  <li><a href="#sec-5-12">5.12 Asymmetric algorithms</a></li>
  <li><a href="#sec-5-13">5.13 HTTPS &amp; E2EE</a></li>
</ul>
"""

OUT = ROOT / "info-sec/topics/05-advanced-cryptography.html"
OUT.write_text(
    f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script>
    (function () {{
      try {{
        if (localStorage.getItem("infosec-notes-theme") !== "light") {{
          document.documentElement.setAttribute("data-theme", "dark");
        }}
      }} catch (e) {{
        document.documentElement.setAttribute("data-theme", "dark");
      }}
    }})();
  </script>
  <title>Topic 5 — Advanced Cryptography</title>
  <link rel="stylesheet" href="../../assets/css/notes.css">
  <script src="../../assets/js/theme.js" defer></script>
</head>
<body>
  <div class="page-wrapper has-toc-nav">
    <aside class="sidebar toc" id="sidebar-nav">
      <p class="toc-title">On this page</p>
      <nav aria-label="Table of contents">{TOC}</nav>
    </aside>
    <main class="main-content">
      <header class="site-header">
        <h1>5. Advanced Cryptography, Ciphers, and Network Implementation</h1>
        <p class="topic-meta">
          <a href="../../index.html">← All books</a>
          · <a href="../index.html">Book index</a>
          · <a href="04-security-kernel.html">Topic 4</a>
          · <span class="topic-tag sym">Sym</span>
          <span class="topic-tag asym">Asym</span>
        </p>
        <div class="header-actions">
          <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="sidebar-nav" aria-label="Open page navigation">
            <span class="nav-toggle-icon" aria-hidden="true">
              <span class="nav-toggle-bar"></span>
              <span class="nav-toggle-bar"></span>
              <span class="nav-toggle-bar"></span>
            </span>
            <span class="nav-toggle-label">Menu</span>
          </button>
          <button type="button" class="theme-toggle" aria-pressed="false">
            <span class="theme-toggle-label">Dark mode</span>
          </button>
        </div>
      </header>
      {build_sections()}
      <footer class="page-footer">
        <a href="04-security-kernel.html">← Topic 4</a>
        <a href="../index.html">Book index</a>
        <a href="../../index.html">All books</a>
        <span>Topic 6 — coming soon</span>
      </footer>
    </main>
  </div>
</body>
</html>
""",
    encoding="utf-8",
)
print("Wrote", OUT, OUT.stat().st_size, "bytes")
