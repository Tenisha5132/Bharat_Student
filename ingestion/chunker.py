import re
from typing import List
from llama_index.core.schema import TextNode, Document
from llama_index.core.node_parser import SentenceSplitter

class LegalChunker:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        # Initialize SentenceSplitter with the specified token chunking and overlap
        self.splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Regex to match common legal section headers like "Article I", "Section 1.", "1.1."
        self.header_pattern = re.compile(
            r'^(?:Article\s+[IVXLCDM\d]+|Section\s+\d+|[A-Z]\.|[IVXLCDM]+\.|Part\s+[IVXLCDM\d]+)\b.*$',
            re.IGNORECASE | re.MULTILINE
        )

    def get_nodes_from_documents(self, documents: List[Document]) -> List[TextNode]:
        """
        Splits documents into nodes and preserves the active legal section header in metadata.
        """
        nodes = []
        current_header = "General"
        
        for doc in documents:
            # Step 1: Split document into chunks
            doc_nodes = self.splitter.get_nodes_from_documents([doc])
            
            for node in doc_nodes:
                # Step 2: Search for any legal headers in the current chunk
                headers_in_node = self.header_pattern.findall(node.text)
                
                # Tag node with the header it falls under
                node.metadata["legal_section"] = current_header
                
                # If there are headers in this chunk, the next chunks will fall under the latest header
                if headers_in_node:
                    current_header = headers_in_node[-1].strip()
                    
                    # Optionally, if the chunk starts with the header, it's accurately tagged.
                    # If you want to ensure the text itself contains the header context for embedding:
                    if current_header not in node.text:
                        node.text = f"[{current_header}]\n" + node.text
                else:
                    # If no new header, ensure the current header context is included in the text
                    # so the embedding model understands what legal section this text belongs to.
                    if current_header != "General" and current_header not in node.text:
                        node.text = f"[{current_header}]\n" + node.text
                        
                nodes.append(node)
                
        return nodes
