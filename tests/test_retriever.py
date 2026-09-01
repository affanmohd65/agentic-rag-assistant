from app import retriever


def test_extract_text_reads_plain_text_file(tmp_path):
    text_file = tmp_path / "notes.txt"
    text_file.write_text("Multimodal RAG indexes more than PDFs.", encoding="utf-8")

    assert retriever.extract_text(str(text_file)) == "Multimodal RAG indexes more than PDFs."


def test_extract_text_transcribes_audio_files(monkeypatch, tmp_path):
    audio_file = tmp_path / "meeting.mp3"
    audio_file.write_bytes(b"audio")
    monkeypatch.setattr(retriever, "_transcribe_audio", lambda path: "Audio transcript")

    assert retriever.extract_text(str(audio_file)) == "Audio transcript"


def test_extract_text_describes_images(monkeypatch, tmp_path):
    image_file = tmp_path / "diagram.png"
    image_file.write_bytes(b"image")
    monkeypatch.setattr(retriever, "_describe_image", lambda path: "Architecture diagram description")

    assert retriever.extract_text(str(image_file)) == "Architecture diagram description"
