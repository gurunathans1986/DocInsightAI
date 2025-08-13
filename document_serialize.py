import json
from typing import Dict, List, Union
import PyPDF2
import fitz  # PyMuPDF - alternative library

def serialize_pdf_by_page(pdf_path: str, method: str = "pypdf2", include_metadata: bool = True) -> Dict:
	"""
	Serialize a PDF document by extracting text from each page.
    
	Args:
		pdf_path (str): Path to the PDF file
		method (str): Extraction method - "pypdf2" or "pymupdf" 
		include_metadata (bool): Whether to include PDF metadata
    
	Returns:
		Dict: Serialized PDF data with page-by-page text content
	"""
    
	if method == "pypdf2":
		return _serialize_with_pypdf2(pdf_path, include_metadata)
	elif method == "pymupdf":
		return _serialize_with_pymupdf(pdf_path, include_metadata)
	else:
		raise ValueError("Method must be 'pypdf2' or 'pymupdf'")

def _serialize_with_pypdf2(pdf_path: str, include_metadata: bool) -> Dict:
	"""Extract text using PyPDF2 library"""
    
	result = {
		"source_file": pdf_path,
		"extraction_method": "pypdf2",
		"total_pages": 0,
		"pages": [],
		"metadata": {}
	}
    
	try:
		with open(pdf_path, 'rb') as file:
			pdf_reader = PyPDF2.PdfReader(file)
			result["total_pages"] = len(pdf_reader.pages)
            
			# Extract metadata if requested
			if include_metadata and pdf_reader.metadata:
				result["metadata"] = {
					"title": pdf_reader.metadata.get('/Title', ''),
					"author": pdf_reader.metadata.get('/Author', ''),
					"subject": pdf_reader.metadata.get('/Subject', ''),
					"creator": pdf_reader.metadata.get('/Creator', ''),
					"producer": pdf_reader.metadata.get('/Producer', ''),
					"creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
					"modification_date": str(pdf_reader.metadata.get('/ModDate', ''))
				}
            
			# Extract text from each page
			for page_num, page in enumerate(pdf_reader.pages, 1):
				try:
					text = page.extract_text()
					page_data = {
						"page_number": page_num,
						"text": text.strip() if text else "",
						"character_count": len(text) if text else 0,
						"word_count": len(text.split()) if text and text.strip() else 0
					}
					result["pages"].append(page_data)
				except Exception as e:
					# Handle pages that can't be extracted
					result["pages"].append({
						"page_number": page_num,
						"text": "",
						"character_count": 0,
						"word_count": 0,
						"error": str(e)
					})
                    
	except Exception as e:
		result["error"] = f"Failed to process PDF: {str(e)}"
        
	return result

def _serialize_with_pymupdf(pdf_path: str, include_metadata: bool) -> Dict:
	"""Extract text using PyMuPDF library (often better for complex PDFs)"""
    
	result = {
		"source_file": pdf_path,
		"extraction_method": "pymupdf",
		"total_pages": 0,
		"pages": [],
		"metadata": {}
	}
    
	try:
		pdf_document = fitz.open(pdf_path)
		result["total_pages"] = len(pdf_document)
        
		# Extract metadata if requested
		if include_metadata:
			metadata = pdf_document.metadata
			result["metadata"] = {
				"title": metadata.get("title", ""),
				"author": metadata.get("author", ""),
				"subject": metadata.get("subject", ""),
				"creator": metadata.get("creator", ""),
				"producer": metadata.get("producer", ""),
				"creation_date": metadata.get("creationDate", ""),
				"modification_date": metadata.get("modDate", "")
			}
        
		# Extract text from each page
		for page_num in range(len(pdf_document)):
			try:
				page = pdf_document[page_num]
				text = page.get_text()
                
				page_data = {
					"page_number": page_num + 1,
					"text": text.strip(),
					"character_count": len(text),
					"word_count": len(text.split()) if text.strip() else 0
				}
				result["pages"].append(page_data)
                
			except Exception as e:
				result["pages"].append({
					"page_number": page_num + 1,
					"text": "",
					"character_count": 0,
					"word_count": 0,
					"error": str(e)
				})
        
		pdf_document.close()
        
	except Exception as e:
		result["error"] = f"Failed to process PDF: {str(e)}"
        
	return result

def save_serialized_pdf(pdf_data: Dict, output_path: str, format: str = "json") -> None:
	"""
	Save the serialized PDF data to a file.
    
	Args:
		pdf_data (Dict): Serialized PDF data from serialize_pdf_by_page()
		output_path (str): Path where to save the output
		format (str): Output format - "json" or "txt"
	"""
    
	if format == "json":
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(pdf_data, f, indent=2, ensure_ascii=False)
            
	elif format == "txt":
		with open(output_path, 'w', encoding='utf-8') as f:
			f.write(f"PDF: {pdf_data['source_file']}\n")
			f.write(f"Total Pages: {pdf_data['total_pages']}\n")
			f.write(f"Extraction Method: {pdf_data['extraction_method']}\n")
			f.write("=" * 50 + "\n\n")
            
			for page in pdf_data['pages']:
				f.write(f"PAGE {page['page_number']}\n")
				f.write("-" * 20 + "\n")
				f.write(f"Characters: {page['character_count']}, Words: {page['word_count']}\n")
				if 'error' in page:
					f.write(f"ERROR: {page['error']}\n")
				else:
					f.write(f"{page['text']}\n")
				f.write("\n" + "=" * 50 + "\n\n")
	else:
		raise ValueError("Format must be 'json' or 'txt'")

# Example usage

# Basic usage
pdf_data = serialize_pdf_by_page("./doc/India Halliburton Employee Handbook Manual.pdf", method="pymupdf")

# Save as JSON for LLM consumption
save_serialized_pdf(pdf_data, "serialized_pdf.json", format="json")

# Or save as readable text
save_serialized_pdf(pdf_data, "serialized_pdf.txt", format="txt")

# Print summary 
print(f"Processed {pdf_data['total_pages']} pages")
for page in pdf_data['pages']:
	print(f"Page {page['page_number']}: {page['word_count']} words")
