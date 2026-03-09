"""Speech-shaping rules for spoken Russian replies."""

from __future__ import annotations

import re
from dataclasses import dataclass

_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_URL_PATTERN = re.compile(r"https?://\S+")
_MARKDOWN_PREFIX_PATTERN = re.compile(r"(?m)^\s{0,3}(?:[#>*-]|\d+\.)\s*")
_INLINE_MARKDOWN_PATTERN = re.compile(r"[*_`~]+")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class RussianSpeechShaper:
    """Normalize OpenClaw text into speech-friendly Russian chunks."""

    max_chunk_chars: int = 220

    def shape(self, text: str) -> list[str]:
        normalized = self._normalize(text)
        if not normalized:
            return []

        sentences = [
            part.strip()
            for part in _SENTENCE_SPLIT_PATTERN.split(normalized)
            if part.strip()
        ]
        return self._chunk(sentences)

    def _normalize(self, text: str) -> str:
        rendered = _LINK_PATTERN.sub(r"\1", text)
        rendered = _URL_PATTERN.sub("", rendered)
        rendered = rendered.replace("```", " ").replace("`", "")
        rendered = _MARKDOWN_PREFIX_PATTERN.sub("", rendered)
        rendered = _INLINE_MARKDOWN_PATTERN.sub("", rendered)
        rendered = rendered.replace("OpenClaw request error:", "OpenClaw request error.")
        rendered = rendered.replace(":", ". ")
        rendered = _WHITESPACE_PATTERN.sub(" ", rendered).strip()
        return rendered

    def _chunk(self, sentences: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            candidate = sentence if not current else f"{current} {sentence}"
            if len(candidate) <= self.max_chunk_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)
            if len(sentence) <= self.max_chunk_chars:
                current = sentence
                continue

            chunks.extend(self._split_long_sentence(sentence))
            current = ""

        if current:
            chunks.append(current)
        return chunks

    def _split_long_sentence(self, sentence: str) -> list[str]:
        words = sentence.split()
        chunks: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if len(candidate) <= self.max_chunk_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = word
        if current:
            chunks.append(current)
        return chunks
