import sys
import os

sys.path.insert(0, os.path.abspath("c:/Users/Sowmya Mounika/OneDrive/Desktop/New folder/echolens"))

try:
    from backend.services.data_processor import process_file_data, process_release_data
    from backend.services.analytics import compute_analytics, generate_memory_summaries
    from backend.services.hindsight import retain_feedback_memories, recall_memories
    from backend.services.groq_agent import answer_product_question
    from backend.main import app

    print("SUCCESS: All backend modules imported without errors.")

    csv_path = "c:/Users/Sowmya Mounika/OneDrive/Desktop/New folder/echolens/data/demo_feedback.csv"
    rel_path = "c:/Users/Sowmya Mounika/OneDrive/Desktop/New folder/echolens/data/demo_releases.csv"
    
    df, detected = process_file_data(csv_path)
    rel_df = process_release_data(rel_path)
    print(f"Processed dataset: {len(df)} rows. Detected columns: {detected}")

    analytics = compute_analytics(df, rel_df)
    print(f"Analytics total feedback: {analytics['total_feedback']}, Positive %: {analytics['positive_percentage']}%")

    memories = generate_memory_summaries(df, rel_df)
    print(f"Generated {len(memories)} memory summaries.")

    retained = retain_feedback_memories(memories)
    print(f"Memories retained (synced={retained}).")

    recalled = recall_memories("checkout redesign", top_k=3)
    print(f"Recalled {len(recalled)} memories for query 'checkout redesign':")
    for r in recalled:
        print(" -", r.get("text")[:100], "...")

    agent_res = answer_product_question("What changed after the checkout redesign?", recalled, analytics)
    print("Agent answer output:\n", agent_res["answer"])

    print("\nALL BACKEND SMOKE TESTS PASSED CLEANLY!")

except Exception as e:
    print(f"ERROR during smoke test: {e}")
    import traceback
    traceback.print_exc()
