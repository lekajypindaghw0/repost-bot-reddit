from app.services.similarity_engine import title_similarity

def test_similarity_threshold_reasonable():
    s = title_similarity("This is a test title", "This is a test title!!")
    assert s > 0.85
