from docling.document_converter import DocumentConverter

source = "Adamo Resume Jan-2026.pdf"  # file path or URL
converter = DocumentConverter()
result = converter.convert(source)
doc = result.document

print(doc.export_to_markdown())