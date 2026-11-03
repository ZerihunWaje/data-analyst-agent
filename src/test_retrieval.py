from retriever import retrieve

questions = [
    "How many unique customers do we have?",
    "Which product categories sell the best?",
    "How often do deliveries arrive late?",
    "What is the revenue per seller?",
]

for q in questions:
    print(f"\nQ: {q}")
    for hit in retrieve(q):
        print(f"   {hit['distance']:.3f}  {hit['id']}")