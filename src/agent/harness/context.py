"""Sync Ambient Analyst Context Hub files to and from ./src/context."""

import argparse
import json
import os
import shutil
from pathlib import Path

import dotenv
from langsmith import Client
from langsmith.schemas import FileEntry
from langchain_core.prompts import ChatPromptTemplate

dotenv.load_dotenv(override=True)

CONTEXT_DIR = Path(__file__).resolve().parents[2] / "context"
MANIFEST = CONTEXT_DIR / ".contexthub.json"

MEMORY_REPO = os.environ.get("AMBIENT_ANALYST_MEMORY_REPO", "ambient-analyst-memory")
PROMPT_NAME = os.environ.get("AMBIENT_ANALYST_PROMPT_NAME", "ambient-analyst-prompt")
SKILL_HANDLES = [
    h.strip()
    for h in os.environ.get(
        "AMBIENT_ANALYST_SKILLS",
        "ambient-analyst-model-evaluation,ambient-analyst-benchmark-analysis,ambient-analyst-landscape-mapping,"
        "ambient-analyst-scorecard-maintenance,ambient-analyst-continuous-learning",
    ).split(",")
    if h.strip()
]


def _prompt_root() -> Path:
    return CONTEXT_DIR / "prompt" / PROMPT_NAME


def prompt_identifier(client: Client) -> str:
    prompt = client.get_prompt(PROMPT_NAME)
    return getattr(prompt, "full_name", None) or PROMPT_NAME


def _write_prompt(client: Client) -> dict:
    root = _prompt_root()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    prompt_meta = client.get_prompt(PROMPT_NAME)
    identifier = getattr(prompt_meta, "full_name", None) or PROMPT_NAME
    prompt = client.pull_prompt(identifier, dangerously_pull_public_prompt=True)
    (root / "prompt.md").write_text(prompt.messages[0].prompt.template)
    return {
        "handle": identifier,
        "commit_hash": getattr(prompt_meta, "last_commit_hash", "latest"),
        "file": "prompt.md",
    }


def _write_repo(root: Path, context) -> dict:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    files = []
    for name, entry in context.files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(entry.content)
        files.append(name)
    return {"commit_hash": context.commit_hash, "files": sorted(files)}


def pull() -> None:
    client = Client()
    manifest = {
        "prompt": {},
        "agent": {"handle": MEMORY_REPO},
        "skills": {},
    }

    manifest["prompt"].update(_write_prompt(client))
    manifest["agent"].update(
        _write_repo(CONTEXT_DIR / "agent" / MEMORY_REPO, client.pull_agent(MEMORY_REPO))
    )
    for handle in SKILL_HANDLES:
        manifest["skills"][handle] = _write_repo(
            CONTEXT_DIR / "skills" / handle,
            client.pull_skill(handle),
        )

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def _read_files(root: Path, previous_files: list[str]) -> dict[str, FileEntry | None]:
    if not root.exists():
        raise FileNotFoundError(f"{root} does not exist; run pull first")
    current = {
        str(path.relative_to(root)): FileEntry(content=path.read_text())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    for name in previous_files:
        current.setdefault(name, None)
    return current


def push() -> None:
    client = Client()
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}

    prompt_meta = manifest.get("prompt", {})
    prompt_file = _prompt_root() / prompt_meta.get("file", "prompt.md")
    if not prompt_file.exists():
        raise FileNotFoundError(f"{prompt_file} does not exist; run pull first")
    identifier = prompt_meta.get("handle") or prompt_identifier(client)
    prompt_meta["commit_hash"] = client.push_prompt(
        identifier,
        object=ChatPromptTemplate.from_messages([("system", prompt_file.read_text())]),
        parent_commit_hash=prompt_meta.get("commit_hash", "latest"),
    )
    prompt_meta["handle"] = identifier
    prompt_meta["file"] = str(prompt_file.relative_to(_prompt_root()))
    manifest["prompt"] = prompt_meta

    agent_meta = manifest.get("agent", {})
    agent_meta["commit_hash"] = client.push_agent(
        MEMORY_REPO,
        files=_read_files(
            CONTEXT_DIR / "agent" / MEMORY_REPO,
            agent_meta.get("files", []),
        ),
        parent_commit=agent_meta.get("commit_hash"),
    )
    agent_meta["handle"] = MEMORY_REPO
    agent_meta["files"] = sorted(
        str(path.relative_to(CONTEXT_DIR / "agent" / MEMORY_REPO))
        for path in (CONTEXT_DIR / "agent" / MEMORY_REPO).rglob("*")
        if path.is_file()
    )
    manifest["agent"] = agent_meta

    skill_meta = manifest.get("skills", {})
    for handle in SKILL_HANDLES:
        meta = skill_meta.get(handle, {})
        root = CONTEXT_DIR / "skills" / handle
        meta["commit_hash"] = client.push_skill(
            handle,
            files=_read_files(root, meta.get("files", [])),
            parent_commit=meta.get("commit_hash"),
        )
        meta["files"] = sorted(
            str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()
        )
        skill_meta[handle] = meta
    manifest["skills"] = skill_meta
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pull", "push"])
    args = parser.parse_args()
    {"pull": pull, "push": push}[args.mode]()


if __name__ == "__main__":
    main()
