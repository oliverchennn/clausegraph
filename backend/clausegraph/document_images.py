"""Bounded local PDF rasterization for image-input evidence models; no remote files."""
import io
import math
import multiprocessing

MAX_VISION_PAGES = 4
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_IMAGE_BYTES = 2 * 1024 * 1024
RENDER_TIMEOUT_SECONDS = 20.0


def _render_worker(content: bytes, numbers: list[int] | None, connection):
    try:
        import pypdfium2 as pdfium

        with pdfium.PdfDocument(content) as pdf:
            if not 0 < len(pdf) <= 200:
                raise ValueError("Invalid page count")
            requested = numbers if numbers is not None else list(range(1, len(pdf) + 1))
            if not requested or len(requested) > MAX_VISION_PAGES or any(n < 1 or n > len(pdf) for n in requested):
                raise ValueError("Invalid requested pages")
            images = []
            for number in requested:
                page = pdf[number - 1]
                try:
                    width, height = page.get_size()
                    if any(not math.isfinite(value) or value <= 0 or value > 20000 for value in (width, height)):
                        raise ValueError("Invalid page dimensions")
                    scale = min(2, 1600 / max(width, height))
                    if min(width, height) * scale < 32:
                        raise ValueError("Page too narrow to read safely")
                    bitmap = page.render(scale=scale, rev_byteorder=True)
                    try:
                        image = bitmap.to_pil()
                        try:
                            rgb = image.convert("RGB")
                            try:
                                stream = io.BytesIO()
                                rgb.save(stream, format="JPEG", quality=85)
                                encoded = stream.getvalue()
                            finally:
                                rgb.close()
                        finally:
                            image.close()
                    finally:
                        bitmap.close()
                    if len(encoded) > MAX_IMAGE_BYTES:
                        raise ValueError("Image exceeds byte limit")
                    images.append((number, encoded))
                finally:
                    page.close()
            connection.send((True, images))
    except Exception:
        connection.send((False, "PDF images could not be rendered within safe limits. Split or simplify this document (at most 4 image pages per request)."))
    finally:
        connection.close()


def render_pdf_pages(content: bytes, numbers: list[int] | None = None) -> list[tuple[int, bytes]]:
    """Return numbered JPEGs from a killable process, capped at four 1600px pages."""
    if not content.startswith(b"%PDF-") or len(content) > MAX_PDF_BYTES:
        raise ValueError("Invalid or oversized PDF for image processing.")
    if numbers is not None:
        if not numbers or len(numbers) > MAX_VISION_PAGES or any(type(n) is not int or n < 1 for n in numbers):
            raise ValueError("Image evidence is limited to 4 source pages per request. Split this document.")
        if len(set(numbers)) != len(numbers):
            raise ValueError("Duplicate requested image pages.")
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_render_worker, args=(content, numbers, child), daemon=True)
    try:
        process.start()
        child.close()
        if not parent.poll(RENDER_TIMEOUT_SECONDS):
            raise ValueError("PDF image rendering timed out. Split or simplify this document.")
        try:
            succeeded, payload = parent.recv()
        except EOFError as exc:
            raise ValueError("PDF image rendering stopped unexpectedly.") from exc
        if not succeeded:
            raise ValueError(payload)
        return payload
    finally:
        parent.close()
        child.close()
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
            process.close()
