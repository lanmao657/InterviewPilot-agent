import openai

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.ai_api_key)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Call OpenAI Embedding API and return vector list."""
        response = await self.client.embeddings.create(
            model=self.settings.embedding_model,
            input=texts,
            dimensions=self.settings.embedding_dimensions,
        )
        return [item.embedding for item in response.data]

    def chunk_text(
        self, text: str, chunk_size: int = 512, overlap: int = 64
    ) -> list[str]:
        """Split text into chunks by paragraph + token limit with overlap.

        Overlap is applied at paragraph and sentence boundaries to preserve
        context across chunk transitions.
        """
        # Split by paragraphs first
        paragraphs = text.split("\n\n")

        chunks: list[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If the paragraph itself exceeds chunk_size, split by sentences
            if len(paragraph) > chunk_size:
                sentences = self._split_sentences(paragraph)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    # If a single sentence exceeds chunk_size, force-split it
                    if len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        # Force-split the long sentence with overlap
                        for sub in self._force_split(sentence, chunk_size, overlap):
                            chunks.append(sub)
                        continue

                    if len(current_chunk) + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # Preserve overlap from end of current chunk
                            overlap_text = current_chunk[-overlap:] if overlap else ""
                            current_chunk = overlap_text + "\n" + sentence
                        else:
                            current_chunk = sentence
                    else:
                        current_chunk += "\n" + sentence if current_chunk else sentence
            else:
                if len(current_chunk) + len(paragraph) > chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        # Preserve overlap from end of current chunk
                        overlap_text = current_chunk[-overlap:] if overlap else ""
                        current_chunk = overlap_text + "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences by Chinese and English punctuation."""
        for sep in ["。", ".", "!", "！", "?", "？"]:
            text = text.replace(sep, sep + "\n")
        return text.split("\n")

    @staticmethod
    def _force_split(text: str, chunk_size: int, overlap: int) -> list[str]:
        """Force-split text that has no natural delimiters into chunk_size pieces."""
        result: list[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            result.append(text[start:end])
            start = end - overlap if overlap and end < len(text) else end
        return result
