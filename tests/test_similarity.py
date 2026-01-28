from app.services.similarity_engine import title_similarity, normalise_title, compare

def test_normalise_title():
    assert normalise_title("Hello, World!!") == "hello world"

def test_title_similarity_basic():
    assert title_similarity("hello world", "hello world") == 1.0
    assert title_similarity("hello world", "different") < 0.6

def test_compare_url_match():
    r = compare("a", "https://example.com/x?utm=1", "b", "https://example.com/x")
    assert r.same_url is True
