"""
Download a subset of real, high-quality open-source Human-LLM conversation dataset
(ShareGPT unfiltered) from Hugging Face.

Streams data incrementally to download only the requested number of conversations
without fetching the entire 600+ MB dataset file.
"""

import argparse
import json
import logging
import os
import sys
import urllib.request
from typing import Any, Dict, List, BinaryIO

DEFAULT_SHAREGPT_URL = (
    "https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered"
    "/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json"
)
DEFAULT_OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "sharegpt", "real_conversations.json")
)

logger = logging.getLogger("sharegpt_downloader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def is_valid_conversation(item: Dict[str, Any], min_turns: int = 2) -> bool:
    """
    Validate that an item contains a well-formed conversation with at least min_turns.
    """
    if not isinstance(item, dict):
        return False
    if "id" not in item or not item.get("id"):
        return False
    turns = item.get("conversations")
    if not isinstance(turns, list) or len(turns) < min_turns:
        return False
    for turn in turns:
        if not isinstance(turn, dict):
            return False
        from_role = turn.get("from")
        val = turn.get("value")
        if not from_role or not isinstance(val, str) or not val.strip():
            return False
    return True


def stream_json_conversations(
    stream: BinaryIO,
    max_count: int = 100,
    min_turns: int = 2,
    chunk_size: int = 65536,
) -> List[Dict[str, Any]]:
    """
    Stream and incrementally parse JSON objects from an array in a binary stream,
    filtering for valid, high-quality multi-turn conversations.

    Args:
        stream: Binary stream providing JSON array content.
        max_count: Maximum number of valid conversations to decode.
        min_turns: Minimum number of non-empty dialogue turns required.
        chunk_size: Number of bytes to read per iteration.

    Returns:
        List of parsed conversation dictionary objects.
    """
    decoder = json.JSONDecoder()
    items: List[Dict[str, Any]] = []
    buf = ""

    while len(items) < max_count:
        chunk = stream.read(chunk_size)
        if not chunk:
            break

        buf += chunk.decode("utf-8", errors="ignore")
        buf = buf.lstrip(" \t\r\n[")

        while len(items) < max_count:
            buf = buf.lstrip(" \t\r\n,")
            if not buf:
                break
            if buf.startswith("]"):
                # Reached end of JSON array
                return items
            try:
                obj, idx = decoder.raw_decode(buf)
                if is_valid_conversation(obj, min_turns=min_turns):
                    items.append(obj)
                else:
                    logger.debug(f"Skipping malformed or empty conversation: {obj.get('id')}")
                buf = buf[idx:]
            except json.JSONDecodeError:
                # Need more chunks from stream to complete current object
                break

    return items


def fetch_sharegpt_conversations(
    count: int = 100,
    output_path: str = DEFAULT_OUTPUT_PATH,
    url: str = DEFAULT_SHAREGPT_URL,
    min_turns: int = 2,
    chunk_size: int = 65536,
    timeout: int = 60,
) -> str:
    """
    Download real conversation samples from Hugging Face and save to JSON.

    Args:
        count: Number of conversations to retrieve.
        output_path: Target path for the output JSON file.
        url: Direct download URL for the dataset file on Hugging Face.
        min_turns: Minimum number of non-empty dialogue turns required.
        chunk_size: Streaming chunk size in bytes.
        timeout: Socket timeout in seconds.

    Returns:
        The normalized absolute output path.
    """
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Connecting to Hugging Face dataset URL: {url}")
    logger.info(f"Target count: {count} conversations (min_turns: {min_turns})")
    logger.info(f"Output destination: {output_path}")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (DataEngineer/1.0; HuggingFace Downloader)"}
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status not in (200, 206):
            raise RuntimeError(f"HTTP request failed with status code {resp.status}")

        items = stream_json_conversations(
            resp, max_count=count, min_turns=min_turns, chunk_size=chunk_size
        )

    if not items:
        raise ValueError(f"No conversation items were decoded from {url}")

    logger.info(f"Successfully decoded {len(items)} conversations from stream.")

    # Write out the parsed conversations
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path)
    total_turns = sum(len(c.get("conversations", [])) for c in items)
    logger.info(
        f"Saved {len(items)} conversations ({total_turns} total dialogue turns, "
        f"{file_size / 1024:.2f} KB) to {output_path}"
    )

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a subset of real Human-LLM conversations from Hugging Face."
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=100,
        help="Number of conversations to fetch (default: 100)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output path for JSON dataset (default: {DEFAULT_OUTPUT_PATH})"
    )
    parser.add_argument(
        "--min-turns",
        type=int,
        default=2,
        help="Minimum number of dialogue turns required per conversation (default: 2)"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_SHAREGPT_URL,
        help="Hugging Face URL for dataset JSON"
    )

    args = parser.parse_args()
    try:
        saved_path = fetch_sharegpt_conversations(
            count=args.count,
            output_path=args.output,
            url=args.url,
            min_turns=args.min_turns,
        )
        print(f"SUCCESS: Saved {args.count} conversations to {saved_path}")
    except Exception as e:
        logger.error(f"Failed to fetch dataset: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
