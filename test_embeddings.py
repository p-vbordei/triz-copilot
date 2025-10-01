#!/usr/bin/env python3
"""Test embeddings and vector database setup."""

import sys
import json
from pathlib import Path

# Check Qdrant connection
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    
    print("Testing Qdrant connection...")
    client = QdrantClient(host="localhost", port=6333)
    
    # Get existing collections
    collections = client.get_collections()
    print(f"✓ Connected to Qdrant")
    print(f"  Existing collections: {[c.name for c in collections.collections]}")
    
    # Create a test collection if none exist
    if not collections.collections:
        print("\nCreating test collection 'triz_knowledge'...")
        client.create_collection(
            collection_name="triz_knowledge",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        print("✓ Created collection 'triz_knowledge'")
    
except Exception as e:
    print(f"✗ Qdrant error: {e}")
    sys.exit(1)

# Test Ollama embeddings
try:
    import requests
    
    print("\nTesting Ollama embeddings...")
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": "Test TRIZ principle"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        embedding = data.get("embedding", [])
        print(f"✓ Ollama embedding service working")
        print(f"  Embedding dimension: {len(embedding)}")
    else:
        print(f"✗ Ollama returned status {response.status_code}")
        
except Exception as e:
    print(f"✗ Ollama error: {e}")
    print("  Make sure Ollama is running with: ollama serve")
    print("  And model is installed: ollama pull nomic-embed-text")

# Load and embed TRIZ principles
try:
    print("\nLoading TRIZ principles...")
    principles_file = Path("src/data/triz_principles.txt")
    
    if principles_file.exists():
        with open(principles_file, 'r') as f:
            content = f.read()
            
        # Parse principles (format: ## Principle N: Name)
        principles = []
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('## Principle '):
                # Extract number and name
                parts = line.replace('## Principle ', '').split(':', 1)
                if len(parts) == 2:
                    num = parts[0].strip()
                    name = parts[1].strip()
                    
                    # Collect description lines until next principle or examples
                    desc_lines = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith('## Principle') and not lines[i].startswith('Examples:'):
                        if lines[i].strip():
                            desc_lines.append(lines[i].strip())
                        i += 1
                    
                    principles.append({
                        "number": int(num),
                        "name": name,
                        "description": ' '.join(desc_lines)
                    })
                    continue
            i += 1
        
        print(f"✓ Loaded {len(principles)} principles")
        
        # Generate embeddings for first 5 principles
        if principles and 'client' in locals():
            print("\nGenerating embeddings for first 5 principles...")
            points = []
            
            for i, principle in enumerate(principles[:5]):
                # Generate embedding
                text = f"{principle['name']}: {principle['description']}"
                response = requests.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": text}
                )
                
                if response.status_code == 200:
                    embedding = response.json()["embedding"]
                    
                    # Create point for Qdrant
                    point = PointStruct(
                        id=principle["number"],
                        vector=embedding,
                        payload={
                            "number": principle["number"],
                            "name": principle["name"],
                            "description": principle["description"],
                            "type": "principle"
                        }
                    )
                    points.append(point)
                    print(f"  ✓ Embedded principle {principle['number']}: {principle['name']}")
            
            # Upload to Qdrant
            if points:
                client.upsert(
                    collection_name="triz_knowledge",
                    points=points
                )
                print(f"\n✓ Uploaded {len(points)} principles to Qdrant")
                
                # Test search
                print("\nTesting vector search...")
                search_text = "separation"
                response = requests.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": "nomic-embed-text", "prompt": search_text}
                )
                
                if response.status_code == 200:
                    query_vector = response.json()["embedding"]
                    results = client.search(
                        collection_name="triz_knowledge",
                        query_vector=query_vector,
                        limit=3
                    )
                    
                    print(f"✓ Search for '{search_text}':")
                    for result in results:
                        print(f"  - Score {result.score:.3f}: {result.payload['name']}")
    else:
        print(f"✗ Principles file not found: {principles_file}")
        
except Exception as e:
    print(f"✗ Error processing principles: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Embedding System Status:")
print("- Qdrant: " + ("✓ Running" if 'client' in locals() else "✗ Not available"))
print("- Ollama: " + ("✓ Running" if 'embedding' in locals() else "✗ Not available"))
print("- Collections: " + (f"{len([c.name for c in collections.collections])} found" if 'collections' in locals() else "None"))
print("="*50)