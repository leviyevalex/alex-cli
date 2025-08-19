# alex-cli

`alex-cli` is a collection of Bash and [Cyclopts](https://github.com/cyclopts/cyclopts) command-line tools written for my own personal use.  

This allows me to track my tools and iterate quickly. Furthermore, it can be installed and used globally — no more keeping random scripts in random folders.

---

## Features

- Organize multiple personal CLIs in one repo.
- Easy global installation via `pipx`.
- Editable installs allow immediate testing and iteration.

---

## Installation

### Using pipx (editable)

Clone the repository and install with pipx:

```bash
git clone https://github.com/yourusername/alex-cli.git
cd alex-cli
pipx install --editable . --suffix ""
